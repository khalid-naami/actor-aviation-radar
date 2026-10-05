"""Global Airport Hubs Database, Great Circle Flight Planning, and Geodesic Geometry."""

import math
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd

AIRPORTS_DATABASE: Dict[str, Dict[str, Any]] = {
    # Morocco & North Africa
    "GMMN": {"iata": "CMN", "name": "Mohammed V International Airport", "city": "Casablanca", "country": "Morocco 🇲🇦", "lat": 33.3675, "lon": -7.5898, "elev_ft": 656, "rwy_hdg": 350, "tz": "Africa/Casablanca"},
    "GMME": {"iata": "RBA", "name": "Rabat–Salé Airport", "city": "Rabat", "country": "Morocco 🇲🇦", "lat": 34.0515, "lon": -6.7515, "elev_ft": 276, "rwy_hdg": 30, "tz": "Africa/Casablanca"},
    "GMMX": {"iata": "RAK", "name": "Marrakech Menara Airport", "city": "Marrakech", "country": "Morocco 🇲🇦", "lat": 31.6069, "lon": -8.0363, "elev_ft": 1535, "rwy_hdg": 100, "tz": "Africa/Casablanca"},
    "GMTT": {"iata": "TNG", "name": "Tangier Ibn Battouta Airport", "city": "Tangier", "country": "Morocco 🇲🇦", "lat": 35.7269, "lon": -5.9169, "elev_ft": 62, "rwy_hdg": 280, "tz": "Africa/Casablanca"},
    "DAAG": {"iata": "ALG", "name": "Houari Boumediene Airport", "city": "Algiers", "country": "Algeria 🇩🇿", "lat": 36.6910, "lon": 3.2154, "elev_ft": 82, "rwy_hdg": 50, "tz": "Africa/Algiers"},
    "DTTA": {"iata": "TUN", "name": "Tunis–Carthage International Airport", "city": "Tunis", "country": "Tunisia 🇹🇳", "lat": 36.8510, "lon": 10.2272, "elev_ft": 22, "rwy_hdg": 10, "tz": "Africa/Tunis"},
    "HECA": {"iata": "CAI", "name": "Cairo International Airport", "city": "Cairo", "country": "Egypt 🇪🇬", "lat": 30.1219, "lon": 31.4056, "elev_ft": 382, "rwy_hdg": 50, "tz": "Africa/Cairo"},

    # Middle East & Gulf
    "OMDB": {"iata": "DXB", "name": "Dubai International Airport", "city": "Dubai", "country": "UAE 🇦🇪", "lat": 25.2532, "lon": 55.3657, "elev_ft": 62, "rwy_hdg": 120, "tz": "Asia/Dubai"},
    "OMAA": {"iata": "AUH", "name": "Zayed International Airport", "city": "Abu Dhabi", "country": "UAE 🇦🇪", "lat": 24.4330, "lon": 54.6511, "elev_ft": 88, "rwy_hdg": 130, "tz": "Asia/Dubai"},
    "OTHH": {"iata": "DOH", "name": "Hamad International Airport", "city": "Doha", "country": "Qatar 🇶🇦", "lat": 25.2731, "lon": 51.6081, "elev_ft": 13, "rwy_hdg": 160, "tz": "Asia/Qatar"},
    "OERK": {"iata": "RUH", "name": "King Khalid International Airport", "city": "Riyadh", "country": "Saudi Arabia 🇸🇦", "lat": 24.9576, "lon": 46.6988, "elev_ft": 2049, "rwy_hdg": 150, "tz": "Asia/Riyadh"},
    "OEJN": {"iata": "JED", "name": "King Abdulaziz International Airport", "city": "Jeddah", "country": "Saudi Arabia 🇸🇦", "lat": 21.6796, "lon": 39.1565, "elev_ft": 48, "rwy_hdg": 160, "tz": "Asia/Riyadh"},
    "OEDF": {"iata": "DMM", "name": "King Fahd International Airport", "city": "Dammam", "country": "Saudi Arabia 🇸🇦", "lat": 26.4712, "lon": 49.7978, "elev_ft": 72, "rwy_hdg": 160, "tz": "Asia/Riyadh"},
    "OKBK": {"iata": "KWI", "name": "Kuwait International Airport", "city": "Kuwait City", "country": "Kuwait 🇰🇼", "lat": 29.2267, "lon": 47.9689, "elev_ft": 206, "rwy_hdg": 150, "tz": "Asia/Kuwait"},
    "OBBI": {"iata": "BAH", "name": "Bahrain International Airport", "city": "Manama", "country": "Bahrain 🇧🇭", "lat": 26.2708, "lon": 50.6336, "elev_ft": 6, "rwy_hdg": 120, "tz": "Asia/Bahrain"},
    "OOMS": {"iata": "MCT", "name": "Muscat International Airport", "city": "Muscat", "country": "Oman 🇴🇲", "lat": 23.5933, "lon": 58.2844, "elev_ft": 48, "rwy_hdg": 80, "tz": "Asia/Muscat"},
    "OJAI": {"iata": "AMM", "name": "Queen Alia International Airport", "city": "Amman", "country": "Jordan 🇯🇴", "lat": 31.7226, "lon": 35.9932, "elev_ft": 2395, "rwy_hdg": 80, "tz": "Asia/Amman"},
    "OLBA": {"iata": "BEY", "name": "Beirut–Rafic Hariri International Airport", "city": "Beirut", "country": "Lebanon 🇱🇧", "lat": 33.8209, "lon": 35.4884, "elev_ft": 87, "rwy_hdg": 30, "tz": "Asia/Beirut"},
    "ORBI": {"iata": "BGW", "name": "Baghdad International Airport", "city": "Baghdad", "country": "Iraq 🇮🇶", "lat": 33.2625, "lon": 44.2344, "elev_ft": 114, "rwy_hdg": 150, "tz": "Asia/Baghdad"},
    "OIIE": {"iata": "IKA", "name": "Tehran Imam Khomeini Airport", "city": "Tehran", "country": "Iran 🇮🇷", "lat": 35.4161, "lon": 51.1522, "elev_ft": 3305, "rwy_hdg": 110, "tz": "Asia/Tehran"},
    "LTFM": {"iata": "IST", "name": "Istanbul Airport", "city": "Istanbul", "country": "Turkey 🇹🇷", "lat": 41.2753, "lon": 28.7519, "elev_ft": 325, "rwy_hdg": 350, "tz": "Europe/Istanbul"},

    # Europe
    "EGLL": {"iata": "LHR", "name": "London Heathrow Airport", "city": "London", "country": "United Kingdom 🇬🇧", "lat": 51.4700, "lon": -0.4543, "elev_ft": 83, "rwy_hdg": 270, "tz": "Europe/London"},
    "LFPG": {"iata": "CDG", "name": "Paris Charles de Gaulle Airport", "city": "Paris", "country": "France 🇫🇷", "lat": 49.0097, "lon": 2.5479, "elev_ft": 392, "rwy_hdg": 260, "tz": "Europe/Paris"},
    "EDDF": {"iata": "FRA", "name": "Frankfurt Airport", "city": "Frankfurt", "country": "Germany 🇩🇪", "lat": 50.0379, "lon": 8.5622, "elev_ft": 364, "rwy_hdg": 250, "tz": "Europe/Berlin"},
    "EHAM": {"iata": "AMS", "name": "Amsterdam Airport Schiphol", "city": "Amsterdam", "country": "Netherlands 🇳🇱", "lat": 52.3105, "lon": 4.7683, "elev_ft": -11, "rwy_hdg": 180, "tz": "Europe/Amsterdam"},
    "LEMD": {"iata": "MAD", "name": "Adolfo Suárez Madrid–Barajas", "city": "Madrid", "country": "Spain 🇪🇸", "lat": 40.4839, "lon": -3.5680, "elev_ft": 1998, "rwy_hdg": 140, "tz": "Europe/Madrid"},
    "LEBL": {"iata": "BCN", "name": "Josep Tarradellas Barcelona-El Prat", "city": "Barcelona", "country": "Spain 🇪🇸", "lat": 41.2974, "lon": 2.0833, "elev_ft": 14, "rwy_hdg": 70, "tz": "Europe/Madrid"},
    "LIRF": {"iata": "FCO", "name": "Rome Fiumicino Airport", "city": "Rome", "country": "Italy 🇮🇹", "lat": 41.8003, "lon": 12.2389, "elev_ft": 15, "rwy_hdg": 160, "tz": "Europe/Rome"},
    "LSZH": {"iata": "ZRH", "name": "Zurich Airport", "city": "Zurich", "country": "Switzerland 🇨🇭", "lat": 47.4582, "lon": 8.5555, "elev_ft": 1416, "rwy_hdg": 160, "tz": "Europe/Zurich"},
    "LOWW": {"iata": "VIE", "name": "Vienna International Airport", "city": "Vienna", "country": "Austria 🇦🇹", "lat": 48.1103, "lon": 16.5697, "elev_ft": 600, "rwy_hdg": 110, "tz": "Europe/Vienna"},
    "EPWA": {"iata": "WAW", "name": "Warsaw Chopin Airport", "city": "Warsaw", "country": "Poland 🇵🇱", "lat": 52.1672, "lon": 20.9679, "elev_ft": 362, "rwy_hdg": 110, "tz": "Europe/Warsaw"},

    # North America
    "KJFK": {"iata": "JFK", "name": "John F. Kennedy International Airport", "city": "New York", "country": "United States 🇺🇸", "lat": 40.6413, "lon": -73.7781, "elev_ft": 13, "rwy_hdg": 40, "tz": "America/New_York"},
    "KLAX": {"iata": "LAX", "name": "Los Angeles International Airport", "city": "Los Angeles", "country": "United States 🇺🇸", "lat": 33.9416, "lon": -118.4085, "elev_ft": 125, "rwy_hdg": 250, "tz": "America/Los_Angeles"},
    "KORD": {"iata": "ORD", "name": "O'Hare International Airport", "city": "Chicago", "country": "United States 🇺🇸", "lat": 41.9742, "lon": -87.9073, "elev_ft": 668, "rwy_hdg": 280, "tz": "America/Chicago"},
    "KATL": {"iata": "ATL", "name": "Hartsfield–Jackson Atlanta Airport", "city": "Atlanta", "country": "United States 🇺🇸", "lat": 33.6407, "lon": -84.4277, "elev_ft": 1026, "rwy_hdg": 90, "tz": "America/New_York"},
    "CYYZ": {"iata": "YYZ", "name": "Toronto Pearson International Airport", "city": "Toronto", "country": "Canada 🇨🇦", "lat": 43.6777, "lon": -79.6248, "elev_ft": 569, "rwy_hdg": 50, "tz": "America/Toronto"},

    # Asia & Pacific
    "WSSS": {"iata": "SIN", "name": "Singapore Changi Airport", "city": "Singapore", "country": "Singapore 🇸🇬", "lat": 1.3644, "lon": 103.9915, "elev_ft": 22, "rwy_hdg": 20, "tz": "Asia/Singapore"},
    "RJTT": {"iata": "HND", "name": "Tokyo Haneda Airport", "city": "Tokyo", "country": "Japan 🇯🇵", "lat": 35.5494, "lon": 139.7798, "elev_ft": 35, "rwy_hdg": 340, "tz": "Asia/Tokyo"},
    "VHHH": {"iata": "HKG", "name": "Hong Kong International Airport", "city": "Hong Kong", "country": "Hong Kong 🇭🇰", "lat": 22.3080, "lon": 113.9185, "elev_ft": 28, "rwy_hdg": 70, "tz": "Asia/Hong_Kong"},
    "VIDP": {"iata": "DEL", "name": "Indira Gandhi International Airport", "city": "New Delhi", "country": "India 🇮🇳", "lat": 28.5562, "lon": 77.1000, "elev_ft": 777, "rwy_hdg": 100, "tz": "Asia/Kolkata"},
    "ZBAA": {"iata": "PEK", "name": "Beijing Capital International Airport", "city": "Beijing", "country": "China 🇨🇳", "lat": 40.0799, "lon": 116.6031, "elev_ft": 116, "rwy_hdg": 360, "tz": "Asia/Shanghai"},
    "YSSY": {"iata": "SYD", "name": "Sydney Kingsford Smith Airport", "city": "Sydney", "country": "Australia 🇦🇺", "lat": -33.9399, "lon": 151.1753, "elev_ft": 21, "rwy_hdg": 160, "tz": "Australia/Sydney"}
}

def get_airport_info(identifier: str) -> Optional[Dict[str, Any]]:
    """Look up airport by ICAO or IATA code."""
    ident_up = identifier.strip().upper()
    if ident_up in AIRPORTS_DATABASE:
        data = AIRPORTS_DATABASE[ident_up].copy()
        data["icao"] = ident_up
        return data
    
    for icao, info in AIRPORTS_DATABASE.items():
        if info.get("iata") == ident_up:
            res = info.copy()
            res["icao"] = icao
            return res
    return None

def search_airports(query: str) -> List[Dict[str, Any]]:
    """Search airports by city, name, country, IATA, or ICAO."""
    q = query.strip().lower()
    matches = []
    for icao, info in AIRPORTS_DATABASE.items():
        search_str = f"{icao} {info.get('iata', '')} {info.get('name', '')} {info.get('city', '')} {info.get('country', '')}".lower()
        if q in search_str:
            item = info.copy()
            item["icao"] = icao
            item["display_label"] = f"{info.get('city', '')} ({info.get('iata', icao)}) - {info.get('name', '')}"
            matches.append(item)
    return matches

def calculate_great_circle_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> Tuple[float, float]:
    """
    Calculate Great Circle distance between two points in km and Nautical Miles (NM).
    Uses Haversine formula.
    """
    R_km = 6371.0
    R_nm = 3440.065

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    dist_km = R_km * c
    dist_nm = R_nm * c
    return round(dist_km, 1), round(dist_nm, 1)

def generate_great_circle_path(lat1: float, lon1: float, lat2: float, lon2: float, num_points: int = 60) -> List[Tuple[float, float]]:
    """
    Interpolate intermediate waypoints along the Great Circle arc using spherical interpolation (SLERP).
    Returns list of (lat, lon) coordinates.
    """
    p1 = math.radians(lat1)
    l1 = math.radians(lon1)
    p2 = math.radians(lat2)
    l2 = math.radians(lon2)

    # Angular distance
    d = 2.0 * math.asin(math.sqrt(
        math.sin((p2 - p1) / 2.0)**2 +
        math.cos(p1) * math.cos(p2) * math.sin((l2 - l1) / 2.0)**2
    ))

    if d == 0:
        return [(lat1, lon1)]

    points = []
    for i in range(num_points + 1):
        f = i / float(num_points)
        A = math.sin((1.0 - f) * d) / math.sin(d)
        B = math.sin(f * d) / math.sin(d)

        x = A * math.cos(p1) * math.cos(l1) + B * math.cos(p2) * math.cos(l2)
        y = A * math.cos(p1) * math.sin(l1) + B * math.cos(p2) * math.sin(l2)
        z = A * math.sin(p1) + B * math.sin(p2)

        lat_interp = math.atan2(z, math.sqrt(x**2 + y**2))
        lon_interp = math.atan2(y, x)

        points.append((math.degrees(lat_interp), math.degrees(lon_interp)))

    return points

def estimate_flight_metrics(dist_nm: float, dist_km: float) -> Dict[str, Any]:
    """
    Estimate commercial flight metrics:
    - Cruise speed: ~460 knots (~850 km/h)
    - Takeoff / Climb / Descent fixed overhead: ~35 minutes (0.58 hours)
    - Fuel burn: ~3.5 kg / km (B777 / A350 average commercial long-haul)
    - CO2 emissions: ~3.15 kg CO2 per kg jet fuel
    """
    cruise_speed_knots = 460.0
    air_time_hours = (dist_nm / cruise_speed_knots) + 0.58
    
    hours = int(air_time_hours)
    minutes = int((air_time_hours - hours) * 60)
    
    est_fuel_tonnes = (dist_km * 3.4) / 1000.0
    est_co2_tonnes = est_fuel_tonnes * 3.16

    return {
        "flight_time_formatted": f"{hours}h {minutes:02d}m",
        "flight_time_decimal": round(air_time_hours, 2),
        "est_fuel_tonnes": round(est_fuel_tonnes, 1),
        "est_co2_tonnes": round(est_co2_tonnes, 1),
        "typical_cruise_altitude_ft": 36000 if dist_nm > 1000 else 28000
    }
