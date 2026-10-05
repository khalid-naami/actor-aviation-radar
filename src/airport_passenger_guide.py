"""Passenger Airport Operations, Security Wait Time Estimator, Baggage Rules & Delay Probability Engine."""

from typing import Dict, Any

class AirportPassengerGuide:
    """Airport procedural times, baggage standards, and weather-driven delay predictor."""

    @staticmethod
    def estimate_airport_timings(flight_type: str = "International") -> Dict[str, Any]:
        """Calculate recommended arrival timings and step-by-step terminal queue estimates."""
        is_intl = (flight_type == "International")
        
        checkin_wait = 25 if is_intl else 15
        security_wait = 18 if is_intl else 12
        immigration_wait = 20 if is_intl else 0
        gate_walk_time = 15
        boarding_buffer = 40 if is_intl else 25

        total_process_min = checkin_wait + security_wait + immigration_wait + gate_walk_time + boarding_buffer
        rec_arrival_hrs = 3.0 if is_intl else 2.0

        return {
            "flight_type": flight_type,
            "recommended_arrival_hours": rec_arrival_hrs,
            "recommended_arrival_text": f"{rec_arrival_hrs:.1f} Hours before scheduled departure",
            "checkin_wait_min": checkin_wait,
            "security_wait_min": security_wait,
            "immigration_wait_min": immigration_wait,
            "gate_walk_min": gate_walk_time,
            "boarding_close_min": 20,
            "total_estimated_process_min": total_process_min
        }

    @staticmethod
    def predict_flight_delay_probability(
        wind_speed_kts: float,
        crosswind_kts: float,
        visibility_sm: float,
        flight_cat: str
    ) -> Dict[str, Any]:
        """
        Calculate statistical flight delay probability based on surface meteorological conditions and visibility.
        """
        base_prob = 12.0  # standard baseline delay rate in normal commercial aviation

        # Visibility penalties
        if visibility_sm < 1.0 or flight_cat == "LIFR":
            base_prob += 55.0
        elif visibility_sm < 3.0 or flight_cat == "IFR":
            base_prob += 35.0
        elif visibility_sm < 5.0 or flight_cat == "MVFR":
            base_prob += 18.0

        # Crosswind / Wind penalties
        if crosswind_kts > 28.0:
            base_prob += 45.0
        elif crosswind_kts > 20.0:
            base_prob += 22.0
        elif crosswind_kts > 14.0:
            base_prob += 10.0

        if wind_speed_kts > 35.0:
            base_prob += 20.0

        prob = min(95.0, round(base_prob, 1))

        if prob < 25.0:
            status = "Low Delay Risk 🟢 (On-Time Departure Expected)"
            color = "#10b981"
        elif prob < 55.0:
            status = "Moderate Delay Risk 🟡 (Minor Air Traffic Sequencing Holds)"
            color = "#f59e0b"
        else:
            status = "High Delay / Holding Risk 🔴 (Weather Flow Control Active)"
            color = "#ef4444"

        return {
            "delay_probability_pct": prob,
            "risk_status": status,
            "status_color": color
        }
