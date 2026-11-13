"""OpenSky Network ADS-B Flight Telemetry Client.

Fetches real-time commercial and private aircraft state vectors (latitude,
longitude, barometric altitude, ground speed, true track heading, vertical rate,
squawk codes, and origin countries). Includes intelligent fallback generator
if the public OpenSky anonymous rate-limit is reached.
"""

from typing import Dict, Any, List, Optional
import math
import random
import requests
import pandas as pd


# Bounding boxes: (lamin, lomin, lamax, lomax)
REGIONS: Dict[str, Optional[tuple]] = {
    "Global (All Airspace)": None,
    "North Africa & Mediterranean": (20.0, -18.0, 40.0, 35.0),
    "North Africa & Morocco": (20.0, -18.0, 38.0, 15.0),
    "Western & Central Europe": (36.0, -11.0, 62.0, 26.0),
    "Western Europe & Mediterranean": (34.0, -11.0, 58.0, 26.0),
    "Middle East & Arabian Gulf": (12.0, 32.0, 38.0, 62.0),
    "Middle East & Gulf Hubs": (12.0, 32.0, 38.0, 62.0),
    "North America": (24.0, -126.0, 52.0, -65.0),
    "North America (East Coast)": (25.0, -90.0, 48.0, -66.0),
    "East & Southeast Asia": (-10.0, 95.0, 46.0, 146.0),
    "East Asia & Japan": (18.0, 100.0, 46.0, 146.0),
}

SQUAWK_EMERGENCIES = {
    "7500": "🚨 HIJACKING (7500)",
    "7600": "📻 RADIO FAILURE (7600)",
    "7700": "⚠️ GENERAL EMERGENCY (7700)",
}


class OpenSkyClient:
    """Fetches and processes live ADS-B flight states."""

    BASE_URL = "https://opensky-network.org/api/states/all"

    def __init__(self, timeout: int = 12):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "GlobalAviationRadar/1.0 (Flight Telemetry Research)"
        })
        self.timeout = timeout

    def fetch_live_flights(self, region_name: str = "North Africa & Mediterranean", max_flights: int = 250) -> Dict[str, Any]:
        """Fetches live aircraft state vectors from OpenSky Network."""
        bbox = REGIONS.get(region_name)
        params = {}
        if bbox:
            params = {
                "lamin": bbox[0],
                "lomin": bbox[1],
                "lamax": bbox[2],
                "lomax": bbox[3],
            }

        try:
            resp = self.session.get(self.BASE_URL, params=params, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                states = data.get("states", []) or []
                if states:
                    df = self._parse_states(states, max_flights)
                    return {
                        "df": df,
                        "is_live": True,
                        "timestamp": data.get("time"),
                        "source": "OpenSky Network Live ADS-B Feed",
                    }
        except Exception:
            pass

        # Fallback if rate-limited (HTTP 429) or timeout
        df_fallback = self._generate_realistic_fallback_flights(region_name, max_flights=max_flights)
        return {
            "df": df_fallback,
            "is_live": False,
            "timestamp": None,
            "source": "Simulated High-Density ADS-B Telemetry (OpenSky Rate-Limit Fallback)",
        }

    def _parse_states(self, states: List[list], max_flights: int) -> pd.DataFrame:
        """Parses raw OpenSky state vector arrays into a clean DataFrame."""
        rows = []
        for s in states[:max_flights * 2]:
            lon = s[5]
            lat = s[6]
            if lon is None or lat is None:
                continue

            callsign = (s[1] or "").strip() or f"UNKN-{s[0][:4].upper()}"
            origin_country = s[2] or "Unknown"
            baro_alt_m = s[7] if s[7] is not None else (s[13] if s[13] is not None else 0.0)
            on_ground = bool(s[8])
            velocity_ms = s[9] if s[9] is not None else 0.0
            true_track = s[10] if s[10] is not None else 0.0
            vertical_rate_ms = s[11] if s[11] is not None else 0.0
            squawk = str(s[14]) if s[14] else "1000"

            # Convert to aviation units
            altitude_ft = max(0.0, round(baro_alt_m * 3.28084, 0))
            speed_kts = max(0.0, round(velocity_ms * 1.94384, 1))
            speed_kmh = max(0.0, round(velocity_ms * 3.6, 1))
            vrate_fpm = round(vertical_rate_ms * 196.85, 0)

            emergency_status = SQUAWK_EMERGENCIES.get(squawk, "Normal")

            # Flight phase classification
            if on_ground or altitude_ft < 200:
                phase = "On Ground / Taxi"
            elif vrate_fpm > 500:
                phase = "Climbing 🛫"
            elif vrate_fpm < -500:
                phase = "Descending 🛬"
            else:
                phase = "Cruising ✈️"

            rows.append({
                "icao24": s[0],
                "callsign": callsign,
                "origin_country": origin_country,
                "longitude": round(float(lon), 4),
                "latitude": round(float(lat), 4),
                "baro_altitude": round(max(0.0, float(baro_alt_m)), 1),
                "altitude_ft": altitude_ft,
                "velocity": round(max(0.0, float(velocity_ms)), 1),
                "speed_kts": speed_kts,
                "speed_kmh": speed_kmh,
                "true_track": round(float(true_track), 1),
                "heading_deg": round(float(true_track), 1),
                "vertical_rate_fpm": vrate_fpm,
                "on_ground": on_ground,
                "squawk": squawk,
                "emergency": emergency_status,
                "flight_phase": phase,
            })
            if len(rows) >= max_flights:
                break

        return pd.DataFrame(rows)

    def _generate_realistic_fallback_flights(self, region_name: str, max_flights: int = 150) -> pd.DataFrame:
        """Generates realistic commercial flight corridors when anonymous API is rate-limited."""
        rng = random.Random(42)
        airlines = [
            ("RAM", "Morocco", 33.36, -7.58),
            ("AFR", "France", 48.72, 2.36),
            ("BAW", "United Kingdom", 51.47, -0.45),
            ("DLH", "Germany", 50.03, 8.57),
            ("UAE", "United Arab Emirates", 25.25, 55.36),
            ("QTR", "Qatar", 25.27, 51.60),
            ("RYR", "Ireland", 41.29, 2.08),
            ("THY", "Turkey", 41.27, 28.75),
            ("IBE", "Spain", 40.49, -3.56),
            ("AAL", "United States", 40.64, -73.77),
            ("SIA", "Singapore", 1.36, 103.99),
            ("ANA", "Japan", 35.54, 139.77),
        ]

        bbox = REGIONS.get(region_name)
        matching_airlines = airlines
        if bbox:
            lamin, lomin, lamax, lomax = bbox
            filtered = [
                a for a in airlines
                if (lamin - 5.0) <= a[2] <= (lamax + 5.0) and (lomin - 5.0) <= a[3] <= (lomax + 5.0)
            ]
            if filtered:
                matching_airlines = filtered

        target_count = max(1, min(int(max_flights), 120))
        rows = []
        for i in range(target_count):
            prefix, country, base_lat, base_lon = matching_airlines[i % len(matching_airlines)]
            flight_num = rng.randint(101, 989)
            callsign = f"{prefix}{flight_num}"
            icao24 = f"{rng.randint(0x400000, 0xabcdef):06x}"

            lat = base_lat + rng.uniform(-8.5, 8.5)
            lon = base_lon + rng.uniform(-12.0, 12.0)
            if bbox:
                lat = max(bbox[0], min(bbox[2], lat))
                lon = max(bbox[1], min(bbox[3], lon))

            on_ground = rng.random() < 0.08
            if on_ground:
                alt_ft = 0.0
                spd_kts = round(rng.uniform(5, 28), 1)
                vrate = 0.0
                phase = "On Ground / Taxi"
            else:
                alt_ft = float(rng.choice([18000, 24000, 31000, 34000, 36000, 38000, 40000]))
                spd_kts = round(rng.uniform(410, 515), 1)
                vrate = float(rng.choice([-1200, -800, 0, 0, 0, 0, 900, 1500]))
                if vrate > 500:
                    phase = "Climbing 🛫"
                elif vrate < -500:
                    phase = "Descending 🛬"
                else:
                    phase = "Cruising ✈️"

            baro_alt_m = round(alt_ft / 3.28084, 1)
            velocity_ms = round(spd_kts / 1.94384, 1)
            heading_deg = round(rng.uniform(0, 359), 1)

            squawk = "7700" if i == 17 else "1000"
            emergency = SQUAWK_EMERGENCIES.get(squawk, "Normal")

            rows.append({
                "icao24": icao24,
                "callsign": callsign,
                "origin_country": country,
                "longitude": round(lon, 4),
                "latitude": round(lat, 4),
                "baro_altitude": baro_alt_m,
                "altitude_ft": alt_ft,
                "velocity": velocity_ms,
                "speed_kts": spd_kts,
                "speed_kmh": round(spd_kts * 1.852, 1),
                "true_track": heading_deg,
                "heading_deg": heading_deg,
                "vertical_rate_fpm": vrate,
                "on_ground": on_ground,
                "squawk": squawk,
                "emergency": emergency,
                "flight_phase": phase,
            })

        return pd.DataFrame(rows)

    @staticmethod
    def filter_nearby_aircraft(df: pd.DataFrame, target_lat: float, target_lon: float, radius_km: float = 250.0) -> pd.DataFrame:
        """Filters aircraft within a given Haversine distance radius (km) of a target airport."""
        if df.empty:
            return df

        def haversine(row):
            r = 6371.0
            phi1, phi2 = math.radians(target_lat), math.radians(row["latitude"])
            dphi = math.radians(row["latitude"] - target_lat)
            dlambda = math.radians(row["longitude"] - target_lon)
            a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
            return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        df_copy = df.copy()
        df_copy["distance_km"] = df_copy.apply(haversine, axis=1).round(1)
        return df_copy[df_copy["distance_km"] <= radius_km].sort_values("distance_km")
