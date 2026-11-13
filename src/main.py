"""Apify Actor Entrypoint: Global Aviation Radar & Airport FIDS Intelligence."""

import asyncio
import math
import os
import sys
from typing import Any, Dict, List

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apify import Actor
from src.opensky_client import OpenSkyClient
from src.aviation_weather_client import AviationWeatherClient
from src.fids_data import FIDSGenerator
from src.airports_data import AIRPORTS_DATABASE
from src.conflict_zones_data import CONFLICT_ZONES_DATABASE, point_in_polygon
from src.airport_passenger_guide import AirportPassengerGuide
from src.aviation_safety_client import AviationSafetyClient
from src.visa_intelligence_data import VisaIntelligenceEngine


def sanitize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively strips None, NaN, and Infinity values for clean JSON schema validation."""
    cleaned: Dict[str, Any] = {}
    for k, v in record.items():
        if v is None:
            continue
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            continue
        if isinstance(v, dict):
            cleaned[k] = sanitize_record(v)
        elif isinstance(v, list):
            cleaned_list = []
            for item in v:
                if isinstance(item, dict):
                    cleaned_list.append(sanitize_record(item))
                elif item is not None and not (isinstance(item, float) and (math.isnan(item) or math.isinf(item))):
                    cleaned_list.append(item)
            cleaned[k] = cleaned_list
        else:
            cleaned[k] = v
    return cleaned


def evaluate_conflict_risk(lat: Any, lon: Any, include_conflicts: bool) -> str:
    """Checks whether an aircraft coordinate lies inside an active conflict NOTAM zone."""
    if not include_conflicts or lat is None or lon is None:
        return "NONE"
    try:
        lat_f = float(lat)
        lon_f = float(lon)
    except (TypeError, ValueError):
        return "NONE"
    for cz in CONFLICT_ZONES_DATABASE:
        poly = cz.get("polygon", [])
        if poly and point_in_polygon(lat_f, lon_f, poly):
            return f"{cz.get('risk_level', 'HIGH')} ({cz.get('zone_name', 'Conflict Zone')})"
    return "NONE"


async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() or {}
        region = actor_input.get("region", "North Africa & Morocco")
        airport_input = actor_input.get("airportIcao", "GMMN (Casablanca Mohammed V - Morocco)")
        max_flights = int(actor_input.get("maxFlights", 150))
        include_fids = bool(actor_input.get("includeFids", True))
        include_conflicts = bool(actor_input.get("includeConflictZones", True))
        api_key = actor_input.get("apiKey") or os.getenv("APIFY_TOKEN") or os.getenv("API_KEY", "")

        # Extract 4-letter ICAO code
        icao_code = airport_input.split(" ")[0].strip().upper()
        airport_info = AIRPORTS_DATABASE.get(icao_code, list(AIRPORTS_DATABASE.values())[0])

        Actor.log.info(f"Initializing Aviation Radar for Region: '{region}' | Airport: {icao_code}")
        if api_key:
            Actor.log.info("API Key / Token authentication provided.")

        opensky = OpenSkyClient()
        wx_client = AviationWeatherClient()

        # 1. Fetch Live ADS-B Flights
        Actor.log.info("Fetching live ADS-B flight state vectors from OpenSky Network...")
        flights_res = opensky.fetch_live_flights(region_name=region, max_flights=max_flights)
        flights_df = flights_res.get("df")
        flights_list = flights_df.to_dict(orient="records") if flights_df is not None and not flights_df.empty else []

        # 2. Fetch Airport METAR Weather + Runway Crosswind
        Actor.log.info(f"Fetching aviation METAR telemetry for {icao_code}...")
        metar_data = wx_client.fetch_airport_metar(
            icao=icao_code,
            lat=airport_info["lat"],
            lon=airport_info["lon"]
        )
        runway_crosswind = wx_client.calculate_runway_crosswind(
            wind_dir_deg=float(metar_data.get("wind_dir_deg", 0)),
            wind_speed_kts=float(metar_data.get("wind_speed_kts", 0)),
            runway_heading_deg=float(airport_info.get("primary_runway_deg", 350))
        )

        # 3. Generate FIDS Board (Departures & Arrivals) + Passenger Terminal Guide
        fids_departures: List[Dict[str, Any]] = []
        fids_arrivals: List[Dict[str, Any]] = []
        if include_fids:
            Actor.log.info(f"Generating FIDS Departure & Arrival schedule for {icao_code}...")
            dep_df = FIDSGenerator.generate_fids_board(icao_code, mode="Departures")
            arr_df = FIDSGenerator.generate_fids_board(icao_code, mode="Arrivals")
            fids_departures = dep_df.to_dict(orient="records") if not dep_df.empty else []
            fids_arrivals = arr_df.to_dict(orient="records") if not arr_df.empty else []

        passenger_guide = AirportPassengerGuide.get_terminal_guide(icao_code)

        # 4. Push Flight Records to Apify Dataset
        dataset_records: List[Dict[str, Any]] = []
        conflicts_detected = 0
        for flight in flights_list[:max_flights]:
            conflict_risk = evaluate_conflict_risk(
                flight.get("latitude"),
                flight.get("longitude"),
                include_conflicts=include_conflicts
            )
            if conflict_risk != "NONE":
                conflicts_detected += 1

            flight_record = {
                "record_type": "live_flight",
                "callsign": flight.get("callsign"),
                "icao24": flight.get("icao24"),
                "origin_country": flight.get("origin_country"),
                "latitude": flight.get("latitude"),
                "longitude": flight.get("longitude"),
                "baro_altitude_m": flight.get("baro_altitude"),
                "altitude_ft": flight.get("altitude_ft"),
                "velocity_ms": flight.get("velocity"),
                "speed_kts": flight.get("speed_kts"),
                "speed_kmh": flight.get("speed_kmh"),
                "true_track_deg": flight.get("true_track"),
                "heading_deg": flight.get("heading_deg"),
                "vertical_rate_fpm": flight.get("vertical_rate_fpm"),
                "on_ground": flight.get("on_ground"),
                "squawk": flight.get("squawk"),
                "emergency": flight.get("emergency"),
                "flight_phase": flight.get("flight_phase"),
                "conflict_zone_risk": conflict_risk,
            }
            dataset_records.append(sanitize_record(flight_record))

        # Also push the Airport Intelligence & METAR record
        airport_record = {
            "record_type": "airport_metar_fids",
            "airport_icao": icao_code,
            "airport": airport_info,
            "metar": metar_data,
            "runway_crosswind": runway_crosswind,
            "passenger_guide": passenger_guide,
            "fids_departures": fids_departures[:15],
            "fids_arrivals": fids_arrivals[:15],
        }
        dataset_records.append(sanitize_record(airport_record))

        # Push Conflict Zone Advisory records if enabled
        if include_conflicts:
            for cz in CONFLICT_ZONES_DATABASE:
                cz_record = {
                    "record_type": "conflict_zone_advisory",
                    "zone_name": cz.get("zone_name"),
                    "risk_level": cz.get("risk_level"),
                    "countries_affected": cz.get("countries_affected", []),
                    "issuing_authority": cz.get("issuing_authority"),
                    "altitude_restriction": cz.get("altitude_restriction"),
                    "advisory_summary": cz.get("advisory_summary"),
                    "conflict_zone_risk": cz.get("risk_level"),
                }
                dataset_records.append(sanitize_record(cz_record))

        if dataset_records:
            await Actor.push_data(dataset_records)
            Actor.log.info(f"Pushed {len(dataset_records)} aviation records to Apify Dataset.")

        # 5. Save Executive Summary to Key-Value Store (OUTPUT)
        safety_df = AviationSafetyClient.get_recent_incidents()
        visa_df = VisaIntelligenceEngine.get_destinations_df()
        summary_payload = {
            "region": region,
            "airportIcao": icao_code,
            "totalFlightsTracked": len(flights_list[:max_flights]),
            "flightsInConflictAirspace": conflicts_detected,
            "dataSource": flights_res.get("source", "OpenSky Network"),
            "airportMetarSummary": {
                "station": metar_data.get("icao", icao_code),
                "icao": metar_data.get("icao", icao_code),
                "flightRules": metar_data.get("flight_category", "VFR"),
                "tempC": metar_data.get("temperature_c"),
                "windSpeedKts": metar_data.get("wind_speed_kts"),
                "visibilityKm": metar_data.get("visibility_km"),
                "rawMetar": metar_data.get("raw_metar"),
                "runwayCrosswindStatus": runway_crosswind.get("status"),
            },
            "fidsSummary": {
                "departuresCount": len(fids_departures),
                "arrivalsCount": len(fids_arrivals),
            },
            "activeConflictZonesCount": len(CONFLICT_ZONES_DATABASE) if include_conflicts else 0,
            "recentSafetyBulletinsCount": len(safety_df),
            "visaFreeDestinationsTracked": len(visa_df),
        }
        await Actor.set_value("OUTPUT", sanitize_record(summary_payload))
        if not dataset_records:
            await Actor.fail(status_message="No aviation radar records were produced.")
            return
        Actor.log.info("Saved summary report to Key-Value Store 'OUTPUT'.")


if __name__ == "__main__":
    asyncio.run(main())
