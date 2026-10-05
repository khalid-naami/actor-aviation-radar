"""Aviation Safety Analytics, Accident Investigation Archives & Risk Factors."""

import pandas as pd
from typing import Dict, List, Any

# Phase of Flight Accident Risk Distribution (ICAO / IATA / Boeing Statistical Summary)
PHASE_OF_FLIGHT_RISK = [
    {"Phase": "Taxi & Pushback 🚜", "Flight_Duration_Pct": 1.0, "Fatal_Accidents_Pct": 4.0, "Description": "Runway incursions, ground vehicle collisions."},
    {"Phase": "Takeoff & Initial Climb 🛫", "Flight_Duration_Pct": 2.0, "Fatal_Accidents_Pct": 14.0, "Description": "Engine loss, bird strikes, windshear (microbursts)."},
    {"Phase": "En-Route Cruise ✈️", "Flight_Duration_Pct": 84.0, "Fatal_Accidents_Pct": 11.0, "Description": "Severe Clear-Air Turbulence (CAT), high-altitude stall, depressurization."},
    {"Phase": "Descent & Initial Approach 📉", "Flight_Duration_Pct": 10.0, "Fatal_Accidents_Pct": 15.0, "Description": "Descent through icing layers, terrain navigation."},
    {"Phase": "Final Approach & Landing 🛬", "Flight_Duration_Pct": 3.0, "Fatal_Accidents_Pct": 56.0, "Description": "Crosswind excursions, low visibility, unstabilized approach, CFIT."}
]

# Primary Causal Factors in Commercial Aviation Incidents
CAUSAL_FACTORS = [
    {"Category": "Loss of Control In-Flight (LOC-I)", "Fatalities_Share_Pct": 32.0, "Primary_Mitigation": "Fly-by-wire flight envelope protection & upset recovery training."},
    {"Category": "Controlled Flight Into Terrain (CFIT)", "Fatalities_Share_Pct": 24.0, "Primary_Mitigation": "Enhanced Ground Proximity Warning Systems (EGPWS) & GPS."},
    {"Category": "Severe Weather & Microbursts / Turbulence", "Fatalities_Share_Pct": 18.0, "Primary_Mitigation": "Doppler radar, predictive windshear sensors, SATCOM real-time SIGMETs."},
    {"Category": "Runway Incursions & Excursions", "Fatalities_Share_Pct": 14.0, "Primary_Mitigation": "Engine reverse thrust automation, anti-skid carbon brakes, EMAS bed."},
    {"Category": "System / Mechanical Component Failure", "Fatalities_Share_Pct": 12.0, "Primary_Mitigation": "Triple redundancy hydraulic/electrical channels & automated EICAS monitoring."}
]

# Decadal Commercial Safety Benchmark (Fatalities per Million Commercial Flights)
SAFETY_EVOLUTION_DECADES = [
    {"Decade": "1970 - 1979", "Fatal_Accident_Rate_Per_M_Flights": 4.60, "Global_Annual_Flights_Millions": 9.5},
    {"Decade": "1980 - 1989", "Fatal_Accident_Rate_Per_M_Flights": 2.80, "Global_Annual_Flights_Millions": 14.2},
    {"Decade": "1990 - 1999", "Fatal_Accident_Rate_Per_M_Flights": 1.45, "Global_Annual_Flights_Millions": 21.0},
    {"Decade": "2000 - 2009", "Fatal_Accident_Rate_Per_M_Flights": 0.75, "Global_Annual_Flights_Millions": 28.5},
    {"Decade": "2010 - 2019", "Fatal_Accident_Rate_Per_M_Flights": 0.28, "Global_Annual_Flights_Millions": 38.9},
    {"Decade": "2020 - 2026", "Fatal_Accident_Rate_Per_M_Flights": 0.12, "Global_Annual_Flights_Millions": 41.5}
]

# Landmark Aviation Safety Case Studies & Lessons Learned
LANDMARK_CASE_STUDIES = [
    {
        "Event": "Malaysia Airlines MH17 (2014)",
        "Airspace": "Eastern Ukraine Conflict Zone (UKDV FIR)",
        "Finding": "Surface-to-Air Missile (Buk 9M38) launched in active warzone.",
        "Regulatory_Impact": "Mandatory EASA Conflict Zone Information Bulletins (CZIB) & real-time no-fly zone alerts worldwide."
    },
    {
        "Event": "Air France AF447 (2009)",
        "Airspace": "Intertropical Convergence Zone (ITCZ) Atlantic",
        "Finding": "High-altitude pitot probe ice crystal blockage causing un-annunciated autopilot disconnect and high-altitude aerodynamic stall.",
        "Regulatory_Impact": "Upgraded Thales pitot tubes, mandatory high-altitude manual stall recovery training for airline pilots."
    },
    {
        "Event": "US Airways 1549 (Miracle on the Hudson, 2009)",
        "Airspace": "New York Terminal Airspace (LGA)",
        "Finding": "Dual-engine bird strike (Canada geese) at 2,800 ft during initial climb.",
        "Regulatory_Impact": "Modernized airport avian radar tracking and turbofan blade ingestion resilience standards."
    },
    {
        "Event": "Singapore Airlines SQ321 (2024)",
        "Airspace": "Irrawaddy Basin (Myanmar / Andaman Sea)",
        "Finding": "Severe rapid Clear-Air Turbulence (CAT) over convective thunderstorm updrafts causing rapid 178-ft vertical drop.",
        "Regulatory_Impact": "Mandatory passenger seatbelt policies during all high-altitude cruise segments near convective zones."
    }
]

class AviationSafetyClient:
    """Client for Aviation Safety Analytics, Incident Causation, and Historical Trends."""

    @staticmethod
    def get_phase_risk_df() -> pd.DataFrame:
        return pd.DataFrame(PHASE_OF_FLIGHT_RISK)

    @staticmethod
    def get_causal_factors_df() -> pd.DataFrame:
        return pd.DataFrame(CAUSAL_FACTORS)

    @staticmethod
    def get_safety_evolution_df() -> pd.DataFrame:
        return pd.DataFrame(SAFETY_EVOLUTION_DECADES)

    @staticmethod
    def get_case_studies() -> List[Dict[str, Any]]:
        return LANDMARK_CASE_STUDIES
