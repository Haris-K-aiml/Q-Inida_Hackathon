"""
QuantumGreen Fleet AI - Voyage and Route Planner
Interactive maritime navigation planning with PyDeck geographical routing,
waypoint passages, weather-adjusted fairway comparisons, and cubic speed curves.
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import altair as alt

from modules.data_models import VesselInfo, OperatingConditions, FuelType, VesselType
from modules.voyage_planner import PORTS_DATABASE, VoyagePlanner
from modules.weather_service import WeatherService
from modules.fuel_model import MaritimeFuelModel

st.set_page_config(
    page_title="Voyage & Route Planner | QuantumGreen Fleet AI",
    page_icon="🗺️",
    layout="wide"
)
from theme import apply_theme
apply_theme()

st.title("🗺️ Maritime Voyage & Environmental Route Planner")
st.caption(
    "Navigational corridor planning, waypoint tracking, weather routing, and speed optimization "
    "across major global maritime shipping lanes."
)

st.warning(
    "⚠️ Navigational Advisory: Waypoints and track corridors are provided for strategic voyage planning and "
    "fuel optimization. Official passage planning must be conducted using authorized ECDIS and ENC charts."
)

# -----------------------------------------------------------------------------
# PORT SELECTION & ROUTING
# -----------------------------------------------------------------------------
st.subheader("1. Port Selection & Maritime Corridors")
p_col1, p_col2, p_col3 = st.columns(3)

port_keys = list(PORTS_DATABASE.keys())
with p_col1:
    origin = st.selectbox("Departure Port:", port_keys, index=0)  # Chennai
with p_col2:
    destination = st.selectbox("Destination Port:", port_keys, index=2)  # Singapore
with p_col3:
    planned_speed = st.slider("Planned Transit Speed (knots):", min_value=8.0, max_value=22.0, value=12.0, step=0.5)

dist_baseline, dist_method = VoyagePlanner.get_sailing_distance(origin, destination)
st.info(f"Verified Sailing Distance: **{dist_baseline:,.0f} Nautical Miles** ({dist_baseline * 1.852:,.0f} km) — Method: {dist_method}")

# -----------------------------------------------------------------------------
# PYDECK GEOGRAPHICAL MAP
# -----------------------------------------------------------------------------
st.subheader("2. Maritime Waypoint Visualization")
route_style = st.radio(
    "Select Corridor to Visualize:",
    ["Direct Malacca Deep-Water", "Northern Andaman Protected", "Eco Green Corridor (Nicobar)"],
    horizontal=True
)

style_key = "direct"
if "Andaman" in route_style:
    style_key = "andaman"
elif "Eco" in route_style or "Green" in route_style:
    style_key = "eco"

waypoints = VoyagePlanner.get_route_waypoints(origin, destination, style_key)
wp_df = pd.DataFrame(waypoints)

# PyDeck Layers
view_state = pdk.ViewState(
    latitude=wp_df["lat"].mean(),
    longitude=wp_df["lon"].mean(),
    zoom=4.5,
    pitch=20
)

# Line layer
line_data = []
for i in range(len(waypoints) - 1):
    line_data.append({
        "from_lat": waypoints[i]["lat"],
        "from_lon": waypoints[i]["lon"],
        "to_lat": waypoints[i+1]["lat"],
        "to_lon": waypoints[i+1]["lon"],
        "name": f"{waypoints[i]['name']} ➔ {waypoints[i+1]['name']}"
    })

line_layer = pdk.Layer(
    "LineLayer",
    data=pd.DataFrame(line_data),
    get_source_position=["from_lon", "from_lat"],
    get_target_position=["to_lon", "to_lat"],
    get_color=[2, 132, 199, 200],
    get_width=5,
    pickable=True
)

point_layer = pdk.Layer(
    "ScatterplotLayer",
    data=wp_df,
    get_position=["lon", "lat"],
    get_color=[234, 88, 12, 220],
    get_radius=25000,
    pickable=True
)

deck = pdk.Deck(
    layers=[line_layer, point_layer],
    initial_view_state=view_state,
    tooltip={"text": "{name}"},
    map_style="light"
)

st.pydeck_chart(deck)
st.dataframe(wp_df.rename(columns={"name": "Waypoint Name", "lat": "Latitude (°N)", "lon": "Longitude (°E)"}), use_container_width=True)

# -----------------------------------------------------------------------------
# ROUTE COMPARISON & WEATHER IMPACT
# -----------------------------------------------------------------------------
st.subheader("3. Environmental Route Alternative Comparison")

dummy_vessel = VesselInfo(
    name="MV Ocean Pioneer",
    vessel_type=VesselType.CARGO_GENERAL.value,
    max_cargo_capacity_tonnes=10000.0,
    current_cargo_weight_tonnes=8000.0,
    fuel_type=FuelType.VLSFO.value
)
dummy_conditions = OperatingConditions(fuel_price_per_tonne=650.0)

route_alts = VoyagePlanner.compare_route_alternatives(
    vessel=dummy_vessel,
    conditions=dummy_conditions,
    origin_port=origin,
    dest_port=destination,
    base_speed_knots=planned_speed
)

rows = []
for r in route_alts:
    rows.append({
        "Maritime Corridor": r.route_name,
        "Distance (NM)": f"{r.distance_nm:,.0f}",
        "Speed (knots)": f"{r.speed_knots:.1f}",
        "Transit Time (days)": f"{r.duration_hours/24:.1f}",
        "Predicted Fuel (tonnes)": f"{r.fuel_tonnes:.1f}",
        "Predicted CO2 (tonnes)": f"{r.co2_tonnes:.1f}",
        "Fuel Cost (USD)": f"${r.fuel_cost_usd:,.0f}",
        "Weather & Ocean State": r.weather_desc
    })
st.dataframe(pd.DataFrame(rows), use_container_width=True)

# -----------------------------------------------------------------------------
# WEATHER RESISTANCE CALCULATOR
# -----------------------------------------------------------------------------
st.subheader("4. Real-time Weather Penalty Simulator (Kwon / ISO 15016)")
w_c1, w_c2 = st.columns(2)
with w_c1:
    sim_hs = st.slider("Simulate Wave Height Hs (meters):", min_value=0.2, max_value=8.0, value=2.2, step=0.2)
with w_c2:
    sim_wind = st.slider("Simulate Wind Speed (knots):", min_value=0.0, max_value=60.0, value=20.0, step=2.0)

w_factor, w_penalty, w_explanation = WeatherService.calculate_weather_factor(sim_hs, sim_wind)
st.metric("Hydrodynamic Power Penalty Multiplier", f"{w_factor:.3f}x", delta=f"+{w_penalty:.1f}% Fuel Increase")
st.caption(w_explanation)
