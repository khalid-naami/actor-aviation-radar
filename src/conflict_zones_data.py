"""Global Conflict Airspaces, War Zones, No-Fly Zones, and Military Interception Risk Database."""

from typing import Dict, List, Any, Tuple
import math

CONFLICT_ZONES_DATABASE: Dict[str, Dict[str, Any]] = {
    "UKRAINE_WAR_ZONE": {
        "name": "Ukraine & Western Russia Conflict Airspace 🇺🇦🇷🇺",
        "risk_level": "Level 3: SEVERE / COMPLETE NO-FLY ZONE ⛔",
        "risk_code": 3,
        "fir_codes": ["UKBV", "UKDV", "UKFV", "UKLV", "UKOV", "URRV"],
        "reason": "Active military air combat, surface-to-air missile batteries (S-300/S-400), cruise missile barrages, and extreme GPS spoofing.",
        "advisory": "All civil aviation strictly prohibited by EASA/FAA NOTAMs. Mandatory rerouting around Ukrainian airspace.",
        "polygon": [
            [22.0, 52.5], [30.0, 53.0], [40.0, 53.5], [42.0, 48.0], [38.0, 44.5],
            [34.0, 44.0], [28.0, 45.0], [22.0, 48.0], [22.0, 52.5]
        ]
    },
    "RED_SEA_YEMEN": {
        "name": "Red Sea, Gulf of Aden & Yemen Airspace 🇾🇪🇸🇦",
        "risk_level": "Level 3: HIGH RISK / MISSILE INTERCEPTIONS ⚠️",
        "risk_code": 3,
        "fir_codes": ["OYSC", "HSSS"],
        "reason": "Anti-ship and anti-air missile launches, suicide drone interceptions, and naval air defense activity.",
        "advisory": "FAA/UK DfT warn against low-altitude transit. Many commercial carriers reroute over Saudi Arabia or Egypt.",
        "polygon": [
            [38.0, 20.0], [44.0, 18.0], [53.0, 16.5], [51.0, 12.0], [43.0, 11.5],
            [40.0, 13.0], [38.0, 17.0], [38.0, 20.0]
        ]
    },
    "LEVANT_SYRIA_IRAQ": {
        "name": "Levant, Syria & Northern Iraq Conflict Corridor 🇸🇾🇮🇶🇱🇧",
        "risk_level": "Level 2: HIGH RISK / MILITARY CROSS-TRAFFIC 🚨",
        "risk_code": 2,
        "fir_codes": ["OSTT", "ORBB", "OLBA"],
        "reason": "Air defense systems active, unannounced airstrikes, military UAV reconnaissance, and intense GPS interference.",
        "advisory": "Syrian airspace strictly avoided by international carriers. Iraq transit permitted only via designated high-altitude airways (FL320+).",
        "polygon": [
            [35.0, 37.5], [42.0, 37.5], [48.0, 36.0], [47.0, 31.0], [40.0, 31.5],
            [35.5, 33.0], [35.0, 37.5]
        ]
    },
    "IRAN_STRAIT_OF_HORMUZ": {
        "name": "Iran & Strait of Hormuz Flight Information Region 🇮🇷🇦🇪",
        "risk_level": "Level 2: ELEVATED ALERT / GPS SPOOFING 📡",
        "risk_code": 2,
        "fir_codes": ["OIIX"],
        "reason": "Frequent electronic warfare, pseudo-GPS signals causing navigation loss of integrity, and sudden airspace restrictions.",
        "advisory": "Pilots advised to verify raw inertial navigation (IRS/VOR) and avoid relying solely on GPS/GNSS near the Gulf.",
        "polygon": [
            [45.0, 39.5], [55.0, 38.0], [62.0, 36.0], [62.0, 25.0], [56.0, 25.5],
            [50.0, 29.0], [47.0, 32.0], [45.0, 39.5]
        ]
    },
    "SUDAN_CIVIL_WAR": {
        "name": "Sudan Airspace & Khartoum FIR (HSSS) 🇸🇩",
        "risk_level": "Level 3: SEVERE CONFLICT / COLLAPSED ATC ⛔",
        "risk_code": 3,
        "fir_codes": ["HSSS"],
        "reason": "Heavy civil war combat, destruction of airport radar infrastructure, loss of civil ATC, and anti-aircraft fire.",
        "advisory": "Complete closure of Khartoum FIR to commercial overflights except emergency humanitarian corridors.",
        "polygon": [
            [22.0, 22.0], [37.0, 22.0], [38.0, 18.0], [34.0, 11.0], [24.0, 9.0],
            [22.0, 15.0], [22.0, 22.0]
        ]
    },
    "SAHEL_INSURGENCY": {
        "name": "Sahel Region Airspace (Mali, Niger, Burkina Faso) 🇲🇱🇳🇪🇧🇫",
        "risk_level": "Level 2: ALTITUDE RESTRICTION (MANPADS Threat) ⚠️",
        "risk_code": 2,
        "fir_codes": ["DRRN", "GAAA"],
        "reason": "Armed insurgent groups possessing Man-Portable Air Defense Systems (MANPADS) capable of targeting low-flying aircraft.",
        "advisory": "Transit prohibited below Flight Level 260 (26,000 feet). High-altitude cruising (FL300+) required.",
        "polygon": [
            [-12.0, 24.0], [15.0, 23.0], [14.0, 12.0], [0.0, 10.0], [-10.0, 12.0],
            [-12.0, 24.0]
        ]
    },
    "TAIWAN_STRAIT": {
        "name": "Taiwan Strait & ADIZ Military Tension Zone 🇹🇼🇨🇳",
        "risk_level": "Level 1: CAUTION / MILITARY DRILLS 🛩️",
        "risk_code": 1,
        "fir_codes": ["RCAA"],
        "reason": "Frequent rapid-deployment military exercises, supersonic fighter scrambles, and high naval density.",
        "advisory": "Monitor NOTAMs for live-fire exercise coordinates and temporary airway reroutings.",
        "polygon": [
            [118.0, 26.0], [122.5, 26.0], [122.5, 21.5], [118.0, 21.5], [118.0, 26.0]
        ]
    },
    "KOREAN_DMZ": {
        "name": "Korean Demarcation Line & Northern FIR Border 🇰🇵🇰🇷",
        "risk_level": "Level 3: PERMANENT PROHIBITED AIRSPACE ⛔",
        "risk_code": 3,
        "fir_codes": ["RKRR", "ZKKP"],
        "reason": "Permanent P-518 prohibited airspace, unannounced ballistic missile launches, and hostile anti-air response.",
        "advisory": "All commercial traffic routes strictly through southern designated international airway corridors.",
        "polygon": [
            [124.0, 38.8], [130.0, 38.8], [130.0, 37.5], [124.0, 37.5], [124.0, 38.8]
        ]
    }
}

def point_in_polygon(x: float, y: float, poly: List[List[float]]) -> bool:
    """
    Ray-casting algorithm to test if (lon, lat) point is inside a polygon.
    poly: list of [lon, lat] pairs.
    """
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def check_flight_path_conflicts(path_coords: List[Tuple[float, float]]) -> List[Dict[str, Any]]:
    """
    Check if an interpolated Great Circle flight path (list of (lat, lon))
    passes through or comes within proximity of any active conflict/no-fly zones.
    """
    detected_conflicts = []
    
    for zone_id, zone_data in CONFLICT_ZONES_DATABASE.items():
        poly = zone_data["polygon"]
        intersected = False
        min_dist_to_zone = 99999.0

        for lat, lon in path_coords:
            if point_in_polygon(lon, lat, poly):
                intersected = True
                min_dist_to_zone = 0.0
                break
            else:
                # Calculate approximate distance to polygon vertices
                for v_lon, v_lat in poly:
                    d_deg = math.hypot(lat - v_lat, lon - v_lon)
                    d_km = d_deg * 111.0
                    if d_km < min_dist_to_zone:
                        min_dist_to_zone = d_km

        if intersected:
            detected_conflicts.append({
                "zone_id": zone_id,
                "name": zone_data["name"],
                "risk_level": zone_data["risk_level"],
                "risk_code": zone_data["risk_code"],
                "status": "DIRECT_INTERSECTION ⚠️",
                "reason": zone_data["reason"],
                "advisory": zone_data["advisory"],
                "min_distance_km": 0.0
            })
        elif min_dist_to_zone < 350.0:  # Within 350 km proximity
            detected_conflicts.append({
                "zone_id": zone_id,
                "name": zone_data["name"],
                "risk_level": zone_data["risk_level"],
                "risk_code": zone_data["risk_code"],
                "status": f"NEARBY_PROXIMITY ({min_dist_to_zone:.0f} km away)",
                "reason": zone_data["reason"],
                "advisory": zone_data["advisory"],
                "min_distance_km": round(min_dist_to_zone, 1)
            })

    return detected_conflicts
