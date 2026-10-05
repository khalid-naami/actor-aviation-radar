# Apify Actor: Global Aviation Radar & Airspace Intelligence ✈️🌐

An advanced real-time aviation intelligence Actor powered by OpenSky Network ADS-B telemetry, FAA/NOAA METAR stations, EASA/FAA conflict airspace databases (CZIB), and real-time Airport Flight Information Display Systems (FIDS).

---

## 🌟 Key Features

1. **Live ADS-B Aircraft Tracking**: Stream real-time airborne flights across global regions or custom bounding boxes (Europe, North America, Middle East, Asia, World).
2. **Conflict Zone & War Hazard Intersections**: Automatically flags flights transiting hazardous airspaces (Ukraine, Red Sea, Yemen, Iran, Syria, etc.).
3. **METAR Weather Intelligence**: Fetches instantaneous METAR observations and decodes IFR/VFR flight rules, dew points, and altimeter settings.
4. **Airport Flight Displays (FIDS)**: Generates comprehensive departure and arrival boards with real-time delays, gate assignments, and aircraft registrations.
5. **Callsign Search**: Pinpoint exact commercial or cargo flights by callsign (e.g., `BAW123`, `RAM501`, `UAE7`).

---

## 📥 Input Schema

| Field | Type | Default | Description |
|---|---|---|---|
| `region` | String | `"Europe"` | Geographic region bounding box (`Europe`, `North America`, `Middle East`, `Asia`, `World`). |
| `maxFlights` | Integer | `50` | Maximum number of aircraft records to fetch. |
| `searchCallsign` | String | `""` | Filter telemetry by flight callsign prefix. |
| `airportIcaoForFids` | String | `"EGLL"` | 4-letter ICAO airport code for FIDS board (e.g. `EGLL`, `KJFK`, `OMDB`, `GMMN`). |
| `includeConflictZones` | Boolean | `true` | Cross-reference flight coordinates against active EASA CZIB conflict zones. |
| `includeMetarWeather` | Boolean | `true` | Query live METAR weather reports for departure and destination airfields. |

---

## 📤 Output Dataset Format

The Actor pushes structured JSON items to the Apify Dataset:
```json
{
  "type": "flight_radar",
  "callsign": "BAW123",
  "icao24": "400a0c",
  "origin_country": "United Kingdom",
  "latitude": 51.4700,
  "longitude": -0.4543,
  "baro_altitude_m": 8500,
  "velocity_ms": 220.5,
  "true_track": 275.0,
  "conflict_zone_risk": "SAFE",
  "metar_observation": {
    "station": "EGLL",
    "raw_metar": "EGLL 032150Z 24012KT 9999 FEW025 15/09 Q1015",
    "flight_rules": "VFR"
  }
}
```

---

## 🚀 How to Run Locally

```bash
cd actor-aviation-radar
pip install -r requirements.txt
python -m src.main
```
