"""
QuantumGreen Fleet AI - Vessel & AIS Live Telemetry Service
Provides verified vessel specifications, IMO/MMSI lookup,
and live simulated AIS Class-A transponder telemetry tracking.
"""

import streamlit as st
import pandas as pd
import pydeck as pdk

from modules.ais_service import AISService, VERIFIED_VESSELS_REGISTRY

st.set_page_config(
    page_title="AIS Telemetry | QuantumGreen Fleet AI",
    page_icon="📡",
    layout="wide"
)
from theme import apply_theme
apply_theme()

st.title("📡 Vessel AIS Registry & Live Telemetry Stream")
st.caption(
    "Verified commercial ship database, IMO/MMSI transponder identification, "
    "and real-time AIS navigational telemetry monitoring."
)

# -----------------------------------------------------------------------------
# VESSEL SEARCH & REGISTRY LOOKUP
# -----------------------------------------------------------------------------
st.subheader("1. Commercial Vessel Registry Lookup")
search_query = st.text_input(
    "Search Registry by Ship Name, IMO Number, or MMSI:",
    placeholder="e.g. Ocean Pioneer or 9345673 or 419001234"
)

matched = AISService.lookup_vessel(search_query) if search_query else None

if search_query:
    if matched:
        st.success(f"✅ Found Verified Vessel: {matched['name']} (IMO {matched['imo']}, Flag: {matched['flag']})")
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Vessel Type", matched["vessel_type"])
        col_m2.metric("Deadweight Tonnage", f"{matched['dwt_tonnes']:,.0f} DWT")
        col_m3.metric("Length / Beam", f"{matched['length_m']}m / {matched['beam_m']}m")
        col_m4.metric("Rated Engine Power", f"{matched['engine_power_kw']:,.0f} kW")
    else:
        st.warning(f"No vessel in the verified registry matching '{search_query}'.")

st.markdown("#### Complete Registered Fleet Database")
fleet_df = pd.DataFrame(VERIFIED_VESSELS_REGISTRY)
st.dataframe(
    fleet_df[[
        "name", "imo", "mmsi", "vessel_type", "dwt_tonnes", "length_m", "beam_m", "draft_m",
        "fuel_type", "engine_power_kw", "base_fuel_rate_tonnes_per_day", "flag"
    ]].rename(columns={
        "name": "Ship Name", "imo": "IMO Number", "mmsi": "MMSI", "vessel_type": "Type",
        "dwt_tonnes": "DWT (t)", "length_m": "Length (m)", "beam_m": "Beam (m)", "draft_m": "Draft (m)",
        "fuel_type": "Fuel", "engine_power_kw": "Power (kW)", "base_fuel_rate_tonnes_per_day": "Base Fuel (t/d)", "flag": "Flag"
    }),
    use_container_width=True
)

# -----------------------------------------------------------------------------
# LIVE AIS BROADCAST MONITORING
# -----------------------------------------------------------------------------
st.subheader("2. Simulated Live Class-A AIS Telemetry Feed")
sel_vessel_name = st.selectbox(
    "Select Target Vessel for Live Tracking:",
    [v["name"] for v in VERIFIED_VESSELS_REGISTRY]
)

telemetry = AISService.get_simulated_live_telemetry(sel_vessel_name)

t_c1, t_c2, t_c3, t_c4 = st.columns(4)
t_c1.metric("Current Latitude / Longitude", f"{telemetry['lat']:.4f}° N, {telemetry['lon']:.4f}° E")
t_c2.metric("Speed Over Ground (SOG)", f"{telemetry['sog_knots']:.1f} knots")
t_c3.metric("Course Over Ground (COG)", f"{telemetry['cog_degrees']:.1f}°")
t_c4.metric("Cross-Track Error (XTE)", f"{telemetry['cross_track_error_nm']:.1f} NM", delta="On Track" if telemetry['cross_track_error_nm'] < 0.5 else "Off Track")

st.markdown(
    f"**Navigation Status:** `{telemetry['nav_status']}` | "
    f"**Destination:** `{telemetry['destination']}` | "
    f"**Last AIS Packet:** `{telemetry['last_ais_contact_utc']}` | "
    f"**Data Source:** `{telemetry['source']}`"
)

# Live Map View of Vessel Position
pos_df = pd.DataFrame([{"lat": telemetry["lat"], "lon": telemetry["lon"], "name": telemetry["vessel_name"]}])
view_state = pdk.ViewState(
    latitude=telemetry["lat"],
    longitude=telemetry["lon"],
    zoom=6,
    pitch=0
)
vessel_pin = pdk.Layer(
    "ScatterplotLayer",
    data=pos_df,
    get_position=["lon", "lat"],
    get_color=[220, 38, 38, 240],
    get_radius=30000,
    pickable=True
)
st.pydeck_chart(pdk.Deck(layers=[vessel_pin], initial_view_state=view_state, tooltip={"text": "{name}"}))
