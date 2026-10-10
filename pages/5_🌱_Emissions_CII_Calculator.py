"""
QuantumGreen Fleet AI - Emissions & IMO CII Calculator
Calculates voyage greenhouse gas emissions according to IMO MEPC 281(70),
Carbon Intensity Indicator (CII) grade ratings (A to E), and carbon tax compliance.
"""

import streamlit as st
import pandas as pd
import altair as alt

from modules.emissions_calculator import EmissionsCalculator
from modules.data_models import VesselInfo, FuelType, VesselType

st.set_page_config(
    page_title="Emissions & CII Calculator | QuantumGreen Fleet AI",
    page_icon="🌱",
    layout="wide"
)
from theme import apply_theme
apply_theme()

st.title("🌱 Emissions & IMO CII Rating Calculator")
st.caption(
    "IMO MEPC decarbonization framework compliance, IMO Carbon Intensity Indicator (CII) ratings, "
    "and EU ETS / global carbon market compliance modeling."
)

# -----------------------------------------------------------------------------
# IMO MEPC 281(70) EMISSION FACTORS
# -----------------------------------------------------------------------------
st.subheader("1. IMO MEPC Carbon Conversion Factors ($C_F$)")
st.markdown("IMO MEPC 281(70) designates official conversion ratios from fuel metric tonnes to metric tonnes of $CO_2$:")

cf_data = []
for ft_name, factor in EmissionsCalculator.IMO_CARBON_FACTORS.items():
    cf_data.append({
        "Marine Fuel Type": ft_name,
        "IMO Carbon Conversion Factor (t CO2 / t fuel)": factor,
        "Decarbonization Potential": "Baseline Fossil" if factor > 3.0 else ("Transitional Gas (-13%)" if factor > 2.5 else "Low Carbon / Net Zero Alternative (-56%)")
    })
st.dataframe(pd.DataFrame(cf_data), use_container_width=True)

# -----------------------------------------------------------------------------
# INTERACTIVE CII CALCULATOR
# -----------------------------------------------------------------------------
st.subheader("2. Interactive Voyage Carbon Intensity Indicator (CII) Simulator")
c_col1, c_col2, c_col3 = st.columns(3)

with c_col1:
    v_type = st.selectbox("Vessel Type Category:", [vt.value for vt in VesselType], index=0)
    dwt = st.number_input("Deadweight Tonnage (DWT tonnes):", min_value=1000.0, max_value=400000.0, value=12000.0, step=1000.0)

with c_col2:
    dist_nm = st.number_input("Voyage Sailing Distance (Nautical Miles):", min_value=50.0, max_value=25000.0, value=1580.0, step=100.0)
    fuel_burn = st.number_input("Voyage Fuel Consumed (metric tonnes):", min_value=1.0, max_value=5000.0, value=90.0, step=5.0)

with c_col3:
    fuel_type = st.selectbox("Bunker Fuel Type:", [ft.value for ft in FuelType], index=0)
    carbon_tax = st.number_input("Carbon Tax / Allowance Price ($/t CO2):", min_value=0.0, max_value=300.0, value=60.0, step=5.0)

# Compute Emissions & CII
total_co2 = EmissionsCalculator.calculate_co2(fuel_burn, fuel_type)
carbon_tax_cost = EmissionsCalculator.calculate_carbon_tax(total_co2, carbon_tax)

vessel_stub = VesselInfo(vessel_type=v_type, dwt_tonnes=dwt)
rating, attained_cii, required_cii, cii_desc = EmissionsCalculator.calculate_cii(
    vessel=vessel_stub,
    co2_tonnes=total_co2,
    distance_nm=dist_nm
)

st.markdown("---")
st.subheader("3. CII Rating & Regulatory Compliance Results")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total CO2 Emitted", f"{total_co2:.1f} tonnes")
k2.metric("Attained Voyage CII", f"{attained_cii:.2f} g/dwt·nm")
k3.metric("Required Baseline CII", f"{required_cii:.2f} g/dwt·nm")

color_map = {"A": "🟢", "B": "🟢", "C": "🟡", "D": "🟠", "E": "🔴"}
k4.metric(
    "IMO CII Rating",
    f"{color_map.get(rating, '')} Grade {rating}",
    delta="Compliant" if rating in ["A", "B", "C"] else "Corrective Action Required"
)

st.info(f"**Regulatory Interpretation:** {cii_desc}")

# Carbon Tax / ETS Impact
st.markdown(f"**Total Carbon Market Liability (EU ETS / Global Tax):** `${carbon_tax_cost:,.2f}`")

# Educational CII Breakdown
with st.expander("ℹ️ Understanding the IMO Carbon Intensity Indicator (CII) Rating Scale"):
    st.markdown(r"""
    The **Carbon Intensity Indicator (CII)** measures how efficiently a ship transports goods in grams of CO2 per deadweight-tonne nautical mile.
    
    * **Grade A (Superior):** Attained CII $\le d_1 \times \text{CII}_{ref}$. Exceptionally energy efficient.
    * **Grade B (Minor Superior):** Attained CII between $d_1$ and $d_2 \times \text{CII}_{ref}$.
    * **Grade C (Moderate):** Attained CII between $d_2$ and $d_3 \times \text{CII}_{ref}$. Baseline IMO target compliance.
    * **Grade D (Inferior):** Attained CII between $d_3$ and $d_4 \times \text{CII}_{ref}$. Ships rated D for 3 consecutive years must submit a Corrective Action Plan.
    * **Grade E (Major Inferior):** Attained CII $\ge d_4 \times \text{CII}_{ref}$. Immediate ship energy efficiency management plan (SEEMP) revision required.
    """)
