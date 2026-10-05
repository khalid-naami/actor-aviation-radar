"""Global Visa Requirements, Passport Mobility Index, and Entry Fees Intelligence Engine."""

from typing import Dict, List, Any, Optional

COUNTRIES_LIST = [
    "Morocco 🇲🇦", "Saudi Arabia 🇸🇦", "United Arab Emirates 🇦🇪", "Qatar 🇶🇦",
    "Egypt 🇪🇬", "United Kingdom 🇬🇧", "France / Schengen Area 🇫🇷🇪🇺", "United States 🇺🇸",
    "Canada 🇨🇦", "Turkey 🇹🇷", "Japan 🇯🇵", "Singapore 🇸🇬", "China 🇨🇳", "Australia 🇦🇺"
]

# Structured Visa Rules Matrix [Origin][Destination]
VISA_RULES_MATRIX: Dict[str, Dict[str, Dict[str, Any]]] = {
    "Morocco 🇲🇦": {
        "Turkey 🇹🇷": {"status": "Visa-Free 🟢", "stay": "90 Days", "fee_usd": "$0 (Free)", "time": "Instant (At Border)", "category": "visa_free"},
        "United Arab Emirates 🇦🇪": {"status": "eVisa Required 💻", "stay": "30 / 60 Days", "fee_usd": "$85 - $150", "time": "24 - 48 Hours", "category": "evisa"},
        "Saudi Arabia 🇸🇦": {"status": "eVisa / Umrah Tourist Visa 💻", "stay": "90 Days (Multiple Entry)", "fee_usd": "$125 (Includes Insurance)", "time": "2 - 24 Hours", "category": "evisa"},
        "Qatar 🇶🇦": {"status": "Visa on Arrival / Hayya 🛬", "stay": "30 Days", "fee_usd": "$0 (Free with Hotel / Hayya)", "time": "Instant on Arrival", "category": "voa"},
        "Egypt 🇪🇬": {"status": "Visa on Arrival / eVisa 🛬", "stay": "30 Days", "fee_usd": "$25", "time": "Instant / 3 Days online", "category": "voa"},
        "United Kingdom 🇬🇧": {"status": "Standard Visitor Visa (Embassy) 🏛️", "stay": "6 Months", "fee_usd": "£115 (~$145)", "time": "3 - 4 Weeks", "category": "embassy"},
        "France / Schengen Area 🇫🇷🇪🇺": {"status": "Schengen Short-Stay Visa (Type C) 🏛️", "stay": "90 Days within 180 Days", "fee_usd": "€90 (~$98)", "time": "15 - 30 Days", "category": "embassy"},
        "United States 🇺🇸": {"status": "B1/B2 Tourist Visa (Embassy) 🏛️", "stay": "Up to 6 Months per entry", "fee_usd": "$185", "time": "Appointment Wait + 2 Weeks", "category": "embassy"},
        "Singapore 🇸🇬": {"status": "eVisa / SG Arrival Card 💻", "stay": "30 Days", "fee_usd": "$0 (Free Entry Card)", "time": "Instant (Submit 3 days prior)", "category": "evisa"},
        "Japan 🇯🇵": {"status": "eVisa for Tourism 💻", "stay": "90 Days", "fee_usd": "$25 (3,000 JPY)", "time": "5 Business Days", "category": "evisa"}
    },
    "Saudi Arabia 🇸🇦": {
        "United Arab Emirates 🇦🇪": {"status": "GCC Freedom of Movement 🟢", "stay": "Unlimited (GCC National ID)", "fee_usd": "$0 (Free)", "time": "Instant", "category": "visa_free"},
        "Qatar 🇶🇦": {"status": "GCC Freedom of Movement 🟢", "stay": "Unlimited (GCC National ID)", "fee_usd": "$0 (Free)", "time": "Instant", "category": "visa_free"},
        "United Kingdom 🇬🇧": {"status": "Electronic Travel Authorisation (ETA) 💻", "stay": "6 Months", "fee_usd": "£10 (~$13)", "time": "3 - 24 Hours", "category": "evisa"},
        "Turkey 🇹🇷": {"status": "eVisa / Visa on Arrival 💻", "stay": "90 Days", "fee_usd": "$60", "time": "Instant Online", "category": "evisa"},
        "Morocco 🇲🇦": {"status": "Visa-Free 🟢", "stay": "90 Days", "fee_usd": "$0 (Free)", "time": "Instant (Passport Stamp)", "category": "visa_free"},
        "Egypt 🇪🇬": {"status": "Visa-Free 🟢", "stay": "90 Days", "fee_usd": "$0 (Free)", "time": "Instant", "category": "visa_free"},
        "France / Schengen Area 🇫🇷🇪🇺": {"status": "Cascade Schengen Visa (Embassy) 🏛️", "stay": "90 Days (Multi-year 5-yr cascade)", "fee_usd": "€90 (~$98)", "time": "10 - 15 Days", "category": "embassy"},
        "United States 🇺🇸": {"status": "B1/B2 Visa (10-Year Validity) 🏛️", "stay": "6 Months per entry", "fee_usd": "$185", "time": "Interview Required", "category": "embassy"},
        "Singapore 🇸🇬": {"status": "Visa-Free / SG Arrival Card 🟢", "stay": "30 Days", "fee_usd": "$0 (Free)", "time": "Instant", "category": "visa_free"},
        "Japan 🇯🇵": {"status": "eVisa for Tourism 💻", "stay": "90 Days", "fee_usd": "$25", "time": "5 Business Days", "category": "evisa"}
    },
    "United Arab Emirates 🇦🇪": {
        "France / Schengen Area 🇫🇷🇪🇺": {"status": "Visa-Free (Bilateral Waiver) 🟢", "stay": "90 Days within 180 Days", "fee_usd": "$0 (Free)", "time": "Instant at Border", "category": "visa_free"},
        "United Kingdom 🇬🇧": {"status": "Electronic Travel Authorisation (ETA) 💻", "stay": "6 Months", "fee_usd": "£10 (~$13)", "time": "3 - 24 Hours", "category": "evisa"},
        "Saudi Arabia 🇸🇦": {"status": "GCC Freedom of Movement 🟢", "stay": "Unlimited (GCC National ID)", "fee_usd": "$0 (Free)", "time": "Instant", "category": "visa_free"},
        "Turkey 🇹🇷": {"status": "Visa-Free 🟢", "stay": "90 Days", "fee_usd": "$0 (Free)", "time": "Instant", "category": "visa_free"},
        "Morocco 🇲🇦": {"status": "Visa-Free 🟢", "stay": "90 Days", "fee_usd": "$0 (Free)", "time": "Instant", "category": "visa_free"},
        "Japan 🇯🇵": {"status": "Visa-Free 🟢", "stay": "30 Days", "fee_usd": "$0 (Free)", "time": "Instant", "category": "visa_free"},
        "Singapore 🇸🇬": {"status": "Visa-Free 🟢", "stay": "30 Days", "fee_usd": "$0 (Free)", "time": "Instant", "category": "visa_free"},
        "United States 🇺🇸": {"status": "B1/B2 Visa 🏛️", "stay": "6 Months per entry", "fee_usd": "$185", "time": "Interview Required", "category": "embassy"}
    },
    "France / Schengen Area 🇫🇷🇪🇺": {
        "Morocco 🇲🇦": {"status": "Visa-Free 🟢", "stay": "90 Days", "fee_usd": "$0 (Free)", "time": "Instant", "category": "visa_free"},
        "United Arab Emirates 🇦🇪": {"status": "Visa-Free 🟢", "stay": "90 Days", "fee_usd": "$0 (Free)", "time": "Instant", "category": "visa_free"},
        "Saudi Arabia 🇸🇦": {"status": "eVisa / Visa on Arrival 💻", "stay": "90 Days (Multiple Entry)", "fee_usd": "$125", "time": "Instant Online", "category": "evisa"},
        "United States 🇺🇸": {"status": "ESTA Visa Waiver 💻", "stay": "90 Days", "fee_usd": "$21", "time": "2 - 72 Hours Online", "category": "evisa"},
        "United Kingdom 🇬🇧": {"status": "Visa-Free / ETA 💻", "stay": "6 Months", "fee_usd": "£10 (~$13)", "time": "Instant / 24 Hours", "category": "evisa"},
        "Japan 🇯🇵": {"status": "Visa-Free 🟢", "stay": "90 Days", "fee_usd": "$0 (Free)", "time": "Instant", "category": "visa_free"},
        "Singapore 🇸🇬": {"status": "Visa-Free 🟢", "stay": "90 Days", "fee_usd": "$0 (Free)", "time": "Instant", "category": "visa_free"}
    },
    "United States 🇺🇸": {
        "Morocco 🇲🇦": {"status": "Visa-Free 🟢", "stay": "90 Days", "fee_usd": "$0 (Free)", "time": "Instant", "category": "visa_free"},
        "France / Schengen Area 🇫🇷🇪🇺": {"status": "Visa-Free (ETIAS) 🟢", "stay": "90 Days within 180 Days", "fee_usd": "€7 (~$8)", "time": "Instant Online", "category": "visa_free"},
        "United Kingdom 🇬🇧": {"status": "Visa-Free / ETA 💻", "stay": "6 Months", "fee_usd": "£10 (~$13)", "time": "Instant / 24 Hours", "category": "evisa"},
        "United Arab Emirates 🇦🇪": {"status": "Visa on Arrival 🟢", "stay": "30 Days", "fee_usd": "$0 (Free)", "time": "Instant at Airport", "category": "voa"},
        "Saudi Arabia 🇸🇦": {"status": "eVisa / Visa on Arrival 💻", "stay": "90 Days", "fee_usd": "$125", "time": "Instant Online", "category": "evisa"},
        "Japan 🇯🇵": {"status": "Visa-Free 🟢", "stay": "90 Days", "fee_usd": "$0 (Free)", "time": "Instant", "category": "visa_free"}
    }
}

class VisaIntelligenceEngine:
    """Calculates entry regulations, visa costs, and passport requirements."""

    @staticmethod
    def get_visa_requirement(origin_country: str, dest_country: str) -> Dict[str, Any]:
        """Look up bilateral visa rules and documentation requirements."""
        if origin_country in VISA_RULES_MATRIX and dest_country in VISA_RULES_MATRIX[origin_country]:
            rule = VISA_RULES_MATRIX[origin_country][dest_country].copy()
        else:
            # Smart default rule generator for unlisted combinations
            rule = {
                "status": "Embassy / eVisa Pre-Approval Required 🏛️",
                "stay": "30 - 90 Days",
                "fee_usd": "$50 - $140",
                "time": "5 - 15 Business Days",
                "category": "standard"
            }

        rule["origin"] = origin_country
        rule["destination"] = dest_country
        rule["passport_validity_min"] = "6 Months minimum validity from planned departure date"
        rule["mandatory_documents"] = [
            "Valid Biometric Passport (with at least 2 blank visa pages)",
            "Confirmed Return / Onward Flight Itinerary",
            "Proof of Accommodation (Hotel booking or official host invitation)",
            "International Travel Health & Medical Evacuation Insurance",
            "Proof of Sufficient Financial Means (Recent bank statements or credit card)"
        ]
        return rule
