"""High-Performance Interactive Plotly Visualizations for Aviation Radar, Conflict Airspace & Safety Analytics."""

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.conflict_zones_data import CONFLICT_ZONES_DATABASE
from src.airports_data import AIRPORTS_DATABASE

PALETTE = {
    "bg": "#0e1117",
    "card_bg": "#1e222b",
    "text": "#e0e6ed",
    "primary": "#38bdf8",     # Sky Blue
    "secondary": "#f59e0b",   # Amber / Runway
    "accent": "#10b981",      # Emerald / Safe
    "danger": "#ef4444",      # Red / War Zone
    "purple": "#a855f7",
    "orange": "#f97316",
    "grid": "#2a303c"
}

def create_flight_radar_map(
    flights_df: pd.DataFrame,
    flight_path: Optional[List[Tuple[float, float]]] = None,
    dep_airport: Optional[Dict[str, Any]] = None,
    arr_airport: Optional[Dict[str, Any]] = None,
    highlight_conflicts: bool = True
) -> go.Figure:
    """Create global real-time flight radar map with aircraft, conflict polygons, and planned routes."""
    fig = go.Figure()

    # 1. Conflict Airspaces & No-Fly Zones Layer
    if highlight_conflicts:
        first_zone = True
        for zone_id, zone in CONFLICT_ZONES_DATABASE.items():
            poly = zone["polygon"]
            lons = [p[0] for p in poly]
            lats = [p[1] for p in poly]
            color = "#ef4444" if zone["risk_code"] == 3 else ("#f97316" if zone["risk_code"] == 2 else "#eab308")

            fig.add_trace(go.Scattergeo(
                lon=lons,
                lat=lats,
                mode="lines",
                name="⛔ Conflict Airspaces & War Zones",
                line=dict(width=2, color=color, dash="dash"),
                fill="toself",
                fillcolor=f"rgba(239, 68, 68, 0.18)" if zone["risk_code"] == 3 else f"rgba(249, 115, 22, 0.12)",
                hoverinfo="text",
                text=(
                    f"⛔ <b>{zone['name']}</b><br>"
                    f"Risk: {zone['risk_level']}<br>"
                    f"Reason: {zone['reason']}<br>"
                    f"Advisory: {zone['advisory']}"
                ),
                showlegend=first_zone
            ))
            first_zone = False

    # 2. Planned Flight Path (Great Circle Route)
    if flight_path and len(flight_path) > 1:
        path_lats = [p[0] for p in flight_path]
        path_lons = [p[1] for p in flight_path]
        fig.add_trace(go.Scattergeo(
            lon=path_lons,
            lat=path_lats,
            mode="lines",
            name="🧭 Planned Trajectory",
            line=dict(width=3.5, color="#38bdf8", dash="solid"),
            hoverinfo="text",
            text="Planned Flight Corridor"
        ))

    # 3. Departure & Arrival Airports
    if dep_airport:
        fig.add_trace(go.Scattergeo(
            lon=[dep_airport["lon"]],
            lat=[dep_airport["lat"]],
            name=f"🛫 DEP: {dep_airport.get('iata', 'DEP')}",
            mode="markers+text",
            text=[f"🛫 {dep_airport.get('iata', '')}"],
            textposition="top center",
            textfont=dict(color="#10b981", size=12, family="Inter"),
            marker=dict(size=14, color="#10b981", symbol="circle", line=dict(width=2, color="#ffffff"))
        ))

    if arr_airport:
        fig.add_trace(go.Scattergeo(
            lon=[arr_airport["lon"]],
            lat=[arr_airport["lat"]],
            name=f"🛬 ARR: {arr_airport.get('iata', 'ARR')}",
            mode="markers+text",
            text=[f"🛬 {arr_airport.get('iata', '')}"],
            textposition="top center",
            textfont=dict(color="#f59e0b", size=12, family="Inter"),
            marker=dict(size=14, color="#f59e0b", symbol="diamond", line=dict(width=2, color="#ffffff"))
        ))

    # 4. Major Worldwide Airport Hubs
    hub_lats = [a["lat"] for a in AIRPORTS_DATABASE.values()]
    hub_lons = [a["lon"] for a in AIRPORTS_DATABASE.values()]
    hub_texts = [f"🏛️ <b>{a['name']}</b> ({a.get('iata', '')})<br>{a['city']}, {a['country']}" for a in AIRPORTS_DATABASE.values()]

    fig.add_trace(go.Scattergeo(
        lon=hub_lons,
        lat=hub_lats,
        name="🏛️ Airport Hubs",
        mode="markers",
        marker=dict(size=6, color="#94a3b8", opacity=0.7),
        text=hub_texts,
        hoverinfo="text"
    ))

    # 5. Real-Time ADS-B Aircraft Layer
    if not flights_df.empty:
        hover_texts = []
        for _, r in flights_df.iterrows():
            cs = r["callsign"]
            alt = r["altitude_ft"]
            spd = r["speed_kts"]
            hdg = r["heading_deg"]
            cntry = r["origin_country"]
            phase = r["flight_phase"]
            emg = f"<br><b>{r['emergency']}</b>" if "7700" in r["emergency"] or "7600" in r["emergency"] else ""
            hover_texts.append(
                f"✈️ <b>Flight {cs}</b> ({cntry})<br>"
                f"Altitude: <b>{alt:,} ft</b> (FL{int(alt/100):03d})<br>"
                f"Ground Speed: <b>{spd} kts</b> ({r['speed_kmh']} km/h)<br>"
                f"Heading: <b>{hdg}°</b> | Phase: {phase}{emg}"
            )

        fig.add_trace(go.Scattergeo(
            lon=flights_df["longitude"],
            lat=flights_df["latitude"],
            mode="markers",
            name="✈️ Live Flights (ADS-B)",
            text=hover_texts,
            hoverinfo="text",
            marker=dict(
                size=8,
                color=flights_df["altitude_ft"],
                colorscale="Viridis",
                colorbar=dict(title="Altitude<br>(Feet)", x=1.02, len=0.6),
                cmin=5000,
                cmax=41000,
                opacity=0.9,
                line=dict(width=0.5, color="#ffffff")
            )
        ))

    fig.update_geos(
        projection_type="natural earth",
        showland=True,
        landcolor="#1a202c",
        showocean=True,
        oceancolor="#0c1017",
        showlakes=True,
        lakecolor="#0c1017",
        showcountries=True,
        countrycolor="#334155",
        coastlinecolor="#475569",
        bgcolor=PALETTE["bg"]
    )

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor=PALETTE["bg"],
        paper_bgcolor=PALETTE["bg"],
        height=650,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=11)
        ),
        margin=dict(l=10, r=10, t=30, b=10)
    )
    return fig

def create_runway_crosswind_compass(xwind_data: Dict[str, Any], rwy_name: str = "Primary Runway") -> go.Figure:
    """Polar radar compass displaying runway heading, wind vector, crosswind, and headwind."""
    rwy_hdg = xwind_data["runway_heading_deg"]
    wind_dir = xwind_data["wind_direction_deg"]
    headwind = xwind_data["headwind_component_kts"]
    crosswind = xwind_data["crosswind_component_kts"]

    fig = go.Figure()

    # Runway Alignment Line (Dual direction: rwy_hdg and reciprocal)
    reciprocal_hdg = (rwy_hdg + 180) % 360
    fig.add_trace(go.Scatterpolar(
        r=[30, 0, 30],
        theta=[rwy_hdg, 0, reciprocal_hdg],
        mode="lines+markers",
        name=f"Runway {rwy_hdg:02d}/{int(reciprocal_hdg/10):02d}",
        line=dict(color="#f59e0b", width=5),
        marker=dict(size=8, color="#f59e0b")
    ))

    # Wind Vector Line
    fig.add_trace(go.Scatterpolar(
        r=[0, abs(headwind) + abs(crosswind)],
        theta=[0, wind_dir],
        mode="lines+markers",
        name=f"Wind Vector ({wind_dir:03d}°)",
        line=dict(color="#38bdf8", width=3, dash="dash"),
        marker=dict(size=10, symbol="triangle-up", color="#38bdf8")
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 35], gridcolor=PALETTE["grid"]),
            angularaxis=dict(direction="clockwise", rotation=90, gridcolor=PALETTE["grid"])
        ),
        template="plotly_dark",
        plot_bgcolor=PALETTE["bg"],
        paper_bgcolor=PALETTE["bg"],
        title=f"🧭 Runway {rwy_name} Alignment vs. Wind ({xwind_data['crosswind_side']})",
        height=380,
        margin=dict(l=40, r=40, t=60, b=30)
    )
    return fig

def create_phase_of_flight_risk_chart(phase_df: pd.DataFrame) -> go.Figure:
    """Grouped chart of Flight Duration % vs Fatal Accident Share % highlighting the Critical 11 Minutes."""
    fig = go.Figure()
    if phase_df.empty:
        return fig

    fig.add_trace(go.Bar(
        x=phase_df["Phase"],
        y=phase_df["Flight_Duration_Pct"],
        name="Flight Duration (%) ⏱️",
        marker_color="#38bdf8"
    ))

    fig.add_trace(go.Bar(
        x=phase_df["Phase"],
        y=phase_df["Fatal_Accidents_Pct"],
        name="Fatal Accident Share (%) ⚠️",
        marker_color="#ef4444"
    ))

    fig.update_layout(
        title="⚠️ The 'Critical 11 Minutes': Flight Phase Duration vs. Accident Risk Distribution",
        template="plotly_dark",
        barmode="group",
        plot_bgcolor=PALETTE["bg"],
        paper_bgcolor=PALETTE["bg"],
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
        yaxis=dict(title="Percentage (%)", gridcolor=PALETTE["grid"]),
        margin=dict(l=40, r=40, t=75, b=30),
        height=380
    )
    return fig

def create_safety_evolution_chart(evo_df: pd.DataFrame) -> go.Figure:
    """Multi-decade commercial aviation safety evolution line chart."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if evo_df.empty:
        return fig

    fig.add_trace(
        go.Scatter(
            x=evo_df["Decade"],
            y=evo_df["Fatal_Accident_Rate_Per_M_Flights"],
            name="Fatal Accidents per Million Flights 📉",
            mode="lines+markers",
            line=dict(color="#10b981", width=3),
            marker=dict(size=8, color="#10b981")
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Bar(
            x=evo_df["Decade"],
            y=evo_df["Global_Annual_Flights_Millions"],
            name="Global Annual Flights (Millions) 🛫",
            marker_color="rgba(56, 189, 248, 0.35)"
        ),
        secondary_y=True
    )

    fig.update_layout(
        title="📈 Multi-Decadal Commercial Aviation Safety Progress (1970 - 2026)",
        template="plotly_dark",
        plot_bgcolor=PALETTE["bg"],
        paper_bgcolor=PALETTE["bg"],
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=75, b=30),
        height=380
    )
    fig.update_yaxes(title_text="Fatal Accidents / M Flights", secondary_y=False, gridcolor=PALETTE["grid"])
    fig.update_yaxes(title_text="Total Flights (Millions)", secondary_y=True, gridcolor=PALETTE["grid"])
    return fig

def create_causal_factors_pie(causal_df: pd.DataFrame) -> go.Figure:
    """Donut chart showing breakdown of primary fatal accident causal factors."""
    fig = go.Figure()
    if causal_df.empty:
        return fig

    fig.add_trace(go.Pie(
        labels=causal_df["Category"],
        values=causal_df["Fatalities_Share_Pct"],
        hole=0.45,
        marker=dict(colors=["#ef4444", "#f97316", "#f59e0b", "#38bdf8", "#a855f7"]),
        textinfo="label+percent"
    ))

    fig.update_layout(
        title="🔬 Primary Causal Factors in Fatal Commercial Aviation Incidents",
        template="plotly_dark",
        plot_bgcolor=PALETTE["bg"],
        paper_bgcolor=PALETTE["bg"],
        margin=dict(l=20, r=20, t=60, b=20),
        height=380
    )
    return fig

def create_delay_probability_gauge(prob_pct: float) -> go.Figure:
    """Generate Gauge Indicator for Departure Delay Risk Probability."""
    val = float(prob_pct) if (prob_pct is not None and not pd.isna(prob_pct)) else 10.0
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val,
        number={'font': {'size': 38, 'color': PALETTE["text"]}, 'suffix': "%"},
        title={'text': "<b>Flight Delay Risk Index</b>", 'font': {'size': 16, 'color': PALETTE["primary"]}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': PALETTE["text"], 'ticksuffix': "%"},
            'bar': {'color': "#ffffff", 'thickness': 0.25},
            'steps': [
                {'range': [0, 25], 'color': "#10b981"},   # Low (Green)
                {'range': [25, 55], 'color': "#f59e0b"},  # Moderate (Yellow)
                {'range': [55, 80], 'color': "#f97316"},  # High (Orange)
                {'range': [80, 100], 'color': "#ef4444"}  # Severe / Ground Hold (Red)
            ]
        }
    ))
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor=PALETTE["bg"],
        paper_bgcolor=PALETTE["bg"],
        height=320,
        margin=dict(l=40, r=40, t=70, b=30)
    )
    return fig

