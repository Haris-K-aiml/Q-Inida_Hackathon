"""
QuantumGreen Fleet AI - AI Ship Intelligence & Solution Engine
Dedicated core intelligence page supporting natural language maritime queries,
rigorous hydrodynamic modeling, constraint validation, and 10-section actionable answers.
"""

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, date, time, timedelta

from modules.data_models import (
    VesselInfo, VoyageInfo, OperatingConditions, ScenarioInput,
    VesselType, FuelType, VoyageStatus, DataProvenance
)
from modules.validation import MaritimeValidator, convert_distance, convert_speed
from modules.ai_engine import MaritimeAIEngine
from modules.ais_service import AISService
from modules.voyage_planner import PORTS_DATABASE, VoyagePlanner
from modules.scenario_engine import ScenarioEngine

# Configure Page
st.set_page_config(
    page_title="AI Ship Intelligence | QuantumGreen Fleet AI",
    page_icon="🚢",
    layout="wide"
)

# Custom Styling for Maritime UI
st.markdown("""
<style>
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .provenance-tag {
        display: inline-block;
        font-size: 0.75rem;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: 600;
        margin-left: 6px;
    }
    .prov-user { background-color: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe; }
    .prov-verified { background-color: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
    .prov-estimated { background-color: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
    .section-header {
        border-left: 4px solid #0284c7;
        padding-left: 10px;
        margin-top: 24px;
        margin-bottom: 12px;
    }
    .disclaimer-box {
        background-color: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 12px;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #78350f;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚢 AI Ship Intelligence & Solution Engine")
st.caption(
    "Data-driven maritime reasoning engine connected to hydrodynamic propulsion models, "
    "IMO MEPC decarbonization calculators, environmental fairway routing, and quantum-inspired optimizers."
)

# Prominent Decision-Support Disclaimer
st.markdown("""
<div class="disclaimer-box">
    ⚖️ <strong>Maritime Decision Support Notice:</strong> QuantumGreen Fleet AI provides predictive decision support and operational optimization. 
    It does not take command of ship propulsion, autopilot, or navigational steering, nor does it book berths or transmit operational orders. 
    All navigation must adhere to SOLAS, COLREGs, and authoritative navigational publications under the command of the Master.
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "current_scenario" not in st.session_state:
    # Initialize with default Section F Example
    st.session_state.current_scenario = ScenarioInput(
        vessel=VesselInfo(
            name="MV Ocean Pioneer",
            imo="9345673",
            mmsi="419001234",
            vessel_type=VesselType.CARGO_GENERAL.value,
            length_m=145.0,
            beam_m=22.0,
            draft_m=7.5,
            dwt_tonnes=12000.0,
            max_cargo_capacity_tonnes=10000.0,
            current_cargo_weight_tonnes=8000.0,
            fuel_type=FuelType.VLSFO.value,
            sfoc_g_per_kwh=175.0,
            engine_power_kw=5200.0,
            current_fuel_tonnes=220.0
        ),
        voyage=VoyageInfo(
            departure_port="Chennai Port",
            destination_port="Singapore",
            current_lat=13.0827,
            current_lon=80.2707,
            planned_route="Direct Malacca Strait",
            planned_speed_knots=12.0,
            distance_nm=1580.0,
            status=VoyageStatus.UNDERWAY.value
        ),
        conditions=OperatingConditions(
            weather_condition="Moderate Sea (BF 4)",
            wind_speed_knots=15.0,
            wave_height_m=1.8,
            fuel_price_per_tonne=650.0,
            carbon_tax_per_tonne_co2=60.0,
            carbon_emission_budget_tonnes=250.0
        ),
        problem_statement="Find a fuel-efficient voyage plan and estimate fuel consumption while keeping the arrival time reasonable."
    )

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "comparison_result" not in st.session_state:
    st.session_state.comparison_result = None

# Quick Load Section F Helper Button
col_quick_f, col_autofill_ais = st.columns([1, 1])
with col_quick_f:
    if st.button("📋 Load Example Scenario (Chennai ➔ Singapore, 8,000t, 12 kn)", type="secondary"):
        st.session_state.current_scenario = ScenarioInput(
            vessel=VesselInfo(
                name="MV Ocean Pioneer",
                imo="9345673",
                mmsi="419001234",
                vessel_type=VesselType.CARGO_GENERAL.value,
                length_m=145.0,
                beam_m=22.0,
                draft_m=7.5,
                dwt_tonnes=12000.0,
                max_cargo_capacity_tonnes=10000.0,
                current_cargo_weight_tonnes=8000.0,
                fuel_type=FuelType.VLSFO.value,
                sfoc_g_per_kwh=175.0,
                engine_power_kw=5200.0,
                current_fuel_tonnes=220.0
            ),
            voyage=VoyageInfo(
                departure_port="Chennai Port",
                destination_port="Singapore",
                current_lat=13.0827,
                current_lon=80.2707,
                planned_route="Direct Malacca Strait",
                planned_speed_knots=12.0,
                distance_nm=1580.0,
                departure_time=datetime.now(),
                delivery_deadline=datetime.now() + timedelta(days=7),
                status=VoyageStatus.UNDERWAY.value
            ),
            conditions=OperatingConditions(
                weather_condition="Moderate Sea (BF 4)",
                wind_speed_knots=15.0,
                wave_height_m=1.8,
                fuel_price_per_tonne=650.0,
                carbon_tax_per_tonne_co2=60.0,
                carbon_emission_budget_tonnes=250.0
            ),
            problem_statement="Find a fuel-efficient voyage plan and estimate fuel consumption while keeping the arrival time reasonable."
        )
        st.session_state.comparison_result = None
        st.success("Loaded Section F baseline scenario!")
        st.rerun()

with col_autofill_ais:
    selected_reg_vessel = st.selectbox(
        "🔍 Autofill from Verified Maritime Fleet Registry:",
        ["None"] + [v["name"] for v in AISService.get_all_registered_vessels()]
    )
    if selected_reg_vessel != "None":
        matched = AISService.lookup_vessel(selected_reg_vessel)
        if matched:
            st.session_state.current_scenario.vessel = AISService.populate_vessel_info_from_registry(
                st.session_state.current_scenario.vessel, matched
            )
            st.info(f"Loaded verified specifications for '{matched['name']}' (IMO {matched['imo']})")

# -----------------------------------------------------------------------------
# PART A: SHIP INFORMATION INPUT FORM
# -----------------------------------------------------------------------------
st.markdown("### 📝 Part A: Maritime Specifications and Operating Parameters")
st.markdown(
    "Enter known vessel and voyage parameters below. Unknown fields may be left blank. "
    "Values will be validated and classified by data provenance."
)

# Unit Selectors
unit_col1, unit_col2, unit_col3 = st.columns(3)
with unit_col1:
    unit_dist = st.selectbox("Distance Unit:", ["Nautical Miles (NM)", "Kilometers (km)"], index=0)
with unit_col2:
    unit_speed = st.selectbox("Speed Unit:", ["Knots (kn)", "km/h"], index=0)
with unit_col3:
    unit_weight = st.selectbox("Cargo Unit:", ["Metric Tonnes (t)", "Long Tons"], index=0)

tab_vessel, tab_voyage, tab_conditions = st.tabs([
    "🚢 Vessel Specifications", "🗺️ Voyage & Schedule", "🌊 Operating Conditions & Constraints"
])

# ---------------- Tab 1: Vessel Specifications ----------------
with tab_vessel:
    v_curr = st.session_state.current_scenario.vessel
    v_col1, v_col2, v_col3 = st.columns(3)

    with v_col1:
        v_name = st.text_input("Ship Name:", value=v_curr.name)
        v_imo = st.text_input("IMO Number (7 digits, optional):", value=v_curr.imo or "")
        v_mmsi = st.text_input("MMSI Number (9 digits, optional):", value=v_curr.mmsi or "")
        v_type_options = [vt.value for vt in VesselType]
        v_type_idx = v_type_options.index(v_curr.vessel_type) if v_curr.vessel_type in v_type_options else 0
        v_type = st.selectbox("Vessel Type:", v_type_options, index=v_type_idx)

    with v_col2:
        v_max_cap = st.number_input(
            "Maximum Cargo Capacity (tonnes):",
            min_value=10.0, max_value=500000.0,
            value=float(v_curr.max_cargo_capacity_tonnes), step=500.0
        )
        v_curr_cargo = st.number_input(
            "Current Cargo Weight (tonnes):",
            min_value=0.0, max_value=500000.0,
            value=float(v_curr.current_cargo_weight_tonnes), step=500.0
        )
        v_length = st.number_input(
            "Length Overall LOA (meters, optional):",
            min_value=0.0, max_value=500.0,
            value=float(v_curr.length_m or 0.0), step=5.0
        )
        v_draft = st.number_input(
            "Design Draft (meters, optional):",
            min_value=0.0, max_value=30.0,
            value=float(v_curr.draft_m or 0.0), step=0.5
        )

    with v_col3:
        fuel_type_options = [ft.value for ft in FuelType]
        fuel_type_idx = fuel_type_options.index(v_curr.fuel_type) if v_curr.fuel_type in fuel_type_options else 0
        v_fuel_type = st.selectbox("Fuel Type:", fuel_type_options, index=fuel_type_idx)
        
        v_fuel_level = st.number_input(
            "Current Fuel Level / Remaining (tonnes, optional):",
            min_value=0.0, max_value=10000.0,
            value=float(v_curr.current_fuel_tonnes or 0.0), step=10.0
        )
        v_sfoc = st.number_input(
            "Engine SFOC (g/kWh, optional):",
            min_value=0.0, max_value=400.0,
            value=float(v_curr.sfoc_g_per_kwh or 0.0), step=5.0,
            help="Specific Fuel Oil Consumption. Leave 0 to use standard IMO benchmark."
        )
        v_engine_power = st.number_input(
            "Engine Power MCR (kW, optional):",
            min_value=0.0, max_value=100000.0,
            value=float(v_curr.engine_power_kw or 0.0), step=200.0
        )

    # Provenance Badges
    st.markdown(
        f"**Data Provenance Status:** "
        f"<span class='provenance-tag prov-user'>User: Name, Cargo</span> "
        f"<span class='provenance-tag {'prov-verified' if v_imo else 'prov-estimated'}'>IMO: {'Verified' if v_imo else 'Optional Blank'}</span> "
        f"<span class='provenance-tag prov-estimated'>SFOC: {'User Value' if v_sfoc > 0 else 'Calibrated IMO MEPC Baseline'}</span>",
        unsafe_allow_html=True
    )

# ---------------- Tab 2: Voyage & Schedule ----------------
with tab_voyage:
    voy_curr = st.session_state.current_scenario.voyage
    voy_col1, voy_col2, voy_col3 = st.columns(3)

    port_list = list(PORTS_DATABASE.keys())
    with voy_col1:
        dep_idx = port_list.index(voy_curr.departure_port) if voy_curr.departure_port in port_list else 0
        voy_dep = st.selectbox("Departure Port:", port_list, index=dep_idx)
        dest_idx = port_list.index(voy_curr.destination_port) if voy_curr.destination_port in port_list else 2
        voy_dest = st.selectbox("Destination Port:", port_list, index=dest_idx)
        voy_route = st.text_input("Planned Route / Corridors:", value=voy_curr.planned_route)
        voy_status_options = [vs.value for vs in VoyageStatus]
        voy_status_idx = voy_status_options.index(voy_curr.status) if voy_curr.status in voy_status_options else 0
        voy_status = st.selectbox("Current Voyage Status:", voy_status_options, index=voy_status_idx)

    with voy_col2:
        # Distance input with unit
        input_dist = voy_curr.distance_nm if "NM" in unit_dist else (voy_curr.distance_nm * 1.852)
        voy_distance_raw = st.number_input(
            f"Total / Remaining Distance ({'NM' if 'NM' in unit_dist else 'km'}):",
            min_value=1.0, max_value=50000.0,
            value=float(input_dist), step=50.0
        )
        # Convert to NM canonical
        voy_dist_nm = voy_distance_raw if "NM" in unit_dist else convert_distance(voy_distance_raw, "km", "NM")

        input_speed = voy_curr.planned_speed_knots if "Knots" in unit_speed else (voy_curr.planned_speed_knots * 1.852)
        voy_speed_raw = st.number_input(
            f"Planned Speed ({'knots' if 'Knots' in unit_speed else 'km/h'}):",
            min_value=1.0, max_value=40.0,
            value=float(input_speed), step=0.5
        )
        voy_speed_knots = voy_speed_raw if "Knots" in unit_speed else convert_speed(voy_speed_raw, "km/h", "knots")

        voy_curr_speed = st.number_input(
            f"Current Speed Over Ground ({'knots' if 'Knots' in unit_speed else 'km/h'}, optional):",
            min_value=0.0, max_value=40.0,
            value=float(voy_speed_raw), step=0.5
        )

    with voy_col3:
        # Calendar & Schedule
        default_dep_date = voy_curr.departure_time.date() if voy_curr.departure_time else date.today()
        voy_dep_date = st.date_input("Departure Date:", value=default_dep_date)
        
        default_deadline_date = voy_curr.delivery_deadline.date() if voy_curr.delivery_deadline else (date.today() + timedelta(days=7))
        has_deadline = st.checkbox("Specify Strict Delivery Deadline", value=True)
        if has_deadline:
            voy_deadline_date = st.date_input("Delivery Deadline Date:", value=default_deadline_date)
            voy_deadline_time = st.time_input("Delivery Deadline Time (UTC):", value=time(18, 0))
            full_deadline_dt = datetime.combine(voy_deadline_date, voy_deadline_time)
        else:
            full_deadline_dt = None

        st.caption(f"Calculated Fairway Baseline Distance: {VoyagePlanner.get_sailing_distance(voy_dep, voy_dest)[0]:,.0f} NM")

# ---------------- Tab 3: Operating Conditions & Constraints ----------------
with tab_conditions:
    c_curr = st.session_state.current_scenario.conditions
    c_col1, c_col2, c_col3 = st.columns(3)

    with c_col1:
        weather_options = [
            "Calm (BF 0-2)", "Slight Sea (BF 3)", "Moderate Sea (BF 4)",
            "Moderate-Rough (BF 5)", "Rough Sea (BF 6)", "High / Storm Sea (BF 8)"
        ]
        w_idx = 2  # Moderate default
        for idx, w_opt in enumerate(weather_options):
            if w_opt.split()[0] in c_curr.weather_condition:
                w_idx = idx
                break
        c_weather = st.selectbox("Current or Expected Weather Sea State:", weather_options, index=w_idx)
        c_wind_speed = st.number_input("Wind Speed (knots, optional):", min_value=0.0, max_value=80.0, value=float(c_curr.wind_speed_knots or 15.0), step=2.0)
        c_wave_height = st.number_input("Significant Wave Height Hs (meters, optional):", min_value=0.0, max_value=20.0, value=float(c_curr.wave_height_m or 1.8), step=0.2)

    with c_col2:
        c_fuel_price = st.number_input("Fuel Price (USD per tonne):", min_value=0.0, max_value=5000.0, value=float(c_curr.fuel_price_per_tonne), step=25.0)
        c_carbon_tax = st.number_input("Carbon Tax / Penalty (USD per tonne CO2):", min_value=0.0, max_value=500.0, value=float(c_curr.carbon_tax_per_tonne_co2), step=5.0)
        c_carbon_budget = st.number_input("Carbon Emission Budget (tonnes CO2, optional):", min_value=0.0, max_value=50000.0, value=float(c_curr.carbon_emission_budget_tonnes or 250.0), step=25.0)

    with c_col3:
        c_speed_min = st.number_input("Minimum Safe Steerage Speed (knots):", min_value=3.0, max_value=20.0, value=float(c_curr.speed_min_knots), step=0.5)
        c_speed_max = st.number_input("Maximum Continuous Engine Speed (knots):", min_value=10.0, max_value=30.0, value=float(c_curr.speed_max_knots), step=0.5)
        c_hist_fuel = st.number_input("Historical Daily Fuel Rate (t/day, optional benchmark):", min_value=0.0, max_value=200.0, value=float(c_curr.historical_daily_fuel or 0.0), step=1.0)

# Save updated inputs into session_state object
st.session_state.current_scenario.vessel.name = v_name
st.session_state.current_scenario.vessel.imo = v_imo if v_imo.strip() else None
st.session_state.current_scenario.vessel.mmsi = v_mmsi if v_mmsi.strip() else None
st.session_state.current_scenario.vessel.vessel_type = v_type
st.session_state.current_scenario.vessel.max_cargo_capacity_tonnes = v_max_cap
st.session_state.current_scenario.vessel.current_cargo_weight_tonnes = v_curr_cargo
st.session_state.current_scenario.vessel.length_m = v_length if v_length > 0 else None
st.session_state.current_scenario.vessel.draft_m = v_draft if v_draft > 0 else None
st.session_state.current_scenario.vessel.fuel_type = v_fuel_type
st.session_state.current_scenario.vessel.current_fuel_tonnes = v_fuel_level if v_fuel_level > 0 else None
st.session_state.current_scenario.vessel.sfoc_g_per_kwh = v_sfoc if v_sfoc > 0 else None
st.session_state.current_scenario.vessel.engine_power_kw = v_engine_power if v_engine_power > 0 else None

st.session_state.current_scenario.voyage.departure_port = voy_dep
st.session_state.current_scenario.voyage.destination_port = voy_dest
st.session_state.current_scenario.voyage.planned_route = voy_route
st.session_state.current_scenario.voyage.distance_nm = voy_dist_nm
st.session_state.current_scenario.voyage.planned_speed_knots = voy_speed_knots
st.session_state.current_scenario.voyage.status = voy_status
st.session_state.current_scenario.voyage.departure_time = datetime.combine(voy_dep_date, time(8, 0))
st.session_state.current_scenario.voyage.delivery_deadline = full_deadline_dt

st.session_state.current_scenario.conditions.weather_condition = c_weather
st.session_state.current_scenario.conditions.wind_speed_knots = c_wind_speed
st.session_state.current_scenario.conditions.wave_height_m = c_wave_height
st.session_state.current_scenario.conditions.fuel_price_per_tonne = c_fuel_price
st.session_state.current_scenario.conditions.carbon_tax_per_tonne_co2 = c_carbon_tax
st.session_state.current_scenario.conditions.carbon_emission_budget_tonnes = c_carbon_budget if c_carbon_budget > 0 else None
st.session_state.current_scenario.conditions.speed_min_knots = c_speed_min
st.session_state.current_scenario.conditions.speed_max_knots = c_speed_max
st.session_state.current_scenario.conditions.historical_daily_fuel = c_hist_fuel if c_hist_fuel > 0 else None

# -----------------------------------------------------------------------------
# PART B: NATURAL-LANGUAGE PROBLEM INPUT
# -----------------------------------------------------------------------------
st.markdown("### 💬 Part B: Natural-Language Problem Input")
st.markdown("Describe your ship or fleet problem in free text, or select one of the core maritime analytical questions below:")

sample_questions = [
    "Why is my ship consuming more fuel than expected?",
    "Which route is more fuel-efficient for this voyage?",
    "How much fuel might this ship need to reach its destination?",
    "Can this ship reach the destination before the deadline?",
    "Which available vessel should carry this shipment?",
    "How can I reduce fuel costs without missing the delivery deadline?",
    "What should I investigate if the ship deviates from its planned route?",
    "Which fleet assignment minimizes fuel consumption and estimated CO2 emissions?",
    "What happens to the voyage if the weather worsens?",
    "Can this fleet operate within a specified carbon budget?"
]

selected_pill = st.pills("Quick Questions:", sample_questions, selection_mode="single")
if selected_pill:
    st.session_state.current_scenario.problem_statement = selected_pill

problem_input = st.text_area(
    "Describe your ship or fleet problem:",
    value=st.session_state.current_scenario.problem_statement,
    height=100,
    placeholder="e.g. Find a fuel-efficient voyage plan and estimate fuel consumption while keeping the arrival time reasonable."
)
st.session_state.current_scenario.problem_statement = problem_input

# -----------------------------------------------------------------------------
# PART C: ANALYZE & SOLVE BUTTON & WORKFLOW
# -----------------------------------------------------------------------------
col_submit, col_status = st.columns([1, 3])
with col_submit:
    solve_clicked = st.button("🚀 Analyze & Solve", type="primary", use_container_width=True)

if solve_clicked:
    with st.spinner("Executing Maritime Validation, Naval Architecture Solvers, and Environmental Analysis..."):
        success, answer, errors_or_warnings = MaritimeAIEngine.solve_scenario(st.session_state.current_scenario)
        if not success:
            st.error("❌ Scenario Validation Failed:")
            for err in errors_or_warnings:
                st.error(f"• {err}")
            st.session_state.analysis_result = None
        else:
            if errors_or_warnings:
                for warn in errors_or_warnings:
                    st.warning(f"⚠️ {warn}")
            st.session_state.analysis_result = answer
            st.session_state.comparison_result = None
            st.success("✅ Analysis and Solution Engine completed successfully!")

# -----------------------------------------------------------------------------
# PART D: STRUCTURED 10-SECTION AI ANSWER
# -----------------------------------------------------------------------------
ans = st.session_state.analysis_result

if ans is not None:
    st.markdown("---")
    st.header("📊 AI Maritime Intelligence — Structured Analysis Report")
    st.caption(f"Engine Mode: {ans.engine_mode} | Generated: {ans.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}")

    # Top KPI Metrics Strip
    m = ans.section_5_calculated_results
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Predicted Fuel", f"{m.fuel_consumption_tonnes:.1f} tonnes", delta=f"{m.hourly_fuel_rate_tonnes if hasattr(m, 'hourly_fuel_rate_tonnes') else ''}")
    kpi2.metric("Estimated Voyage Duration", f"{m.voyage_duration_hours:.1f} hrs", help=f"{m.voyage_duration_days:.1f} sailing days")
    kpi3.metric("Estimated CO2 Emissions", f"{m.co2_emissions_tonnes:.1f} t CO2")
    kpi4.metric("Total Fuel Cost", f"${m.fuel_cost_usd:,.0f}")
    kpi5.metric("IMO CII Rating", f"Grade {m.cii_rating}", delta="Compliant" if m.cii_rating in ['A','B','C'] else "Review Required")

    # 1. Problem Understanding
    with st.expander("1. 🎯 Problem Understanding", expanded=True):
        st.markdown(ans.section_1_problem_understanding)
        st.info(f"**Identified Operational Problem Classification:** `{ans.problem_type}`")

    # 2. Input Summary & Data Provenance
    with st.expander("2. 📋 Input Summary & Data Provenance", expanded=False):
        st.markdown("All vessel parameters, voyage assumptions, and their source verification status:")
        df_inputs = pd.DataFrame(ans.section_2_input_summary)
        st.dataframe(df_inputs, use_container_width=True)

    # 3. Data Quality and Missing Information
    with st.expander("3. 🔍 Data Quality and Missing Information", expanded=False):
        dq = ans.section_3_data_quality_missing_info
        st.markdown(f"**Status:** {dq['data_quality_assessment']}")
        if dq["missing_optional"]:
            st.markdown("**Documented Assumptions & Calibrated Fallbacks:**")
            for item in dq["missing_optional"]:
                st.markdown(f"• **{item['field']}:** {item['action']} *(Impact: {item['impact']})*")
        else:
            st.success("All operational inputs are fully verified without missing fields.")

    # 4. Technical Analysis
    with st.expander("4. ⚙️ Technical Analysis & Maritime Physics", expanded=True):
        st.markdown(ans.section_4_technical_analysis)

    # 5. Calculated Results
    with st.expander("5. 📈 Calculated Results & Numerical Evidence", expanded=True):
        col_res1, col_res2 = st.columns([1, 1])
        with col_res1:
            st.markdown("#### Primary Voyage Metrics")
            st.markdown(f"- **Total Predicted Fuel:** `{m.fuel_consumption_tonnes:.2f} metric tonnes`")
            st.markdown(f"- **Main Engine Shaft Power Required:** `{m.hydrodynamic_power_kw:,.0f} kW`")
            st.markdown(f"- **Total CO2 Generated:** `{m.co2_emissions_tonnes:.2f} tonnes`")
            st.markdown(f"- **Fuel Bunker Expense:** `${m.fuel_cost_usd:,.2f}` (at ${st.session_state.current_scenario.conditions.fuel_price_per_tonne:.2f}/t)")
            st.markdown(f"- **Carbon Compliance / Tax Cost:** `${m.carbon_cost_usd:,.2f}` (at ${st.session_state.current_scenario.conditions.carbon_tax_per_tonne_co2:.2f}/tCO2)")
            st.markdown(f"- **Estimated Voyage Duration:** `{m.voyage_duration_hours:.1f} hours` ({m.voyage_duration_days:.1f} days)")
            if m.estimated_eta:
                st.markdown(f"- **Estimated Time of Arrival (ETA):** `{m.estimated_eta.strftime('%Y-%m-%d %H:%M UTC')}`")
            st.markdown(f"- **Schedule Feasibility:** `{'✅ Feasible' if m.deadline_feasible else '❌ Infeasible / Delay Projected'}`")
            if m.deadline_slack_hours is not None:
                st.markdown(f"- **Schedule Slack Buffer:** `{m.deadline_slack_hours:+.1f} hours`")
            if m.fuel_remaining_at_dest_tonnes is not None:
                st.markdown(f"- **Bunker Reserve at Destination:** `{m.fuel_remaining_at_dest_tonnes:.1f} tonnes` `{'⚠️ Fuel Deficit' if m.fuel_shortage else '✅ Safe Reserve'}`")

        with col_res2:
            st.markdown("#### Speed vs. Fuel Consumption Curve (Cubic Power Law)")
            if ans.speed_curve_data:
                curve_df = pd.DataFrame(ans.speed_curve_data)
                chart = alt.Chart(curve_df).mark_line(point=True, color="#0284c7").encode(
                    x=alt.X("Speed (knots)", scale=alt.Scale(zero=False)),
                    y=alt.Y("Voyage Fuel (tonnes)", title="Total Fuel (tonnes)"),
                    tooltip=["Speed (knots)", "Voyage Fuel (tonnes)", "Daily Fuel (tonnes/day)", "Duration (days)"]
                ).properties(height=260)
                st.altair_chart(chart, use_container_width=True)

        # Alternative Routes Comparison Table
        if ans.route_comparisons:
            st.markdown("#### Maritime Corridor Alternative Comparisons")
            alts_data = []
            for r in ans.route_comparisons:
                alts_data.append({
                    "Corridor / Route": r.route_name,
                    "Distance (NM)": f"{r.distance_nm:,.0f}",
                    "Speed (kn)": f"{r.speed_knots:.1f}",
                    "Duration (days)": f"{r.duration_hours/24:.1f}",
                    "Fuel (tonnes)": f"{r.fuel_tonnes:.1f}",
                    "CO2 (tonnes)": f"{r.co2_tonnes:.1f}",
                    "Fuel Cost ($)": f"${r.fuel_cost_usd:,.0f}",
                    "Weather Condition": r.weather_desc
                })
            st.dataframe(pd.DataFrame(alts_data), use_container_width=True)

    # 6. Recommended Solution
    with st.expander("6. 💡 Recommended Solution & Optimization Action", expanded=True):
        rec = ans.section_6_recommended_solution
        st.subheader(rec["title"])
        st.markdown(rec["summary"])
        st.info(f"**Bunker Reserve Status:** {rec['bunker_verdict']}")
        st.caption(f"**Safety Protocol:** {rec['disclaimer']}")

    # 7. Explanation & Trade-Offs
    with st.expander("7. ⚖️ Explanation & Operational Trade-Offs", expanded=True):
        st.markdown(ans.section_7_explanation)

    # 8. Expected Impact (vs Baseline)
    with st.expander("8. 📉 Expected Impact (Optimized vs Baseline)", expanded=True):
        imp = ans.section_8_expected_impact
        col_imp1, col_imp2, col_imp3 = st.columns(3)
        col_imp1.metric("Fuel Savings", f"{imp['fuel_savings_tonnes']:+.1f} tonnes", delta=f"{imp['fuel_savings_pct']:+.1f}%")
        col_imp2.metric("CO2 Reduction", f"{imp['co2_savings_tonnes']:+.1f} tonnes", delta=f"{imp['co2_savings_pct']:+.1f}%")
        col_imp3.metric("Financial Net Benefit", f"${imp['financial_savings_usd']:+,.0f}")
        st.caption("Baseline: Standard commercial 14-knot sailing on direct corridor without weather avoidance.")

    # 9. Confidence and Limitations
    with st.expander("9. 🛡️ Confidence, Uncertainty & Model Limitations", expanded=False):
        c_and_l = ans.section_9_confidence_and_limitations
        st.markdown(f"**Confidence Assessment:** {c_and_l['confidence_assessment']}")
        st.markdown("**Documented Hydrodynamic Uncertainties:**")
        for unc in c_and_l["documented_uncertainties"]:
            st.markdown(f"• {unc}")
        st.markdown("**Information that would further increase accuracy:**")
        for rec_dat in c_and_l["recommended_data_for_higher_accuracy"]:
            st.markdown(f"• {rec_dat}")

    # 10. Next Actions
    with st.expander("10. 🎯 Actionable Next Steps", expanded=True):
        for idx, act in enumerate(ans.section_10_next_actions, 1):
            st.markdown(f"**{idx}.** {act}")

    # -------------------------------------------------------------------------
    # PART G: INTERACTIVE FOLLOW-UP AND SCENARIO SOLVING
    # -----------------------------------------------------------------------------
    st.markdown("---")
    st.subheader("🔄 Part G: Interactive Follow-Up & Scenario Sensitivity Solving")
    st.markdown(
        "Preserve the current baseline scenario, adjust parameters, and view immediate **Before-and-After** comparisons."
    )

    st.markdown("**Quick Scenario Actions:**")
    fu_cols = st.columns(3)
    
    with fu_cols[0]:
        btn_spd = st.button("⚡ What if speed increases (+1.5 kn)?", use_container_width=True)
        btn_fuel = st.button("📈 What if fuel prices rise by 10%?", use_container_width=True)

    with fu_cols[1]:
        btn_cargo = st.button("📦 What if cargo increases (+15%)?", use_container_width=True)
        btn_wthr = st.button("🌊 What happens if weather worsens?", use_container_width=True)

    with fu_cols[2]:
        btn_vessel = st.button("🚢 Can another vessel sail faster?", use_container_width=True)
        btn_carbon = st.button("🌱 How to stay in carbon budget?", use_container_width=True)

    action_to_apply = None
    if btn_spd:
        action_to_apply = "speed_plus"
    elif btn_fuel:
        action_to_apply = "fuel_plus_10"
    elif btn_cargo:
        action_to_apply = "cargo_plus_15"
    elif btn_wthr:
        action_to_apply = "weather_worsen"
    elif btn_vessel:
        action_to_apply = "another_vessel"
    elif btn_carbon:
        action_to_apply = "carbon_cap"

    # Custom Follow-up text input
    custom_follow_up = st.text_input("Or enter a custom follow-up question:", placeholder="e.g. What if I increase the ship speed?")
    if st.button("Run Custom Follow-Up"):
        if custom_follow_up.strip():
            action_to_apply = custom_follow_up.strip()

    if action_to_apply:
        new_scenario, change_desc = ScenarioEngine.apply_follow_up(st.session_state.current_scenario, action_to_apply)
        with st.spinner("Rerunning hydrodynamic solvers with modified parameters..."):
            succ, new_answer, _ = MaritimeAIEngine.solve_scenario(new_scenario)
            if succ:
                st.session_state.comparison_result = ScenarioEngine.compare_runs(
                    st.session_state.analysis_result, new_answer, change_desc
                )
                st.session_state.current_scenario = new_scenario
                st.session_state.analysis_result = new_answer
                st.success(f"Scenario updated: {change_desc}")
                st.rerun()

    # Display Before vs After Comparison if available
    if st.session_state.comparison_result is not None:
        comp = st.session_state.comparison_result
        st.markdown(f"### ⚖️ Side-by-Side Comparison: {comp['change_description']}")
        
        comp_df = pd.DataFrame(comp["table"])
        st.dataframe(comp_df, use_container_width=True)
        
        # Delta Metrics
        d_col1, d_col2, d_col3 = st.columns(3)
        d_col1.metric("Delta Fuel Consumption", f"{comp['delta_fuel']:+.2f} tonnes")
        d_col2.metric("Delta Total Cost", f"${comp['delta_cost']:+,.2f}")
        d_col3.metric("Delta Voyage Transit Time", f"{comp['delta_hours']:+.1f} hours")
