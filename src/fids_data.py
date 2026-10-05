"""Airport Flight Information Display System (FIDS) - Real-time Departures & Arrivals Engine."""

import random
import datetime
from typing import Dict, List, Any
import pandas as pd

AIRLINE_FLEET = [
    {"code": "AT", "name": "Royal Air Maroc", "callsign": "RAM"},
    {"code": "EK", "name": "Emirates", "callsign": "UAE"},
    {"code": "SV", "name": "Saudia", "callsign": "SVA"},
    {"code": "QR", "name": "Qatar Airways", "callsign": "QTR"},
    {"code": "AF", "name": "Air France", "callsign": "AFR"},
    {"code": "BA", "name": "British Airways", "callsign": "BAW"},
    {"code": "LH", "name": "Lufthansa", "callsign": "DLH"},
    {"code": "TK", "name": "Turkish Airlines", "callsign": "THY"},
    {"code": "MS", "name": "EgyptAir", "callsign": "MSR"},
    {"code": "AA", "name": "American Airlines", "callsign": "AAL"},
    {"code": "SQ", "name": "Singapore Airlines", "callsign": "SIA"},
    {"code": "EY", "name": "Etihad Airways", "callsign": "ETD"},
    {"code": "IB", "name": "Iberia", "callsign": "IBE"}
]

DESTINATION_CITIES = [
    ("Dubai", "DXB", "United Arab Emirates"),
    ("Paris", "CDG", "France"),
    ("London", "LHR", "United Kingdom"),
    ("Riyadh", "RUH", "Saudi Arabia"),
    ("Jeddah", "JED", "Saudi Arabia"),
    ("Istanbul", "IST", "Turkey"),
    ("New York", "JFK", "United States"),
    ("Doha", "DOH", "Qatar"),
    ("Madrid", "MAD", "Spain"),
    ("Frankfurt", "FRA", "Germany"),
    ("Casablanca", "CMN", "Morocco"),
    ("Cairo", "CAI", "Egypt"),
    ("Rome", "FCO", "Italy"),
    ("Singapore", "SIN", "Singapore"),
    ("Amsterdam", "AMS", "Netherlands")
]

class FIDSManager:
    """Generates realistic live airport FIDS departure and arrival boards."""

    @staticmethod
    def generate_fids_boards(airport_iata: str, airport_city: str) -> Dict[str, pd.DataFrame]:
        """Generate synchronized Departure and Arrival boards for the target airport."""
        now = datetime.datetime.now()
        
        # Consistent seed per 5 minutes for stable display
        seed_val = int(now.timestamp() / 300) + sum(ord(c) for c in airport_iata)
        rng = random.Random(seed_val)

        # 1. Departures Board
        departures = []
        for i in range(16):
            airline = rng.choice(AIRLINE_FLEET)
            flight_num = f"{airline['code']} {rng.randint(101, 989)}"
            
            dest_city, dest_iata, dest_country = rng.choice(DESTINATION_CITIES)
            while dest_iata == airport_iata:
                dest_city, dest_iata, dest_country = rng.choice(DESTINATION_CITIES)

            sched_time = now + datetime.timedelta(minutes=i * 18 - 40)
            status_roll = rng.random()
            
            terminal = f"T{rng.choice(['1', '2', '3'])}"
            gate = f"{rng.choice(['A', 'B', 'C', 'D'])}{rng.randint(1, 28):02d}"

            if i < 2:
                status = "Departed 🛫"
                est_time = sched_time.strftime("%H:%M")
            elif i < 5:
                status = "Boarding 🟢"
                est_time = sched_time.strftime("%H:%M")
            elif i < 8:
                status = "Gate Open 🚶"
                est_time = sched_time.strftime("%H:%M")
            elif status_roll < 0.20:
                delay_min = rng.choice([25, 40, 60, 90])
                delayed_time = sched_time + datetime.timedelta(minutes=delay_min)
                status = f"Delayed +{delay_min}m ⚠️"
                est_time = delayed_time.strftime("%H:%M")
            else:
                status = "On Time 🟢"
                est_time = sched_time.strftime("%H:%M")

            departures.append({
                "Time": sched_time.strftime("%H:%M"),
                "Estimated": est_time,
                "Flight": flight_num,
                "Airline": airline["name"],
                "Destination": f"{dest_city} ({dest_iata})",
                "Terminal": terminal,
                "Gate": gate,
                "Status": status
            })

        # 2. Arrivals Board
        arrivals = []
        for i in range(16):
            airline = rng.choice(AIRLINE_FLEET)
            flight_num = f"{airline['code']} {rng.randint(101, 989)}"
            
            orig_city, orig_iata, orig_country = rng.choice(DESTINATION_CITIES)
            while orig_iata == airport_iata:
                orig_city, orig_iata, orig_country = rng.choice(DESTINATION_CITIES)

            sched_time = now + datetime.timedelta(minutes=i * 16 - 35)
            status_roll = rng.random()
            
            terminal = f"T{rng.choice(['1', '2', '3'])}"
            belt = f"Belt {rng.randint(1, 9)}"

            if i < 3:
                status = "Landed / Baggage 🛄"
                est_time = sched_time.strftime("%H:%M")
            elif i < 6:
                status = "Final Approach 🛬"
                est_time = sched_time.strftime("%H:%M")
            elif status_roll < 0.18:
                delay_min = rng.choice([20, 35, 50])
                delayed_time = sched_time + datetime.timedelta(minutes=delay_min)
                status = f"Delayed +{delay_min}m ⚠️"
                est_time = delayed_time.strftime("%H:%M")
            else:
                status = "En Route / On Time 🟢"
                est_time = sched_time.strftime("%H:%M")

            arrivals.append({
                "Time": sched_time.strftime("%H:%M"),
                "Estimated": est_time,
                "Flight": flight_num,
                "Airline": airline["name"],
                "Origin": f"{orig_city} ({orig_iata})",
                "Terminal": terminal,
                "Baggage Belt": belt,
                "Status": status
            })

        return {
            "departures_df": pd.DataFrame(departures),
            "arrivals_df": pd.DataFrame(arrivals)
        }
