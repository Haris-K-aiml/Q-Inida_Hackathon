"""
QuantumGreen Fleet AI - Main Application Hub
Intelligent Maritime Decarbonization and Fleet Solution Platform.
"""

import streamlit as st

st.set_page_config(
    page_title="QuantumGreen Fleet AI",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header & Branding
st.title("🌊 QuantumGreen Fleet AI")
st.subheader("Intelligent Maritime Decision Support, Fleet Optimization & Decarbonization Platform")
st.markdown(
    "QuantumGreen Fleet AI empowers shipowners, charterers, and fleet operators to enter vessel details, "
    "describe complex maritime challenges in natural language, and receive physics-calibrated, "
    "data-driven solutions connected to hydrodynamic models and quantum-inspired optimizers."
)

# Mandatory Operational Disclaimer
st.info(
    "⚖️ **Operational Decision Support Notice:** QuantumGreen Fleet AI provides predictive analytics, "
    "energy efficiency modeling, and decision support. It does not replace certified electronic navigational charts (ECDIS), "
    "SOLAS-mandated bridge procedures, or the navigational authority of the vessel's Master. "
    "The system does not directly steer vessels or issue binding maritime orders."
)

st.markdown("---")

# Feature Showcase Grid
st.header("🧭 Integrated Core Modules")

c1, c2 = st.columns(2)

with c1:
    st.markdown("""
    ### 🚢 1. AI Ship Intelligence & Solution Engine *(Core Feature #19)*
    * **Full Structured Input Form:** Comprehensive vessel, voyage, and operating parameters with unit converters and data provenance tracking.
    * **Natural Language Problem Input:** Understands and classifies questions regarding high fuel consumption, alternative routes, bunker needs, deadline feasibility, and weather impacts.
    * **10-Section Structured Advisory:** Clear problem understanding, input summary, technical naval architecture analysis, calculated results, trade-offs, and next actions.
    * **Interactive Follow-Up Scenarios:** Instant Before-and-After sensitivity solving (*"What if speed increases?", "What if weather worsens?"*).
    """)

    st.markdown("""
    ### ⚛️ 2. Quantum-Inspired Fleet Optimizer
    * Combinatorial multi-vessel, multi-cargo, multi-route assignment engine.
    * Simulated annealing with transverse-field quantum tunneling heuristic.
    * Benchmark comparisons against classical greedy direct allocation.
    * Hard capacity constraint enforcement and energy landscape tracking.
    """)

with c2:
    st.markdown(r"""
    ### 🗺️ 3. Voyage & Environmental Route Planner
    * Interactive geographical fairway routing using PyDeck 3D visualization.
    * Commercial maritime corridors: Direct Malacca, Northern Andaman Sea, and Eco Green Corridor.
    * Hydrodynamic weather penalty modeling using Kwon's empirical formulation and ISO 15016.
    * Speed-consumption cubic power curves ($P \propto V^3$).
    """)

    st.markdown("""
    ### 📡 4. Vessel & AIS Live Telemetry Stream
    * Searchable verified commercial vessel database with IMO checksum verification.
    * Simulated live Class-A AIS transponder telemetry feed (SOG, COG, Heading).
    * Navigational cross-track error (XTE) deviation alerts.
    """)

    st.markdown("""
    ### 🌱 5. Emissions & IMO CII Calculator
    * IMO MEPC 281(70) conversion factors across VLSFO, MGO, LNG, Methanol, and Biofuels.
    * Automated Carbon Intensity Indicator (CII) rating assessment (Grades A to E).
    * Global carbon tax and EU ETS compliance liability estimation.
    """)

st.markdown("---")

# Quick Navigation Hub
st.header("🚀 Quick Launch Navigation")
st.markdown("Select a module from the sidebar or click below to launch:")

nav_col1, nav_col2, nav_col3 = st.columns(3)
with nav_col1:
    st.page_link("pages/1_🚢_AI_Ship_Intelligence.py", label="Open AI Ship Intelligence", icon="🚢")
with nav_col2:
    st.page_link("pages/2_⚛️_Quantum_Fleet_Optimizer.py", label="Open Quantum Fleet Optimizer", icon="⚛️")
with nav_col3:
    st.page_link("pages/3_🗺️_Voyage_Route_Planner.py", label="Open Voyage Route Planner", icon="🗺️")

# System Status Footer
st.markdown("---")
st.caption(
    "QuantumGreen Fleet AI v2.4 | Naval Architecture Propulsion Models | "
    "IMO MEPC Decarbonization Compliant | Classical & Quantum-Inspired Solvers Online"
)
