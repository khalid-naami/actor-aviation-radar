"""Main execution entrypoint for Global Aviation Radar Apify Actor."""

import asyncio
import os
from typing import Dict, Any, List
from apify import Actor

from src.opensky_client import OpenSkyClient, REGIONS
from src.conflict_zones_data import CONFLICT_ZONES_DATABASE
from src.fids_data import FIDSManager
from src.airports_data import get_airport_info, AIRPORTS_DATABASE
from src.aviation_weather_client import AviationWeatherClient

async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() or {}
        region_name: str = actor_input.get("region", "Western Europe & Mediterranean")
        max_flights: int = int(actor_input.get("maxFlights", 100))
        search_callsign: str = actor_input.get("searchCallsign", "").strip().upper()
        target_icao: str = actor_input.get("airportIcaoForFids", "GMMN").strip().upper()
        include_conflicts: bool = bool(actor_input.get("includeConflictZones", True))
        include_weather: bool = bool(actor_input.get("includeMetarWeather", True))
        api_key: str = actor_input.get("apiKey") or os.getenv("APIFY_TOKEN") or os.getenv("API_KEY", "")

        opensky = OpenSkyClient()
        weather_client = AviationWeatherClient()

        Actor.log.info(f"Scanning ADS-B flight transponders in region: {region_name}...")
        if api_key:
            Actor.log.info("API Key / Token authentication provided.")

        flights_df = opensky.fetch_live_flights(region_name=region_name, max_flights=max_flights)

        if search_callsign and not flights_df.empty:
            flights_df = flights_df[flights_df["callsign"].str.contains(search_callsign, na=False)]

        flight_records = flights_df.to_dict(orient="records") if not flights_df.empty else []
        Actor.log.info(f"Extracted {len(flight_records)} live transponders.")

        # Emergency transponders check (Squawk 7700 / 7600 / 7500)
        emergencies = [f for f in flight_records if str(f.get("squawk")) in ["7700", "7600", "7500"]]
        if emergencies:
            Actor.log.warning(f"Detected {len(emergencies)} active emergency squawks!")

        # Conflict Zones
        conflicts_list = []
        if include_conflicts:
            conflicts_list = list(CONFLICT_ZONES_DATABASE.values())

        # Airport FIDS Timetables
        fids_departures = FIDSManager.generate_fids_departures(target_icao)
        fids_arrivals = FIDSManager.generate_fids_arrivals(target_icao)
        airport_details = get_airport_info(target_icao)

        # Aerodrome METAR Weather
        metar_data = {}
        if include_weather and airport_details:
            try:
                metar_data = weather_client.fetch_airport_metar(
                    target_icao,
                    airport_details["lat"],
                    airport_details["lon"]
                )
            except Exception as e:
                Actor.log.warning(f"Could not fetch METAR: {e}")

        # Push full flight items to dataset
        dataset_items = []
        for flight in flight_records:
            item = {
                "type": "live_flight",
                "callsign": flight.get("callsign"),
                "icao24": flight.get("icao24"),
                "country": flight.get("origin_country"),
                "origin_country": flight.get("origin_country"),
                "latitude": flight.get("latitude"),
                "longitude": flight.get("longitude"),
                "altitude_m": flight.get("baro_altitude"),
                "baro_altitude_m": flight.get("baro_altitude"),
                "velocity_ms": flight.get("velocity"),
                "true_track": flight.get("true_track"),
                "squawk": str(flight.get("squawk")) if flight.get("squawk") is not None else None
            }
            dataset_items.append(item)

        # Also push airport FIDS board to dataset
        if airport_details:
            dataset_items.append({
                "type": "airport_fids_board",
                "airport": airport_details,
                "metar": metar_data,
                "departures_count": len(fids_departures),
                "arrivals_count": len(fids_arrivals)
            })

        if dataset_items:
            try:
                await Actor.push_data(dataset_items)
            except Exception as push_err:
                Actor.log.warning(f"Initial dataset push_data encountered validation issue: {push_err}. Retrying sanitized payload...")
                sanitized = [{k: v for k, v in itm.items() if v is not None} for itm in dataset_items]
                await Actor.push_data(sanitized)

        # Save executive summary in Key-Value store for Apify MCP & instant API tools
        summary_payload = {
            "region": region_name,
            "totalTrackedAircraft": len(flight_records),
            "emergencyTranspondersCount": len(emergencies),
            "emergencyFlights": emergencies,
            "activeConflictZonesCount": len(conflicts_list),
            "targetAirport": airport_details.get("name") if airport_details else target_icao,
            "airportMetarSummary": {
                "station": metar_data.get("station", target_icao),
                "flightRules": metar_data.get("flight_rules", "VFR"),
                "temperature": metar_data.get("temp_c")
            },
            "topFlightsSample": [
                {
                    "callsign": f.get("callsign"),
                    "country": f.get("origin_country"),
                    "altitude_m": f.get("baro_altitude"),
                    "velocity_ms": f.get("velocity")
                }
                for f in flight_records[:10]
            ]
        }
        await Actor.set_value("OUTPUT", summary_payload)
        Actor.log.info(f"Pushed {len(dataset_items)} items to dataset and stored summary OUTPUT in Key-Value store.")

if __name__ == "__main__":
    asyncio.run(main())
