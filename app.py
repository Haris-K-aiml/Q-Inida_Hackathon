"""
QuantumGreen Fleet AI
AI-Powered Maritime Intelligence & Fleet Optimization
"""

import streamlit as st

st.set_page_config(
    page_title="QuantumGreen Fleet AI",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)
from theme import apply_theme
apply_theme()

# ---------- PROFESSIONAL AI THEME ----------
st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(ellipse at top right,
        #10375a 0%, #06172d 42%, #020b18 100%);
    color: #edf6ff;
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #071b33, #020b18);
    border-right: 1px solid #16446a;
}

[data-testid="stSidebar"] * {
    color: #e1efff;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}

.hero {
    padding: 35px 32px;
    border-radius: 22px;
    border: 1px solid #17618b;
    background:
        radial-gradient(ellipse at 90% 10%,
        rgba(0, 190, 255, 0.22), transparent 42%),
        linear-gradient(115deg, #071b35, #103b60 70%, #07516a);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.24);
    margin-bottom: 22px;
}

.eyebrow {
    color: #39e7bd;
    text-transform: uppercase;
    letter-spacing: 3px;
    font-size: 12px;
    font-weight: 700;
}

.hero h1 {
    color: #ffffff;
    font-size: clamp(30px, 4vw, 48px);
    margin: 12px 0;
    font-weight: 800;
}

.hero p {
    color: #d2e8fa;
    font-size: 17px;
    line-height: 1.7;
    max-width: 780px;
}

.accent {
    color: #36e6b6;
}

.status {
    display: inline-block;
    padding: 7px 12px;
    border-radius: 20px;
    border: 1px solid #227b78;
    background: rgba(0, 215, 170, 0.08);
    color: #5cf5c9;
    font-size: 12px;
}

.section-title {
    font-size: 23px;
    font-weight: 750;
    color: #f1f7ff;
    margin: 28px 0 15px 0;
}

.metric-card {
    background: linear-gradient(145deg, #0c2946, #07182e);
    border: 1px solid #17466b;
    border-radius: 16px;
    padding: 19px;
    min-height: 125px;
    margin-bottom: 10px;
}

.metric-label {
    color: #a8c5e1;
    font-size: 13px;
}

.metric-value {
    color: #ffffff;
    font-size: 27px;
    font-weight: 750;
    margin-top: 9px;
}

.metric-note {
    color: #43e4b2;
    font-size: 12px;
    margin-top: 5px;
}

.feature-card {
    background: linear-gradient(145deg, #0c2946, #06162b);
    border: 1px solid #17466b;
    border-radius: 16px;
    padding: 20px;
    min-height: 175px;
    margin-bottom: 14px;
}

.feature-card h3 {
    color: #f1f7ff;
    font-size: 18px;
}

.feature-card p {
    color: #b9cee3;
    font-size: 14px;
    line-height: 1.7;
}

div.stButton > button,
div.stLinkButton > a {
    background: linear-gradient(100deg, #0879e8, #00a9c7);
    color: white;
    border: 1px solid #36bafa;
    border-radius: 10px;
    font-weight: 650;
}

div.stButton > button:hover,
div.stLinkButton > a:hover {
    background: #0864ba;
    border-color: #67e7ff;
    color: white;
}

div[data-testid="stPageLink"] a {
    border: 1px solid #1c638b;
    border-radius: 10px;
    background: #0b2743;
}

hr {
    border-color: #17466b;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("""
    <div style="padding:12px 0 22px 0">
        <div style="font-size:35px">🌊</div>
        <div style="font-size:23px;font-weight:800">
            Quantum<span style="color:#39e6b6">Green</span>
        </div>
        <div style="color:#a9c7e5;font-size:14px">
            FLEET AI COMMAND CENTER
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🧭 Navigation")
    st.caption("Choose an operational module")

    st.page_link(
        "app.py",
        label="AI Command Center",
        icon="🏠"
    )
    st.page_link(
        "pages/1_🚢_AI_Ship_Intelligence.py",
        label="Ship Intelligence",
        icon="🚢"
    )
    st.page_link(
        "pages/2_⚛️_Quantum_Fleet_Optimizer.py",
        label="Quantum Fleet Optimizer",
        icon="⚛️"
    )
    st.page_link(
        "pages/3_🗺️_Voyage_Route_Planner.py",
        label="Voyage Route Planner",
        icon="🗺️"
    )

    st.markdown("---")
    st.markdown("### 🌱 Mission")
    st.caption(
        "Smarter ships. Optimized voyages. "
        "Lower emissions. Greener oceans."
    )

    st.markdown("---")
    st.caption("QuantumGreen Fleet AI · v2.5")


# ---------- HERO ----------
st.markdown(
    """
    <div style="text-align:center; color:#83a6c8; font-size:12px; padding:15px">
        🌊 QuantumGreen Fleet AI | AI Maritime Intelligence | Sustainable Fleet Operations
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- METRICS ----------
st.markdown(
    '<div class="section-title">📡 Fleet Intelligence Overview</div>',
    unsafe_allow_html=True
)

st.caption(
    "Connect these overview cards to your actual model outputs "
     "before presenting operational figures."
)

m1, m2, m3, m4 = st.columns(4)

metrics = [
    (m1, "🚢", "Fleet Monitoring", "Multi-vessel", "Vessel intelligence"),
    (m2, "⚛️", "Optimization Engine", "Quantum-inspired", "Route and allocation"),
    (m3, "🌿", "Emission Analytics", "CO₂ tracking", "Sustainability analysis"),
    (m4, "🧠", "AI Decision Support", "Smart insights", "Data-driven advisory"),
]

for col, icon, label, value, note in metrics:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{icon} {label}</div>
            <div class="metric-value" style="font-size:21px">
                {value}
            </div>
            <div class="metric-note">{note}</div>
        </div>
        """, unsafe_allow_html=True)


# ---------- MODULE LAUNCHER ----------
st.markdown(
    '<div class="section-title">🚀 AI Module Launcher</div>',
    unsafe_allow_html=True
)

c1, c2 = st.columns(2, gap="large")

with c1:
    st.markdown("""
    <div class="feature-card">
        <div style="font-size:30px">🚢</div>
        <h3>01 · AI Ship Intelligence</h3>
        <p>
            Analyze vessel specifications, voyage conditions,
            fuel requirements, operating constraints, and
            maritime challenges with structured technical advisory.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.page_link(
        "pages/1_🚢_AI_Ship_Intelligence.py",
        label="Launch Ship Intelligence →",
        icon="🚢",
        use_container_width=True
    )

    st.markdown("""
    <div class="feature-card">
        <div style="font-size:30px">🗺️</div>
        <h3>03 · Voyage & Route Intelligence</h3>
        <p>
            Explore maritime corridors, route alternatives,
            weather-related penalties, speed constraints,
            and fuel-efficiency considerations.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.page_link(
        "pages/3_🗺️_Voyage_Route_Planner.py",
        label="Launch Route Planner →",
        icon="🗺️",
        use_container_width=True
    )

with c2:
    st.markdown("""
    <div class="feature-card">
        <div style="font-size:30px">⚛️</div>
        <h3>02 · Quantum-Inspired Fleet Optimizer</h3>
        <p>
            Explore multi-vessel and multi-route allocation
            using your optimization engine, capacity constraints,
            and classical benchmark comparisons.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.page_link(
        "pages/2_⚛️_Quantum_Fleet_Optimizer.py",
        label="Launch Fleet Optimizer →",
        icon="⚛️",
        use_container_width=True
    )

    st.markdown("""
    <div class="feature-card">
        <div style="font-size:30px">🌱</div>
        <h3>04 · Emissions & Sustainability</h3>
        <p>
            Access your existing emissions calculations,
            carbon-intensity assessment, fuel comparisons,
            and applicable carbon-cost analysis.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Link this button when the corresponding page exists.
    if st.button(
        "Explore Sustainability Modules →",
        use_container_width=True
    ):
        st.info(
            "Open the emissions calculator from your existing "
            "project pages or connect its page here."
        )


# ---------- AI ADVISORY PANEL ----------
st.markdown(
    '<div class="section-title">🧠 Intelligent Operations</div>',
    unsafe_allow_html=True
)

a1, a2 = st.columns([1.4, 1], gap="large")

with a1:
    st.markdown("""
    <div class="feature-card">
        <h3>AI Decision-Support Workflow</h3>
        <p>
            <span style="color:#39e6b6">01</span>
            &nbsp; Enter vessel and voyage parameters.
            <br><br>
            <span style="color:#39e6b6">02</span>
            &nbsp; Run the relevant analysis or optimization module.
            <br><br>
            <span style="color:#39e6b6">03</span>
            &nbsp; Review calculated results, constraints, and trade-offs.
            <br><br>
            <span style="color:#39e6b6">04</span>
            &nbsp; Evaluate efficiency and sustainability implications.
        </p>
    </div>
    """, unsafe_allow_html=True)

with a2:
    st.markdown("""
    <div class="feature-card">
        <h3>🌍 Sustainability Mission</h3>
        <p>
            Support more informed maritime decisions through
            fuel-efficiency analysis, route evaluation, fleet
            optimization, and emissions-aware planning.
        </p>
        <div style="color:#39e6b6;font-weight:700">
            INTELLIGENCE FOR GREENER OCEANS
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------- DISCLAIMER ----------
st.markdown("---")
st.warning(
    "**Operational Decision-Support Notice:** This platform provides "
    "analytical estimates and decision support. It does not replace "
    "certified electronic navigational charts (ECDIS), SOLAS-mandated "
    "bridge procedures, or the vessel Master's authority. "
    "Outputs must be independently validated before operational use."
)

st.markdown(
    """
    <div style="text-align:center;color:#83a6c8;
                font-size:12px;padding:15px">
        🌊 QuantumGreen Fleet AI &nbsp; | &nbsp;
        AI Maritime Intelligence &nbsp; | &nbsp;
        Sustainable Fleet Operations
    </div>
    """,
    unsafe_allow_html=True
)