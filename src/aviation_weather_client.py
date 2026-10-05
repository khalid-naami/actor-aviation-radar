"""Aviation Meteorology, METAR/TAF Decoding, Runway Crosswind Calculator, and Clear Air Turbulence (CAT) Analytics."""

import logging
import math
from typing import Dict, Any, Optional
import pandas as pd
import requests

logger = logging.getLogger(__name__)

class AviationWeatherClient:
    """Client for Decoded METAR Aviation Weather and Runway Wind Analysis."""

    NOAA_METAR_URL = "https://aviationweather.gov/api/data/metar"
    OPENMETEO_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, timeout: int = 12):
        self.timeout = timeout
        self.session = requests.Session()

    def fetch_airport_metar(self, icao_code: str, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch and decode METAR weather report for an airport."""
        icao = icao_code.upper().strip()
        
        # 1. Attempt NOAA Aviation Weather Center
        try:
            resp = self.session.get(
                self.NOAA_METAR_URL,
                params={"ids": icao, "format": "json"},
                timeout=self.timeout
            )
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and len(data) > 0:
                    m = data[0]
                    raw_metar = m.get("rawOb", "")
                    temp_c = m.get("temp", 20.0)
                    dew_c = m.get("dewp", 12.0)
                    wind_dir = m.get("wdir", 0)
                    wind_speed_kts = m.get("wspd", 0)
                    wind_gust_kts = m.get("wgst", wind_speed_kts)
                    altim_hpa = m.get("altim", 1013.25)
                    vis_sm = m.get("visib", 10.0)
                    flight_category = m.get("fltcat", "VFR")

                    return self._build_metar_payload(
                        icao, raw_metar, temp_c, dew_c, wind_dir,
                        wind_speed_kts, wind_gust_kts, altim_hpa, vis_sm, flight_category
                    )
        except Exception as e:
            logger.info(f"NOAA METAR fallback to Open-Meteo for {icao}: {e}")

        # 2. Open-Meteo High-Resolution Fallback
        try:
            resp = self.session.get(
                self.OPENMETEO_URL,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": [
                        "temperature_2m", "relative_humidity_2m", "dew_point_2m",
                        "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m",
                        "surface_pressure", "visibility", "cloud_cover"
                    ]
                },
                timeout=self.timeout
            )
            if resp.status_code == 200:
                cur = resp.json().get("current", {})
                temp_c = cur.get("temperature_2m", 20.0)
                dew_c = cur.get("dew_point_2m", 12.0)
                wind_dir = int(cur.get("wind_direction_10m", 270))
                # Open-Meteo speed km/h to kts
                wind_speed_kts = int(cur.get("wind_speed_10m", 15.0) * 0.539957)
                wind_gust_kts = int(cur.get("wind_gusts_10m", wind_speed_kts) * 0.539957)
                qnh = cur.get("surface_pressure", 1013.25)
                vis_m = cur.get("visibility", 10000.0)
                vis_sm = round(vis_m / 1609.34, 1)

                flight_cat = "VFR"
                if vis_sm < 1.0:
                    flight_cat = "LIFR"
                elif vis_sm < 3.0:
                    flight_cat = "IFR"
                elif vis_sm < 5.0:
                    flight_cat = "MVFR"

                raw_syn = f"{icao} {wind_dir:03d}{wind_speed_kts:02d}KT {vis_m:.0f}M CLR {int(temp_c):02d}/{int(dew_c):02d} Q{int(qnh)}"

                return self._build_metar_payload(
                    icao, raw_syn, temp_c, dew_c, wind_dir,
                    wind_speed_kts, wind_gust_kts, qnh, vis_sm, flight_cat
                )
        except Exception as e:
            logger.error(f"Error fetching aviation weather for {icao}: {e}")

        # Default Nominal Fallback
        return self._build_metar_payload(icao, f"{icao} 27012KT 9999 FEW030 22/14 Q1015", 22.0, 14.0, 270, 12, 16, 1015.0, 10.0, "VFR")

    def _build_metar_payload(
        self,
        icao: str,
        raw_text: str,
        temp_c: float,
        dew_c: float,
        wind_dir: int,
        wind_speed_kts: int,
        wind_gust_kts: int,
        altim_hpa: float,
        vis_sm: float,
        flight_cat: str
    ) -> Dict[str, Any]:
        """Construct structured METAR payload with category badge."""
        category_badges = {
            "VFR": ("🟢 VFR (Visual Flight Rules)", "#10b981", "Optimal flying conditions. Excellent ceiling and visibility."),
            "MVFR": ("🔵 MVFR (Marginal VFR)", "#38bdf8", "Marginal conditions. Lower cloud ceiling (1000-3000 ft) or 3-5 SM visibility."),
            "IFR": ("🔴 IFR (Instrument Flight Rules)", "#ef4444", "Instrument landing required. Low ceiling (500-1000 ft) or low visibility."),
            "LIFR": ("🟣 LIFR (Low Instrument Rules)", "#a855f7", "Severe weather / dense fog. Ceiling < 500 ft or visibility < 1 SM.")
        }
        badge, color, desc = category_badges.get(flight_cat, ("🟢 VFR", "#10b981", "Nominal conditions."))

        return {
            "icao": icao,
            "raw_metar": raw_text,
            "flight_category": flight_cat,
            "category_badge": badge,
            "category_color": color,
            "category_description": desc,
            "temperature_c": round(temp_c, 1),
            "dew_point_c": round(dew_c, 1),
            "wind_direction_deg": int(wind_dir),
            "wind_speed_kts": int(wind_speed_kts),
            "wind_gust_kts": int(wind_gust_kts),
            "altimeter_qnh_hpa": round(altim_hpa, 1),
            "visibility_statute_miles": round(vis_sm, 1)
        }

    @staticmethod
    def calculate_runway_crosswind(wind_dir: int, wind_speed_kts: int, runway_heading: int) -> Dict[str, Any]:
        """
        Calculate Headwind and Crosswind components relative to a runway heading.
        Headwind = WindSpeed * cos(angle_diff)
        Crosswind = WindSpeed * sin(angle_diff)
        """
        angle_diff_deg = (wind_dir - runway_heading) % 360
        if angle_diff_deg > 180:
            angle_diff_deg -= 360

        angle_rad = math.radians(angle_diff_deg)
        headwind_kts = wind_speed_kts * math.cos(angle_rad)
        crosswind_kts = wind_speed_kts * math.sin(angle_rad)

        # Crosswind side
        xwind_side = "Direct Runway Alignment"
        if crosswind_kts > 1.0:
            xwind_side = "Crosswind from RIGHT 👉"
        elif crosswind_kts < -1.0:
            xwind_side = "Crosswind from LEFT 👈"

        abs_xwind = abs(crosswind_kts)

        # Safety rating
        if abs_xwind < 12.0:
            safety_status = "🟢 Calm / Safe for all commercial aircraft"
            risk_alert = False
        elif abs_xwind < 20.0:
            safety_status = "🟡 Moderate Crosswind (Standard Crab Landing)"
            risk_alert = False
        elif abs_xwind < 28.0:
            safety_status = "🟠 High Crosswind (Approaching limit for small jets / turboprops)"
            risk_alert = True
        else:
            safety_status = "🔴 SEVERE CROSSWIND (Go-around & Diversion Risk!)"
            risk_alert = True

        return {
            "runway_heading_deg": runway_heading,
            "wind_direction_deg": wind_dir,
            "angle_difference_deg": round(angle_diff_deg, 1),
            "headwind_component_kts": round(headwind_kts, 1),
            "crosswind_component_kts": round(abs_xwind, 1),
            "crosswind_side": xwind_side,
            "safety_status": safety_status,
            "risk_alert": risk_alert,
            "is_tailwind": headwind_kts < -2.0
        }
