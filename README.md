# 🌊 QuantumGreen Fleet AI

**AI Ship Intelligence, Multi-Vessel Fleet Optimization, and Maritime Decarbonization Platform**

QuantumGreen Fleet AI is a commercial-grade maritime decision support system designed to assist shipowners, technical superintendents, charterers, and fleet operators. It combines naval architecture hydrodynamic propulsion modeling, IMO MEPC decarbonization guidelines, environmental weather routing, and quantum-inspired simulated annealing solvers into an intuitive multi-page web platform.

---

## 🚀 Core Features Overview

### 1. 🚢 AI Ship Intelligence & Solution Engine (`pages/1_🚢_AI_Ship_Intelligence.py`) — *Core Feature #19*
* **Professional Maritime Input Form (Part A):**
  * **Vessel Specifications:** Ship name, IMO number (with 7-digit checksum verification), MMSI (9-digit verification), vessel type, length, beam, draft, deadweight tonnage (DWT), maximum capacity, current cargo weight, fuel type, engine SFOC ($g/\text{kWh}$), engine power ($kW$), and current bunker reserve.
  * **Voyage Information:** Departure and destination ports (with verified coordinates), current coordinates, planned route, planned speed, sailing distance, departure time, and delivery deadline.
  * **Operating Conditions:** Sea state (Beaufort scale), significant wave height ($H_s$), wind speed, bunker fuel price, carbon tax penalty, operating speed constraints, and carbon budget.
  * **Data Provenance Badges:** Clearly tags values as `[User Entered]`, `[Verified AIS / Registry]`, or `[System Estimated / Calibrated Baseline]`.
  * **Unit Selectors:** Seamless switching between Nautical Miles (NM) $\leftrightarrow$ Kilometers (km), Knots $\leftrightarrow$ km/h, and Metric Tonnes $\leftrightarrow$ Long Tons.
  * **Contradiction Rejection:** Automatically rejects impossible inputs (e.g., cargo exceeding deadweight, departure after deadline, speeds outside commercial naval boundaries).
* **Natural-Language Problem Input (Part B):**
  * Large dedicated text area with quick-select pills for all 10 standard maritime problems:
    1. *Why is my ship consuming more fuel than expected?*
    2. *Which route is more fuel-efficient for this voyage?*
    3. *How much fuel might this ship need to reach its destination?*
    4. *Can this ship reach the destination before the deadline?*
    5. *Which available vessel should carry this shipment?*
    6. *How can I reduce fuel costs without missing the delivery deadline?*
    7. *What should I investigate if the ship deviates from its planned route?*
    8. *Which fleet assignment minimizes fuel consumption and estimated CO2 emissions?*
    9. *What happens to the voyage if the weather worsens?*
    10. *Can this fleet operate within a specified carbon budget?*
* **10-Section Structured Advisory Report (Part D):**
  1. **Problem Understanding:** Restates the user's inquiry and identifies the analytical problem class.
  2. **Input Summary:** Tabular summary of all parameters and provenance badges.
  3. **Data Quality & Missing Information:** Identifies missing parameters and applies transparent maritime fallbacks without inventing values.
  4. **Technical Analysis:** Explains hydrodynamic power curves, Admiralty coefficient, cubic speed law ($P \propto V^3$), and Kwon added resistance.
  5. **Calculated Results:** Key metrics, fuel burn, duration, ETA, fuel costs, emissions, IMO CII grade, and speed-consumption curve.
  6. **Recommended Solution:** Prioritized actionable advice with bunker reserve margins.
  7. **Explanation:** Detailed operational trade-offs (Speed vs Fuel vs Demurrage).
  8. **Expected Impact:** Before-and-after percentage savings relative to the 14-knot commercial baseline.
  9. **Confidence & Limitations:** Transparent uncertainty evaluation; no fabricated confidence percentages.
  10. **Next Actions:** Actionable steps and follow-up guidance.
* **Interactive Follow-Up Scenario Solving (Part G):**
  * One-click sensitivity mutations (*"What if speed increases by 1.5 kn?", "What if fuel prices rise by 10%?", "What if weather worsens?"*).
  * Generates side-by-side Before vs After delta comparisons.

### 2. ⚛️ Quantum-Inspired Fleet Optimizer (`pages/2_⚛️_Quantum_Fleet_Optimizer.py`)
* Constrained combinatorial fleet assignment solver mapping shipments to vessels and routes.
* Simulated Annealing with transverse-field quantum tunneling heuristic.
* Hard vessel capacity constraint enforcement and energy landscape tracking.
* Comparative benchmark against classical greedy direct allocation.

### 3. 🗺️ Voyage & Environmental Route Planner (`pages/3_🗺️_Voyage_Route_Planner.py`)
* 3D PyDeck visualization of maritime passages and shipping corridors.
* Corridors: Direct Malacca Strait, Northern Andaman Protected Channel, and Eco Green Corridor.
* Real-time weather resistance simulator based on Kwon's formula and ISO 15016.

### 4. 📡 Vessel & AIS Live Telemetry Stream (`pages/4_📡_Vessel_AIS_Telemetry.py`)
* Searchable commercial ship registry with verified IMO numbers and vessel specifications.
* Simulated live Class-A AIS transponder telemetry broadcast (SOG, COG, Heading, Lat/Lon).
* Cross-track error (XTE) deviation detection.

### 5. 🌱 Emissions & IMO CII Calculator (`pages/5_🌱_Emissions_CII_Calculator.py`)
* IMO MEPC 281(70) emission factors for VLSFO, HFO, MGO, LNG, Methanol, and Biofuels.
* Interactive IMO Carbon Intensity Indicator (CII) simulator (Grades A to E).
* EU ETS and global carbon tax liability calculator.

---

## 🛠️ Architecture & Project Structure

```
c:\Users\Hari\Downloads\Q-India\
├── app.py                              # Main application landing page and navigation hub
├── pages/
│   ├── 1_🚢_AI_Ship_Intelligence.py    # Core Feature: AI Ship Intelligence & Solution Engine
│   ├── 2_⚛️_Quantum_Fleet_Optimizer.py   # Quantum-inspired fleet allocation solver
│   ├── 3_🗺️_Voyage_Route_Planner.py      # Navigational routing and PyDeck 3D maps
│   ├── 4_📡_Vessel_AIS_Telemetry.py     # Verified vessel registry & live AIS stream
│   └── 5_🌱_Emissions_CII_Calculator.py  # IMO MEPC emissions & CII rating calculator
├── modules/
│   ├── __init__.py
│   ├── data_models.py                   # Typed vessel, voyage, condition, and answer data classes
│   ├── validation.py                    # IMO/MMSI checksums, bounds validation, unit converters
│   ├── fuel_model.py                    # Naval architecture Admiralty power & cubic speed curves
│   ├── emissions_calculator.py          # IMO MEPC 281(70) factors and CII rating algorithm
│   ├── voyage_planner.py                # Ports database, nautical distance, and fairway routing
│   ├── ais_service.py                   # Verified vessel registry and live telemetry simulation
│   ├── weather_service.py               # Kwon wave added resistance and Beaufort scale modeling
│   ├── classical_optimizer.py           # Deterministic greedy fleet benchmark solver
│   ├── quantum_optimizer.py             # Quantum-inspired annealing with transverse field tunneling
│   ├── scheduling_engine.py             # ETA, calendar deadline feasibility, and slack analysis
│   ├── ai_engine.py                     # Central 10-step AI intelligence & 10-section report generator
│   └── scenario_engine.py               # Interactive scenario mutations and Before/After delta engine
├── tests/
│   ├── __init__.py
│   ├── test_modules.py                  # Unit tests for validation, physics, emissions, and solvers
│   └── test_scenarios.py                # Acceptance tests for Section B, F, G, and H requirements
├── requirements.txt
└── README.md
```

---

## 🧪 Running Acceptance and Unit Tests

Execute the full automated test suite (32 unit and scenario tests):

```bash
python -m unittest discover tests
```

---

## 🖥️ Running the Application

To launch the multi-page web platform:

```bash
streamlit run app.py
```

---

## ⚖️ Maritime Safety Disclaimer
QuantumGreen Fleet AI provides predictive decision support and operational optimization. It does not control ship propulsion, autopilot, or navigational steering, nor does it book berths or transmit operational orders. All navigation must adhere to SOLAS, COLREGs, and authoritative navigational publications under the command of the Master.
