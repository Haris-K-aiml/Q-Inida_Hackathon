"""
QuantumGreen Fleet AI - Quantum-Inspired Fleet Optimizer
Solves multi-vessel multi-route fleet assignment problems using
quantum-inspired simulated annealing with transverse field tunneling heuristics.
"""

import streamlit as st
import pandas as pd
import altair as alt

from modules.classical_optimizer import ClassicalOptimizer
from modules.quantum_optimizer import QuantumInspiredFleetOptimizer

st.set_page_config(
    page_title="Quantum Fleet Optimizer | QuantumGreen Fleet AI",
    page_icon="⚛️",
    layout="wide"
)
from theme import apply_theme
apply_theme()

st.title("⚛️ Quantum-Inspired Green Fleet Optimizer")
st.caption(
    "Constrained combinatorial fleet assignment engine utilizing quantum-inspired simulated annealing "
    "to minimize aggregate fuel burn, CO2 emissions, and capacity violations."
)

st.info(
    "💡 Educational & Prototype Note: This module executes classical simulated annealing with a transverse-field "
    "tunneling heuristic inspired by Quantum Annealing (QUBO). It does not require quantum hardware."
)

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
st.sidebar.header("Optimization Parameters")

fuel_price = st.sidebar.number_input(
    "Fuel Price (USD per tonne):",
    min_value=100.0, max_value=2500.0, value=650.0, step=25.0
)

carbon_price = st.sidebar.number_input(
    "Carbon Penalty / Tax (USD per tonne CO2):",
    min_value=0.0, max_value=300.0, value=60.0, step=5.0
)

iterations = st.sidebar.slider(
    "Search Iterations:",
    min_value=200, max_value=5000, value=2500, step=100
)

init_temp = st.sidebar.slider(
    "Initial Annealing Temperature:",
    min_value=1000.0, max_value=10000.0, value=5000.0, step=500.0
)

# -----------------------------------------------------------------------------
# FLEET, SHIPMENT & ROUTE CONFIGURATION
# -----------------------------------------------------------------------------
default_vessels = [
    {"name": "Eco Ship Alpha", "capacity": 1200.0, "fuel_rate": 2.8, "fuel_type": "VLSFO"},
    {"name": "Cargo Ship Beta", "capacity": 900.0, "fuel_rate": 3.8, "fuel_type": "VLSFO"},
    {"name": "Fast Ship Gamma", "capacity": 700.0, "fuel_rate": 5.0, "fuel_type": "MGO"}
]

default_shipments = [
    {"name": "Shipment 1 (Containers)", "cargo": 400.0},
    {"name": "Shipment 2 (Dry Bulk)", "cargo": 300.0},
    {"name": "Shipment 3 (Machinery)", "cargo": 250.0},
    {"name": "Shipment 4 (Chemicals)", "cargo": 500.0}
]

default_routes = [
    {"name": "Direct Deep-Water Route", "distance": 900.0, "weather": 1.20},
    {"name": "Coastal Protected Route", "distance": 1100.0, "weather": 1.00},
    {"name": "Green Corridor TSS", "distance": 1000.0, "weather": 0.90}
]

st.subheader("1. Available Fleet & Voyage Logistics")
col_v, col_s, col_r = st.columns(3)

with col_v:
    st.markdown("**Available Commercial Vessels:**")
    st.dataframe(pd.DataFrame(default_vessels), use_container_width=True)

with col_s:
    st.markdown("**Pending Cargo Shipments:**")
    st.dataframe(pd.DataFrame(default_shipments), use_container_width=True)

with col_r:
    st.markdown("**Available Maritime Corridors:**")
    st.dataframe(pd.DataFrame(default_routes), use_container_width=True)

# -----------------------------------------------------------------------------
# RUN OPTIMIZATION SOLVER
# -----------------------------------------------------------------------------
st.markdown("---")
if st.button("🚀 Run Quantum-Inspired Fleet Optimization", type="primary", use_container_width=True):
    with st.spinner("Executing Classical Baseline vs Quantum-Inspired Simulated Annealing..."):
        # Solve baseline
        classical_res = ClassicalOptimizer.solve_greedy_fleet_assignment(
            vessels=default_vessels,
            shipments=default_shipments,
            routes=default_routes,
            fuel_price=fuel_price,
            carbon_tax=carbon_price
        )

        # Solve quantum-inspired annealing
        quantum_res = QuantumInspiredFleetOptimizer.solve(
            vessels=default_vessels,
            shipments=default_shipments,
            routes=default_routes,
            fuel_price=fuel_price,
            carbon_tax=carbon_price,
            iterations=iterations,
            initial_temperature=init_temp,
            random_seed=42
        )

    st.success("Optimization finished! Results displayed below.")

    # -------------------------------------------------------------------------
    # DISPLAY RECOMMENDED FLEET PLAN
    # -------------------------------------------------------------------------
    st.subheader("2. Recommended Fleet Assignment Plan")
    opt_assign_df = pd.DataFrame(quantum_res["assignments"])
    st.dataframe(
        opt_assign_df[[
            "shipment_name", "cargo_tonnes", "vessel_name", "route_name", "distance_km", "fuel_tonnes", "co2_tonnes"
        ]].rename(columns={
            "shipment_name": "Shipment",
            "cargo_tonnes": "Cargo (t)",
            "vessel_name": "Assigned Vessel",
            "route_name": "Selected Route",
            "distance_km": "Distance (km)",
            "fuel_tonnes": "Est. Fuel (t)",
            "co2_tonnes": "Est. CO2 (t)",

        }),
        width="stretch",
    )

    if quantum_res["valid_plan"]:
        st.success("✅ All vessel capacity limits and cargo allocations are strictly satisfied.")
    else:
        st.error("❌ Capacity constraint violation detected. Increase search iterations.")

    # -------------------------------------------------------------------------
    # PERFORMANCE COMPARISON SUMMARY
    # -------------------------------------------------------------------------
    st.subheader("3. Baseline vs. Quantum-Inspired Optimized Plan")
    
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    col_kpi1.metric(
        "Estimated Total Fuel",
        f"{quantum_res['total_fuel_tonnes']:.2f} t",
        delta=f"{(quantum_res['total_fuel_tonnes'] - classical_res['total_fuel_tonnes']):.2f} t"
    )
    col_kpi2.metric(
        "Estimated CO2 Emissions",
        f"{quantum_res['total_co2_tonnes']:.2f} t",
        delta=f"{(quantum_res['total_co2_tonnes'] - classical_res['total_co2_tonnes']):.2f} t"
    )
    col_kpi3.metric(
        "Total Fleet Cost (Fuel + Carbon)",
        f"${quantum_res['total_cost_usd']:,.2f}",
        delta=f"-${(classical_res['total_cost_usd'] - quantum_res['total_cost_usd']):,.2f}"
    )

    # Detailed Comparative Table
    fuel_savings_pct = ((classical_res["total_fuel_tonnes"] - quantum_res["total_fuel_tonnes"]) / classical_res["total_fuel_tonnes"]) * 100.0
    co2_savings_pct = ((classical_res["total_co2_tonnes"] - quantum_res["total_co2_tonnes"]) / classical_res["total_co2_tonnes"]) * 100.0
    cost_savings_pct = ((classical_res["total_cost_usd"] - quantum_res["total_cost_usd"]) / classical_res["total_cost_usd"]) * 100.0

    comp_df = pd.DataFrame({
        "Performance Measure": ["Fuel Consumption (tonnes)", "CO2 Emissions (tonnes)", "Fuel Expense (USD)", "Carbon Tax (USD)", "Total Operating Cost (USD)"],
        "Classical Baseline": [
            round(classical_res["total_fuel_tonnes"], 2),
            round(classical_res["total_co2_tonnes"], 2),
            f"${classical_res['fuel_cost_usd']:,.2f}",
            f"${classical_res['carbon_cost_usd']:,.2f}",
            f"${classical_res['total_cost_usd']:,.2f}"
        ],
        "Quantum-Inspired Optimized": [
            round(quantum_res["total_fuel_tonnes"], 2),
            round(quantum_res["total_co2_tonnes"], 2),
            f"${quantum_res['fuel_cost_usd']:,.2f}",
            f"${quantum_res['carbon_cost_usd']:,.2f}",
            f"${quantum_res['total_cost_usd']:,.2f}"
        ],
        "Net Efficiency Gain": [
            f"{fuel_savings_pct:+.2f}%",
            f"{co2_savings_pct:+.2f}%",
            f"-${(classical_res['fuel_cost_usd'] - quantum_res['fuel_cost_usd']):,.2f}",
            f"-${(classical_res['carbon_cost_usd'] - quantum_res['carbon_cost_usd']):,.2f}",
            f"{cost_savings_pct:+.2f}% (${(classical_res['total_cost_usd'] - quantum_res['total_cost_usd']):,.2f})"
        ]
    })
    st.dataframe(comp_df, use_container_width=True)

    # -------------------------------------------------------------------------
    # VESSEL CAPACITY UTILIZATION
    # -------------------------------------------------------------------------
    st.subheader("4. Vessel Deadweight Capacity Utilization")
    cap_rows = []
    for idx, v_info in enumerate(default_vessels):
        assigned_load = quantum_res["vessel_loads"][idx]
        cap = v_info["capacity"]
        rem = cap - assigned_load
        cap_rows.append({
            "Vessel Name": v_info["name"],
            "Capacity (t)": cap,
            "Assigned Load (t)": assigned_load,
            "Remaining Capacity (t)": rem,
            "Capacity Status": "Within Limit" if assigned_load <= cap else "OVERLOADED"
        })
    st.dataframe(pd.DataFrame(cap_rows), use_container_width=True)

    # -------------------------------------------------------------------------
    # CHARTS & ENERGY LANDSCAPE
    # -------------------------------------------------------------------------
    st.subheader("5. Optimization Energy Landscape & Convergence")
    if quantum_res["history"]:
        hist_df = pd.DataFrame(quantum_res["history"])
        hist_chart = alt.Chart(hist_df).mark_line(color="#10b981").encode(
            x=alt.X("step", title="Search Iteration Step"),
            y=alt.Y("energy", title="Hamiltonian Energy (Objective Score)", scale=alt.Scale(zero=False)),
            tooltip=["step", "energy", "temperature"]
        ).properties(height=260)
        st.altair_chart(hist_chart, use_container_width=True)
        st.caption(
            "Hamiltonian energy decreases as the transverse field decays and annealing temperature cools, "
            "successfully escaping high-energy barrier regions to locate the global optimum."
        )
