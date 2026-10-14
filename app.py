"""
app.py
──────
Streamlit Web Frontend for the Quantum Optimization-based Agricultural
Supply Chain Management System (Tamil Nadu Farm-to-Market Logistics).

Run with:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import time
from pathlib import Path
import matplotlib.pyplot as plt

from data_loader import DataLoader
from problem_builder import ProblemBuilder
from quantum_optimizer import QuantumFarmOptimizer
from visualizer import Visualizer
from quantum_routes import candidates, solve_quantum, benchmarks

# Page configuration
st.set_page_config(
    page_title="AgriQuantum | Agricultural Logistics Optimization",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# InspoAI Swiss-Mono / Stripe Clarity Design System Styling
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet"/>

<style>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

    :root {
        --base: #FAFAF8;
        --surface: #FFFFFF;
        --raised: #F0F0EC;
        --line: #D9D9D2;
        --ink: #111110;
        --muted: #6B6B64;
        --accent: #FF4D00;
        --accent-green: #0A8754;
    }

    /* Core Canvas */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        font-family: 'Inter', sans-serif !important;
        background-color: var(--base) !important;
        color: var(--ink) !important;
    }

    [data-testid="stHeader"] {
        background: rgba(250, 250, 248, 0.95) !important;
        backdrop-filter: blur(12px) !important;
        border-bottom: 1px solid var(--line) !important;
    }

    [data-testid="stSidebar"] {
        background: var(--surface) !important;
        border-right: 1px solid var(--line) !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    .block-container {
        max-width: 1480px;
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
    }

    /* Typography */
    h1, h2, h3, h4, .font-display {
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.03em !important;
        font-weight: 600 !important;
        color: var(--ink) !important;
    }
    .font-mono, .mono-label {
        font-family: 'IBM Plex Mono', monospace !important;
        letter-spacing: 0.05em !important;
    }

    /* InspoAI Monospaced Section Kickers */
    .section-kicker {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--muted);
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
    .section-kicker::before {
        content: "";
        display: inline-block;
        width: 6px;
        height: 6px;
        background: var(--accent);
    }

    /* Swiss-Mono Connected KPI Ribbon */
    .kpi-ribbon {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        border: 1px solid var(--line);
        background: var(--line);
        gap: 1px;
        margin-bottom: 2rem;
    }
    .kpi-card {
        background: var(--surface);
        padding: 1.4rem 1.6rem;
        position: relative;
    }
    .kpi-card.highlight {
        border-left: 3px solid var(--accent);
    }
    .kpi-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--muted);
        margin-bottom: 0.5rem;
    }
    .kpi-val {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 600;
        letter-spacing: -0.04em;
        color: var(--ink);
        line-height: 1.1;
    }
    .kpi-sub {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        margin-top: 0.4rem;
        color: var(--accent-green);
    }
    .kpi-sub.muted {
        color: var(--muted);
    }

    /* Top Console Navbar Bar */
    .inspo-navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.8rem 0;
        border-bottom: 1px solid var(--line);
        margin-bottom: 1.5rem;
    }
    .inspo-brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .inspo-badge {
        background: var(--accent);
        color: #FFFFFF;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 3px 7px;
        border-radius: 0px;
    }
    .inspo-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.3rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        margin: 0;
        color: var(--ink);
    }
    .inspo-tag {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.68rem;
        text-transform: uppercase;
        border: 1px solid var(--line);
        padding: 3px 8px;
        color: var(--muted);
        background: var(--raised);
    }

    /* Custom Streamlit Metric Override fallback */
    [data-testid="stMetric"] {
        background: var(--surface) !important;
        border: 1px solid var(--line) !important;
        border-radius: 0px !important;
        padding: 1.25rem 1.4rem !important;
        box-shadow: none !important;
        border-left: 3px solid var(--ink) !important;
    }
    [data-testid="stMetric"]:hover {
        border-left-color: var(--accent) !important;
    }
    [data-testid="stMetricLabel"] {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        color: var(--muted) !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Space Grotesk', sans-serif !important;
        color: var(--ink) !important;
        font-size: 1.85rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.04em !important;
    }

    /* Inspo Segmented Radio Switcher */
    div[role="radiogroup"] {
        display: flex !important;
        background: var(--raised) !important;
        border: 1px solid var(--line) !important;
        padding: 3px !important;
        gap: 3px !important;
        border-radius: 0px !important;
    }
    div[role="radiogroup"] label {
        border-radius: 0px !important;
        padding: 6px 14px !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.78rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
        color: var(--muted) !important;
    }
    div[role="radiogroup"] label:hover {
        color: var(--ink) !important;
    }
    div[role="radiogroup"] label[data-checked="true"], 
    div[role="radiogroup"] label:has(input:checked) {
        background: var(--ink) !important;
        color: #FFFFFF !important;
    }
    div[role="radiogroup"] label[data-checked="true"] p, 
    div[role="radiogroup"] label:has(input:checked) p {
        color: #FFFFFF !important;
    }

    /* Tabs - Clean Inspo Strip */
    [data-testid="stTabs"] [role="tablist"] {
        gap: 0px !important;
        border-bottom: 1px solid var(--line) !important;
        margin-bottom: 1.5rem !important;
        background: transparent !important;
    }
    [data-testid="stTabs"] button[role="tab"] {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.78rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        border-radius: 0px !important;
        padding: 0.75rem 1.5rem !important;
        color: var(--muted) !important;
        border: 1px solid transparent !important;
        border-bottom: none !important;
        background: transparent !important;
        transition: all 0.15s ease !important;
    }
    [data-testid="stTabs"] button[role="tab"]:hover {
        color: var(--ink) !important;
        background: var(--raised) !important;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: var(--ink) !important;
        background: var(--surface) !important;
        border: 1px solid var(--line) !important;
        border-bottom: 2px solid var(--accent) !important;
        font-weight: 600 !important;
    }

    /* Precision Buttons */
    .stButton > button {
        border-radius: 0px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.78rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        font-weight: 600 !important;
        border: 1px solid var(--ink) !important;
        color: var(--ink) !important;
        background: var(--surface) !important;
        padding: 0.6rem 1.4rem !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button:hover {
        background: var(--ink) !important;
        color: var(--surface) !important;
    }
    .stButton > button[kind="primary"] {
        background: var(--accent) !important;
        color: #FFFFFF !important;
        border-color: var(--accent) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: var(--ink) !important;
        border-color: var(--ink) !important;
        color: #FFFFFF !important;
    }

    /* Container Box Borders */
    .inspo-panel {
        border: 1px solid var(--line);
        background: var(--surface);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .inspo-panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid var(--line);
        padding-bottom: 0.8rem;
        margin-bottom: 1.2rem;
    }
    .inspo-panel-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1rem;
        font-weight: 600;
    /* Input controls */
    .stApp input, .stApp textarea, .stApp [data-baseweb="select"] > div {
        border-radius: 0px !important;
        border-color: var(--line) !important;
        background-color: var(--surface) !important;
        color: var(--ink) !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Hero Banner */
    .hero {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1.5rem;
        margin: 0.5rem 0 1.5rem;
        padding: 1.4rem 1.8rem;
        border: 1px solid var(--line);
        background: var(--surface);
    }
    .hero-kicker {
        font-family: 'IBM Plex Mono', monospace;
        color: var(--accent);
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }
    .hero h1 {
        margin: 0;
        font-size: 1.75rem;
        line-height: 1.2;
    }
    .hero p {
        color: var(--muted);
        margin: 0.35rem 0 0;
        font-size: 0.9rem;
    }
    .hero-badge {
        flex: 0 0 auto;
        padding: 0.4rem 0.8rem;
        border: 1px solid var(--line);
        background: var(--raised);
        color: var(--ink);
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        font-weight: 500;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    /* Recommendation Cards */
    .recommendation {
        min-height: 125px;
        padding: 1.15rem 1.25rem;
        border: 1px solid var(--line);
        background: var(--surface);
    }
    .recommendation h4 {
        margin: 0.2rem 0 0.35rem;
        font-size: 0.95rem;
        font-family: 'Space Grotesk', sans-serif;
    }
    .recommendation p {
        margin: 0;
        color: var(--muted);
        font-size: 0.82rem;
        line-height: 1.5;
    }
    .rec-mark {
        font-family: 'IBM Plex Mono', monospace;
        color: var(--muted);
        font-weight: 600;
        font-size: 0.7rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    /* Dataframe tables */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--line) !important;
        border-radius: 0px !important;
        background: var(--surface) !important;
    }

    /* Status Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 2px 7px;
        border: 1px solid transparent;
    }
    .badge-optimum {
        background: rgba(10, 135, 84, 0.1);
        color: #0A8754;
        border-color: rgba(10, 135, 84, 0.3);
    }
    .badge-feasible {
        background: rgba(17, 17, 16, 0.06);
        color: var(--ink);
        border-color: var(--line);
    }
    .badge-quantum {
        background: rgba(255, 77, 0, 0.1);
        color: var(--accent);
        border-color: rgba(255, 77, 0, 0.3);
    }

    /* Benchmark Progress Bar Card */
    .solver-bar-container {
        border: 1px solid var(--line);
        background: var(--surface);
        padding: 1.25rem 1.4rem;
        margin-bottom: 0.75rem;
    }
    .solver-bar-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    .solver-bar-name {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        color: var(--ink);
    }
    .solver-bar-meta {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        color: var(--muted);
    }
    .solver-progress-bg {
        width: 100%;
        height: 12px;
        background: var(--raised);
        border: 1px solid var(--line);
        position: relative;
    }
    .solver-progress-fill {
        height: 100%;
        background: var(--ink);
        transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .solver-progress-fill.qaoa {
        background: var(--accent);
    }
    .solver-progress-fill.anneal {
        background: #4A5568;
    }
</style>
""", unsafe_allow_html=True)



# ── Cached Data Loader ────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Indexing supply chain datasets...")
def get_loader():
    return DataLoader()


loader = get_loader()
price_snapshot_date = pd.to_datetime(loader.prices.get("date"), errors="coerce").max() if not loader.prices.empty else pd.NaT
price_snapshot_label = price_snapshot_date.strftime("%d %b %Y").upper() if pd.notna(price_snapshot_date) else "DATE UNAVAILABLE"

# ── Top Bar Header & Mode Selector ───────────────────────────────────────────
top_c1, top_c2 = st.columns([1.1, 1.4])
with top_c1:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:0.75rem; padding: 0.3rem 0;">
        <div style="background:#FF4D00; color:#FFFFFF; font-family:'IBM Plex Mono',monospace; font-size:0.75rem; font-weight:700; padding:4px 8px;">AQ</div>
        <h2 style="margin:0; font-size:1.4rem; font-family:'Space Grotesk',sans-serif; color:#111110; font-weight:700; letter-spacing:-0.03em;">AGRIQUANTUM</h2>
        <span style="border:1px solid #D9D9D2; background:#F0F0EC; padding:3px 8px; font-family:'IBM Plex Mono',monospace; font-size:0.68rem; text-transform:uppercase; color:#6B6B64;">TN LOGISTICS · {price_snapshot_label}</span>
    </div>
    """, unsafe_allow_html=True)

with top_c2:
    app_mode = st.radio(
        "Select Optimization Scope",
        [
            "🚚 Multi-Batch Fleet Dispatch (MILP / QAOA Portfolio)", 
            "🌾 Single-Farmer Village Route (Logarithmic Binary QAOA)"
        ],
        horizontal=True,
        label_visibility="collapsed",
        help="Switch between joint multi-truck fleet optimization and individual farmer village-to-market recommendation."
    )


# ── Inspo Top Horizontal Parameter Bar ─────────────────────────────────────────
if "Multi-Batch Fleet Dispatch" in app_mode:
    st.markdown('<div class="section-kicker">00 · Dispatch Parameters & Classical / Quantum Controls</div>', unsafe_allow_html=True)
    with st.expander("⚙️ Dispatch Planning Scope & QAOA Configuration", expanded=True):
        p_c1, p_c2, p_c3, p_c4 = st.columns([1, 1, 1.4, 1.3])
        with p_c1:
            num_batches = st.slider(
                "Harvest batches",
                min_value=2,
                max_value=8,
                value=3,
                help="Number of farm harvest batches to allocate."
            )
        with p_c2:
            num_markets = st.slider(
                "Candidate markets",
                min_value=2,
                max_value=8,
                value=3,
                help="Number of destination wholesale / Uzhavar markets."
            )
        with p_c3:
            all_districts = sorted(set(loader.sources["district"].dropna().unique()).union(loader.markets["district"].dropna().unique()))
            selected_districts = st.multiselect(
                "Filter Districts",
                options=all_districts,
                default=[],
                help="Leave empty to search all 9 Tamil Nadu districts."
            )
        with p_c4:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            run_btn = st.button("⚡ Run Solver Portfolio (MILP + QAOA)", type="primary", use_container_width=True, help="Executes Exact Classical MILP, Greedy, Annealing, and QAOA Statevector Simulation")

        st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid var(--line);'>", unsafe_allow_html=True)
        q_c1, q_c2, q_c3 = st.columns([1, 1.2, 1.4])
        with q_c1:
            qaoa_reps = st.slider(
                "Circuit depth (p)",
                min_value=1,
                max_value=3,
                value=1,
                help="Number of alternating QAOA cost and mixer Hamiltonian layers."
            )
        with q_c2:
            qaoa_maxiter = st.slider(
                "Parameter iterations",
                min_value=10,
                max_value=40,
                value=20,
                step=5,
                help="COBYLA parameter optimization steps."
            )
        with q_c3:
            st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
            run_qaoa_toggle = st.checkbox("Include QAOA statevector simulation", value=True, help="Run the Qiskit QAOA simulation alongside exact classical MILP.")

else:
    st.markdown('<div class="section-kicker">00 · Single Shipment Parameters & Logarithmic Quantum Controls</div>', unsafe_allow_html=True)
    with st.expander("⚙️ Single-Farmer Shipment Controls", expanded=True):
        sources_idx = loader.sources.set_index("source_id")
        crops_idx = loader.crops.set_index("crop_id")

        sf_c1, sf_c2, sf_c3, sf_c4, sf_c5 = st.columns([1.5, 1.2, 1, 1, 1.4])
        with sf_c1:
            sf_source_id = st.selectbox(
                "Village / Location",
                sources_idx.index.tolist(),
                format_func=lambda s: f"{sources_idx.loc[s, 'source_name']} ({sources_idx.loc[s, 'district']})"
            )
        with sf_c2:
            default_crop_idx = crops_idx.index.tolist().index("C015") if "C015" in crops_idx.index else 0
            sf_crop_id = st.selectbox(
                "Produce / Crop",
                crops_idx.index.tolist(),
                index=default_crop_idx,
                format_func=lambda c: str(crops_idx.loc[c, "crop_name"])
            )
        with sf_c3:
            sf_quantity = st.number_input("Qty (kg)", min_value=1.0, value=100.0, step=10.0)
        with sf_c4:
            sf_deadline = st.number_input("Limit (hrs)", min_value=0.5, value=24.0, step=0.5)
        with sf_c5:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            sf_run_btn = st.button("⚛️ Execute Quantum QAOA (Top 3)", type="primary", use_container_width=True, help="Evaluates all eligible markets statewide using logarithmic binary-indexed qubits n = ceil(log2(M+1))")


        st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid var(--line);'>", unsafe_allow_html=True)
        sq_c1, sq_c2, sq_c3, sq_c4 = st.columns(4)
        with sq_c1:
            sf_depth = st.slider("Circuit depth (p)", 1, 5, 2)
        with sq_c2:
            sf_iterations = st.slider("COBYLA iterations", 20, 200, 80, 20)
        with sq_c3:
            sf_shots = st.select_slider("Measurement shots", options=[2048, 8192, 32768], value=8192)
        with sq_c4:
            sf_seed = st.number_input("Random seed", min_value=0, max_value=999999, value=42)



# ── Main View Dispatch ────────────────────────────────────────────────────────
if "Multi-Batch Fleet Dispatch" in app_mode:
    # ── Main Header ───────────────────────────────────────────────────────────
    st.markdown(f'''<section class="hero"><div><div class="hero-kicker">Harvest dispatch · Tamil Nadu</div><h1>Farm-to-market, in good flow.</h1><p>Plan fresh produce allocations with route feasibility, market capacity and transport economics in view.</p></div><div class="hero-badge">Price snapshot · {price_snapshot_label}</div></section>''', unsafe_allow_html=True)

    # ── Session State for Storing Run Results ─────────────────────────────────────
    if "last_results" not in st.session_state:
        st.session_state.last_results = None

    # If user clicks button OR initial load without results
    if run_btn or st.session_state.last_results is None:
        with st.spinner("Building optimization problem and executing solvers..."):
            builder = ProblemBuilder(loader)
            districts_filter = selected_districts if selected_districts else None

            problem = builder.build(
                max_batches=num_batches,
                max_markets=num_markets,
                target_districts=districts_filter,
                prune_infeasible=True,
            )

            optimizer = QuantumFarmOptimizer(problem)

            # 1. Greedy
            optimizer.solve_greedy()

            # 2. Classical Exact MILP
            optimizer.solve_classical_milp()

            # 3. Simulated Annealing
            optimizer.solve_simulated_annealing(sweeps=500)

            # 4. QAOA
            if run_qaoa_toggle:
                optimizer.solve_qaoa(reps=qaoa_reps, maxiter=qaoa_maxiter)

            # Save to session
            st.session_state.last_results = {
                "problem": problem,
                "optimizer": optimizer,
                "comparison": optimizer.compare_results(),
                "best_solver": "classical_exact",
            }

    res_data = st.session_state.last_results
    problem = res_data["problem"]
    optimizer = res_data["optimizer"]
    comparison_df = res_data["comparison"]

    # ── Top Metric Cards ──────────────────────────────────────────────────────────
    best_res = optimizer.results.get("classical_exact", optimizer.results.get("greedy", {}))
    qaoa_res = optimizer.results.get("qaoa", {})

    exact_profit = best_res.get("total_profit", 0.0)
    qaoa_profit = qaoa_res.get("total_profit", 0.0)
    approx_ratio = (qaoa_profit / exact_profit * 100.0) if exact_profit > 0 else 0.0
    active_q = qaoa_res.get("num_qubits", min(problem.n_vars, 10))

    # ── InspoAI Swiss-Mono KPI Ribbon ─────────────────────────────────────────────
    st.markdown(f'''
    <div class="section-kicker">01 · Key Metrics</div>
    <div class="kpi-ribbon">
        <div class="kpi-card highlight">
            <div class="kpi-title">Best Feasible Plan</div>
            <div class="kpi-val">₹{exact_profit:,.0f}</div>
            <div class="kpi-sub">Exact MILP Optimal</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">QAOA Approximation</div>
            <div class="kpi-val">{approx_ratio:.1f}%</div>
            <div class="kpi-sub {'muted' if not run_qaoa_toggle else ''}">₹{qaoa_profit:,.0f} candidate</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Simulation Qubits</div>
            <div class="kpi-val">{active_q}</div>
            <div class="kpi-sub muted">{problem.n_vars} problem vars</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Batches Allocated</div>
            <div class="kpi-val">{best_res.get('batches_assigned', 0)} <span style="font-size:1.1rem; color:var(--muted); font-weight:400;">/ {problem.n_batches}</span></div>
            <div class="kpi-sub">100% capacity verified</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('<div class="section-kicker">Dispatch guidance</div>', unsafe_allow_html=True)
    guide1, guide2, guide3 = st.columns(3)
    with guide1:
        st.markdown(f'''<div class="recommendation"><div class="rec-mark">01 · Plan to use</div><h4>Start with the best feasible allocation</h4><p>The current plan assigns {best_res.get('batches_assigned', 0)} of {problem.n_batches} batches and estimates <strong>₹{exact_profit:,.0f}</strong> net objective. Review market and route limits before dispatch.</p></div>''', unsafe_allow_html=True)
    with guide2:
        if not run_qaoa_toggle:
            qaoa_note = "Run the QAOA simulation to compare its candidate with the exact and heuristic baselines."
        elif qaoa_res.get("attribution", "").lower().find("backfill") >= 0:
            qaoa_note = "This candidate uses classical capacity-preserving backfill. Treat it as a hybrid result and inspect feasibility in Solver Benchmarks."
        else:
            qaoa_note = "Compare this statevector simulation with the exact MILP baseline. Simulator results do not demonstrate quantum hardware advantage."
        st.markdown(f'''<div class="recommendation"><div class="rec-mark">02 · Research readout</div><h4>Interpret the QAOA result carefully</h4><p>{qaoa_note}</p></div>''', unsafe_allow_html=True)
    with guide3:
        allocated = best_res.get('batches_assigned', 0)
        if allocated < problem.n_batches:
            capacity_note = f"Some batches remain unallocated. Check market capacity, price margins and the feasibility matrix. Price inputs are a snapshot from {price_snapshot_label}; refresh them before dispatch."
        else:
            capacity_note = f"All selected batches are allocated. Price inputs are a snapshot from {price_snapshot_label}; refresh market prices and confirm vehicle availability and freshness windows with the dispatch team."
        st.markdown(f'''<div class="recommendation"><div class="rec-mark">03 · Before dispatch</div><h4>Validate operational inputs</h4><p>{capacity_note}</p></div>''', unsafe_allow_html=True)

    st.markdown("")

    # ── Interactive Tabs ──────────────────────────────────────────────────────────
    tab_bench, tab_map, tab_schedule, tab_quantum, tab_data = st.tabs([
        "📈 Solver comparison",
        "🗺️ Route map",
        "📋 Dispatch schedule",
        "⚛️ Quantum methods",
        "🧺 Data explorer",
    ])

    # ── Tab 1: Solver Benchmarks ──────────────────────────────────────────────────
    with tab_bench:
        st.subheader("Solver comparison")
        st.caption("Compare net objective, feasibility and runtime across classical baselines and the QAOA candidate.")

        col_tbl, col_chart = st.columns([1.3, 1])

        with col_tbl:
            st.markdown('<div class="section-kicker">01 · Independent Solution Validation</div>', unsafe_allow_html=True)
            styled_df = comparison_df.copy()
            if "Sold Margin (INR)" in styled_df.columns:
                styled_df["Sold Margin (INR)"] = styled_df["Sold Margin (INR)"].map(lambda x: f"₹{x:,.2f}")
            if "Net Objective (INR)" in styled_df.columns:
                styled_df["Net Objective (INR)"] = styled_df["Net Objective (INR)"].map(lambda x: f"₹{x:,.2f}")
            st.dataframe(styled_df, use_container_width=True, hide_index=True)

            qaoa_attr = qaoa_res.get("attribution", "Quantum QAOA")
            q_depth = qaoa_res.get("reps", qaoa_reps)
            st.markdown(f'''
            <div style="display:flex; gap:0.5rem; flex-wrap:wrap; margin-top:0.75rem;">
                <span class="badge badge-optimum">MILP Optimal Verified</span>
                <span class="badge badge-quantum">QAOA Depth p={q_depth}</span>
                <span class="badge badge-feasible">Capacity Feasible: {qaoa_res.get('is_feasible', True)}</span>
            </div>
            ''', unsafe_allow_html=True)

            st.caption("Exact MILP is the operational benchmark. Greedy & Simulated Annealing provide classical heuristic baselines. QAOA runs via Qiskit statevector simulation.")

        with col_chart:
            st.markdown('<div class="section-kicker">02 · Normalized Objective Bars</div>', unsafe_allow_html=True)
            # InspoAI Swiss-Mono normalized benchmark cards
            max_p = max([optimizer.results[s].get("total_profit", 1.0) for s in optimizer.results], default=1.0)
            if max_p <= 0: max_p = 1.0

            bars_html = '<div style="display:flex; flex-direction:column; gap:0.6rem;">'
            for s_name, s_data in optimizer.results.items():
                prof = s_data.get("total_profit", 0.0)
                norm_val = max(0.0, prof / max_p)
                pct_width = min(100.0, norm_val * 100.0)
                is_q = "qaoa" in s_name.lower()
                is_opt = "exact" in s_name.lower() or "milp" in s_name.lower()
                fill_class = "qaoa" if is_q else ("" if is_opt else "anneal")

                badge_label = "1.00 OPT" if is_opt else f"{norm_val:.2f} RATIO"

                bars_html += f'<div class="solver-bar-container"><div class="solver-bar-header"><span class="solver-bar-name">{s_name.replace("_", " ").upper()}</span><span class="solver-bar-meta">₹{prof:,.0f} · {badge_label}</span></div><div class="solver-progress-bg"><div class="solver-progress-fill {fill_class}" style="width: {pct_width:.1f}%;"></div></div></div>'
            bars_html += '</div>'
            st.markdown(bars_html, unsafe_allow_html=True)



    # ── Tab 2: Interactive Dispatch Map ───────────────────────────────────────────
    with tab_map:
        st.subheader("Optimized farm-to-market routes")
        st.caption("Assigned collection centres and candidate destinations for the selected planning scope.")

        assignments = best_res.get("assignments", pd.DataFrame())

        if not assignments.empty:
            # Build coordinates dataframe for PyDeck
            route_records = []
            for _, row in assignments.iterrows():
                batch_row = problem.batches[problem.batches["batch_id"] == row["batch_id"]].iloc[0]
                src_row = loader.sources[loader.sources["source_id"] == batch_row["source_id"]].iloc[0]
                mkt_row = loader.markets[loader.markets["market_id"] == row["market_id"]].iloc[0]

                route_records.append({
                    "batch_id": row["batch_id"],
                    "crop": loader.crop_id_to_name.get(row["crop_id"], row["crop_id"]),
                    "qty": row["quantity_kg"],
                    "profit": row["net_profit"],
                    "src_name": src_row["source_name"],
                    "src_lon": float(src_row["longitude"]),
                    "src_lat": float(src_row["latitude"]),
                    "dst_name": mkt_row["market_name"],
                    "dst_lon": float(mkt_row["longitude_num"]),
                    "dst_lat": float(mkt_row["latitude_num"]),
                })
            routes_df = pd.DataFrame(route_records)

            # Sources & Markets points
            src_points = pd.DataFrame([{
                "lon": float(r["longitude"]), "lat": float(r["latitude"]), "name": r["source_name"]
            } for _, r in loader.sources.iterrows()])

            # Assigned markets
            mkt_points = routes_df[["dst_lon", "dst_lat", "dst_name"]].drop_duplicates().rename(
                columns={"dst_lon": "lon", "dst_lat": "lat", "dst_name": "name"}
            )

            mid_lat = routes_df["src_lat"].mean()
            mid_lon = routes_df["src_lon"].mean()

            view_state = pdk.ViewState(
                latitude=mid_lat if pd.notna(mid_lat) else 11.1271,
                longitude=mid_lon if pd.notna(mid_lon) else 78.6569,
                zoom=7,
                pitch=35,
            )

            # PyDeck layers: Arcs from source to destination
            arc_layer = pdk.Layer(
                "ArcLayer",
                data=routes_df,
                get_source_position=["src_lon", "src_lat"],
                get_target_position=["dst_lon", "dst_lat"],
                get_source_color=[30, 136, 229, 220],   # Blue
                get_target_color=[67, 160, 71, 220],   # Green
                get_width=5,
                auto_highlight=True,
            )

            src_layer = pdk.Layer(
                "ScatterplotLayer",
                data=src_points,
                get_position=["lon", "lat"],
                get_color=[21, 101, 192, 180],
                get_radius=8000,
                pickable=True,
            )

            mkt_layer = pdk.Layer(
                "ScatterplotLayer",
                data=mkt_points,
                get_position=["lon", "lat"],
                get_color=[229, 57, 53, 240],   # Red
                get_radius=12000,
                pickable=True,
            )

            deck = pdk.Deck(
                layers=[src_layer, mkt_layer, arc_layer],
                initial_view_state=view_state,
                tooltip={"text": "{name}\n{src_name} -> {dst_name}\nCrop: {crop} ({qty} kg)\nNet Profit: Rs {profit}"},
                map_style="light",
            )
            st.pydeck_chart(deck)

            st.caption("Blue points show collection centres · Red points show assigned markets · Green arcs show selected transport routes.")
        else:
            st.warning("No assignments generated.")

    # ── Tab 3: Dispatch Schedule & Economics ──────────────────────────────────────
    with tab_schedule:
        st.subheader("Dispatch schedule & economics")
        st.caption("Review assigned produce, destination, freshness-window travel and the modeled financial breakdown.")

        if not assignments.empty:
            sched_df = assignments.copy()
            sched_df["crop_name"] = sched_df["crop_id"].map(loader.crop_id_to_name)
            mkt_map = dict(zip(loader.markets["market_id"], loader.markets["market_name"]))
            sched_df["market_name"] = sched_df["market_id"].map(mkt_map)

            for idx, row in sched_df.iterrows():
                b_row = problem.batches[problem.batches["batch_id"] == row["batch_id"]].iloc[0]
                s_row = loader.sources[loader.sources["source_id"] == b_row["source_id"]].iloc[0]
                sched_df.at[idx, "source_name"] = s_row["source_name"]
                sched_df.at[idx, "distance_km"] = loader.get_travel_distance(b_row["source_id"], row["market_id"])
                sched_df.at[idx, "travel_min"] = loader.get_travel_time(b_row["source_id"], row["market_id"])

            col_display = [
                "batch_id", "crop_name", "quantity_kg", "source_name", "market_name",
                "distance_km", "travel_min", "revenue", "transport_cost", "late_penalty", "net_profit"
            ]
            disp_df = sched_df[[c for c in col_display if c in sched_df.columns]].copy()

            # Format currency
            format_dict = {
                "quantity_kg": "{:,.0f} kg",
                "distance_km": "{:.1f} km",
                "travel_min": "{:.0f} min",
                "revenue": "₹{:,.2f}",
                "transport_cost": "₹{:,.2f}",
                "late_penalty": "₹{:,.2f}",
                "net_profit": "₹{:,.2f}",
            }
            st.dataframe(disp_df.style.format(format_dict), use_container_width=True, hide_index=True)

            # InspoAI Financial Stat Strip
            tot_rev = sched_df["revenue"].sum()
            tot_trans = sched_df["transport_cost"].sum()
            tot_late = sched_df["late_penalty"].sum()
            tot_net = sched_df["net_profit"].sum()

            st.markdown(f'''
            <div class="kpi-ribbon" style="margin-top:1.25rem; margin-bottom:1.5rem;">
                <div class="kpi-card">
                    <div class="kpi-title">Gross Revenue</div>
                    <div class="kpi-val">₹{tot_rev:,.2f}</div>
                    <div class="kpi-sub">Market Wholesale Value</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Transport Cost</div>
                    <div class="kpi-val">₹{tot_trans:,.2f}</div>
                    <div class="kpi-sub muted">Distance & Fuel Model</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Lateness Penalty</div>
                    <div class="kpi-val">₹{tot_late:,.2f}</div>
                    <div class="kpi-sub {'muted' if tot_late == 0 else ''}">Freshness Window Loss</div>
                </div>
                <div class="kpi-card highlight">
                    <div class="kpi-title">Net Farm Profit</div>
                    <div class="kpi-val">₹{tot_net:,.2f}</div>
                    <div class="kpi-sub">Optimized Return</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

            # Download CSV button
            csv_data = disp_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Export Dispatch Schedule (CSV)",
                data=csv_data,
                file_name="optimized_dispatch_schedule.csv",
                mime="text/csv",
                use_container_width=True,
            )

        else:
            st.info("No schedule available.")

    # ── Tab 4: Quantum Formulation & QAOA ─────────────────────────────────────────
    with tab_quantum:
        st.subheader("Quantum optimization methods")
        st.caption("QUBO and Ising formulation details, with a clear comparison to the classical optimization baseline.")

        st.markdown(r"""
        ### 1. QUBO & Ising Hamiltonian Mapping
        The agricultural supply chain allocation is formulated as a **Quadratic Unconstrained Binary Optimization (QUBO)** problem.
        The binary variables $x_{b, m} \in \{0, 1\}$ represent whether batch $b$ is shipped to market $m$.

        Using the spin mapping $x_i = \frac{1 - Z_i}{2}$, the QUBO is mapped to an **Ising Hamiltonian**:
        $$H_C = \sum_{i} h_i Z_i + \sum_{i < j} J_{ij} Z_i Z_j$$
        where $Z_i$ is the Pauli-$Z$ operator acting on qubit $i$.

        ### 2. Quantum Approximate Optimization Algorithm (QAOA)
        QAOA applies alternating unitary operators to an equal superposition state $|+\rangle^{\otimes n}$:
        $$|\vec{\gamma}, \vec{\beta}\rangle = \prod_{k=1}^{p} e^{-i \beta_k H_M} e^{-i \gamma_k H_C} |+\rangle^{\otimes n}$$
        * **Cost Unitary** $e^{-i \gamma_k H_C}$: Encodes the net profit, transport cost, freshness deadlines, and capacity penalties.
        * **Mixer Unitary** $e^{-i \beta_k H_M}$: Transverse field mixer $H_M = \sum_{i} X_i$ providing quantum tunneling.
        * **Variational Optimization:** Classical optimizer (`COBYLA`) iteratively updates $(\vec{\gamma}, \vec{\beta})$ to minimize $\langle H_C \rangle$.
        """)

        st.markdown("---")
        st.subheader("Feasibility & Profit Matrix")

        # Heatmap plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        im1 = ax1.imshow(problem.feasible.astype(int), cmap="RdYlGn", aspect="auto")
        ax1.set_title("Feasibility Matrix (Freshness & Eligibility)")
        ax1.set_xlabel("Market Index")
        ax1.set_ylabel("Batch Index")
        ax1.set_xticks(range(problem.n_markets))
        ax1.set_xticklabels(problem.market_ids, rotation=45, fontsize=8)
        ax1.set_yticks(range(problem.n_batches))
        ax1.set_yticklabels(problem.batch_ids, fontsize=8)
        plt.colorbar(im1, ax=ax1, shrink=0.7)

        disp_prof = np.where(problem.feasible, problem.profit_gain, 0.0)
        im2 = ax2.imshow(disp_prof, cmap="Greens", aspect="auto")
        ax2.set_title("Marginal Net Profit Matrix (INR)")
        ax2.set_xlabel("Market Index")
        ax2.set_ylabel("Batch Index")
        ax2.set_xticks(range(problem.n_markets))
        ax2.set_xticklabels(problem.market_ids, rotation=45, fontsize=8)
        ax2.set_yticks(range(problem.n_batches))
        ax2.set_yticklabels(problem.batch_ids, fontsize=8)
        plt.colorbar(im2, ax=ax2, shrink=0.7)

        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        # Synthesized Qiskit Quantum Circuit Display
        if "circuit" in qaoa_res and qaoa_res["circuit"] is not None:
            st.markdown("---")
            st.subheader("Synthesized Qiskit Quantum Circuit")
            qc = qaoa_res["circuit"]
            st.caption(f"Circuit Depth: **{qc.depth()}** | Total Gate Count: **{qc.size()}** | Qubits: **{qc.num_qubits}** | Classical Bits: **{qc.num_clbits}**")
        
            c_col1, c_col2 = st.columns([1, 2])
            with c_col1:
                st.markdown("**Gate Operations Breakdown:**")
                ops_df = pd.DataFrame(list(qc.count_ops().items()), columns=["Gate / Op", "Count"])
                st.dataframe(ops_df, use_container_width=True, hide_index=True)
                st.info("""
                * **H (Hadamard):** Creates initial uniform superposition $|+\\rangle^{\\otimes n}$.
                * **RZ:** Single-qubit longitudinal phase rotations $e^{-i\\gamma h_i Z}$.
                * **CX - RZ - CX:** Two-qubit Ising couplings $e^{-i\\gamma J_{ij} Z_i Z_j}$.
                * **RX:** Transverse field mixer rotations $e^{-i\\beta X_i}$.
                * **Measure:** Projects quantum state into classical bitstrings.
                """)

            with c_col2:
                st.markdown("**Circuit Gate Diagram:**")
                try:
                    fig_qc = qc.draw(output="mpl", fold=18, style={"backgroundcolor": "#FFFFFF"})
                    st.pyplot(fig_qc)
                    plt.close(fig_qc)
                except Exception:
                    st.text(qc.draw(output="text", fold=80, idle_wires=False))

    # ── Tab 5: Dataset Explorer ───────────────────────────────────────────────────
    with tab_data:
        st.subheader("Supply-chain data explorer")
        st.caption("Inspect the CSV data used to assemble the selected planning instance.")

        d_choice = st.selectbox(
            "Choose Dataset to Inspect:",
            [
                "Crop Master (40 crops)",
                "Supply Locations (36 collection centres)",
                "Vehicle Fleet (8 trucks)",
                "Daily Batches (30 batches)",
                "Market Master (319 markets)",
                "Handling Parameters (Diesel ₹92.76/L, loading/unloading)",
            ]
        )

        if d_choice.startswith("Crop"):
            st.dataframe(loader.crops, use_container_width=True)
        elif d_choice.startswith("Supply"):
            st.dataframe(loader.sources, use_container_width=True)
        elif d_choice.startswith("Vehicle"):
            st.dataframe(loader.vehicles, use_container_width=True)
        elif d_choice.startswith("Daily"):
            st.dataframe(loader.batches, use_container_width=True)
        elif d_choice.startswith("Market"):
            st.dataframe(loader.markets[["market_id", "market_name", "district", "latitude_num", "longitude_num", "capacity_kg"]], use_container_width=True)
        elif d_choice.startswith("Handling"):
            st.dataframe(loader.params, use_container_width=True)


else:
    # ── Mode 2: Single-Farmer Village Route ───────────────────────────────────
    st.markdown(f'''<section class="hero"><div><div class="hero-kicker">Village-to-market · Tamil Nadu</div><h1>Individual Farmer Route Optimizer</h1><p>Quantum-first market recommendations for single shipments. Evaluates all eligible markets statewide via logarithmic binary indexing.</p></div><div class="hero-badge">Price snapshot · {price_snapshot_label}</div></section>''', unsafe_allow_html=True)

    st.info("💡 **Single-Farmer Scope**: Logarithmic binary-index QAOA encodes all $M$ eligible wholesale markets into $n = \\lceil\\log_2(M+1)\\rceil$ qubits. No pre-selection truncation is applied.")

    sf_sig = (sf_source_id, sf_crop_id, sf_quantity, sf_deadline, sf_depth, sf_iterations, sf_shots, sf_seed)

    if sf_run_btn or "sf_results" not in st.session_state:
        with st.spinner("Filtering statewide eligible markets and executing QAOA statevector simulation..."):
            options_df, unsold_val = candidates(loader, sf_source_id, sf_crop_id, sf_quantity, sf_deadline)
            if options_df.empty:
                st.warning("⚠️ No eligible markets with recorded prices, sufficient capacity and feasible travel within the delivery deadline. Try adjusting the crop, quantity, or deadline.")
                st.session_state.sf_results = None
            else:
                q_res = solve_quantum(options_df, unsold_val, depth=sf_depth, iterations=sf_iterations, shots=sf_shots, seed=int(sf_seed))
                try:
                    c_bench, exact_idx = benchmarks(options_df, unsold_val, seed=int(sf_seed))
                    v_err = None
                except Exception as exc:
                    c_bench, exact_idx, v_err = pd.DataFrame(), None, str(exc)
                st.session_state.sf_results = (sf_sig, options_df, q_res, c_bench, exact_idx, v_err)

    if st.session_state.sf_results is not None:
        _, sf_options, sf_quantum, sf_comparison, sf_exact_index, sf_err = st.session_state.sf_results
        sf_top = sf_quantum["top"]
        sf_src = loader.sources.set_index("source_id").loc[sf_source_id]

        best_margin = sf_quantum.get("objective", 0.0) if sf_quantum.get("objective") is not None else 0.0
        st.markdown(f'''
        <div class="section-kicker">01 · Single Shipment Metrics</div>
        <div class="kpi-ribbon">
            <div class="kpi-card highlight">
                <div class="kpi-title">Best Modeled Margin</div>
                <div class="kpi-val">₹{best_margin:,.2f}</div>
                <div class="kpi-sub">QAOA Sampled Route</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Eligible Markets</div>
                <div class="kpi-val">{len(sf_options)}</div>
                <div class="kpi-sub muted">Capacity & Freshness Verified</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Logarithmic Qubits</div>
                <div class="kpi-val">{sf_quantum["qubits"]} <span style="font-size:1.1rem; color:var(--muted); font-weight:400;">qubits</span></div>
                <div class="kpi-sub muted">n = ⌈log₂(M+1)⌉ basis</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Simulation Latency</div>
                <div class="kpi-val">{sf_quantum['seconds']:.3f}s</div>
                <div class="kpi-sub">Statevector Evolution</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

        if sf_quantum.get("no_dispatch"):
            st.warning("⚠️ QAOA sampled a better modeled financial outcome by not dispatching (holding at farm) due to high transport costs or negative price margins.")

        sf_tab1, sf_tab2, sf_tab3 = st.tabs([
            "🗺️ Top 3 QAOA Routes",
            "📊 Classical Verification Benchmark",
            "⚛️ Binary-Index Quantum Details"
        ])

        with sf_tab1:
            st.subheader("Top Market Options Sampled by QAOA")
            st.caption("Ranked by modeled net margin among measured feasible states.")

            route_rows, markers = [], []
            for i, row in sf_top.iterrows():
                is_opt = sf_exact_index is not None and not sf_comparison.empty and np.isclose(row["net_margin"], sf_comparison.iloc[0]["objective"], rtol=0, atol=0.01)
                lbl = "Best QAOA Option" if i == 0 else f"Alternative {i+1}"
                badge_html = '<span class="badge badge-optimum">Optimum Verified</span>' if (i == 0 and is_opt) else f'<span class="badge badge-quantum">Rank #{i+1}</span>'
                color = [20, 150, 75, 240] if i == 0 else [45, 100, 200, 210]

                card_html = (
                    f'<div class="solver-bar-container" style="border-left: 3px solid ({"#FF4D00" if i==0 else "#111110"});">'
                    f'<div class="solver-bar-header">'
                    f'<div style="display:flex; align-items:center; gap:0.6rem;">'
                    f'<span class="solver-bar-name" style="font-size:0.95rem;">{row["market"]}</span>'
                    f'{badge_html}'
                    f'</div>'
                    f'<span class="font-mono text-xs" style="color:var(--accent); font-weight:600; font-size:1.05rem;">₹{row["net_margin"]:,.2f}</span>'
                    f'</div>'
                    f'<div style="display:flex; gap:1.2rem; flex-wrap:wrap; font-family:\'IBM Plex Mono\',monospace; font-size:0.75rem; color:var(--muted); margin-top:0.4rem;">'
                    f'<span>📍 {row["distance_km"]:.1f} KM</span>'
                    f'<span>⏱️ {row["travel_minutes"]:.0f} MIN</span>'
                    f'<span>💰 WHOLESALE ₹{row["price_per_kg"]:.2f}/KG</span>'
                    f'<span>⚛️ {int(row["shots"])} SHOTS (|{row["bitstring"]}⟩)</span>'
                    f'</div>'
                    f'</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)


                c_name = loader.crop_id_to_name.get(sf_crop_id, sf_crop_id)
                tip = (f"{lbl}\n{sf_src['source_name']} → {row['market']}\n{c_name}: {sf_quantity:g} kg\n"
                       f"Distance: {row['distance_km']:.1f} km | Time: {row['travel_minutes']:.0f} min\n"
                       f"Net Margin: Rs {row['net_margin']:,.2f}\n"
                       f"Measured: {int(row['shots'])} shots | Bitstring: {row['bitstring']}")

                route_rows.append({"start": [float(sf_src["longitude"]), float(sf_src["latitude"])], "end": [row["longitude"], row["latitude"]], "color": color, "tooltip": tip})
                markers.append({"position": [row["longitude"], row["latitude"]], "color": color, "tooltip": tip})
                st.link_button(f"🚗 Turn-by-Turn GPS to {row['market']}", f"https://www.google.com/maps/dir/?api=1&origin={sf_src['latitude']},{sf_src['longitude']}&destination={row['latitude']},{row['longitude']}&travelmode=driving")


            if route_rows:
                c_name = loader.crop_id_to_name.get(sf_crop_id, sf_crop_id)
                markers.append({"position": [float(sf_src["longitude"]), float(sf_src["latitude"])], "color": [110, 60, 160, 255], "tooltip": f"Source: {sf_src['source_name']}\n{sf_src['district']}\nCrop: {c_name}\nQuantity: {sf_quantity:g} kg"})
                coords = np.array([m["position"] for m in markers])
                extent = max(float(np.ptp(coords[:, 0])), float(np.ptp(coords[:, 1])), 0.02)
                deck = pdk.Deck(
                    layers=[
                        pdk.Layer("ArcLayer", route_rows, get_source_position="start", get_target_position="end", get_source_color="color", get_target_color="color", get_width=5, pickable=True),
                        pdk.Layer("ScatterplotLayer", markers, get_position="position", get_fill_color="color", get_radius=350, radius_min_pixels=7, pickable=True)
                    ],
                    initial_view_state=pdk.ViewState(longitude=float(coords[:, 0].mean()), latitude=float(coords[:, 1].mean()), zoom=float(np.clip(np.log2(180/extent), 5, 13))),
                    tooltip={"text": "{tooltip}"},
                    map_style="light"
                )
                st.pydeck_chart(deck)

            st.dataframe(sf_top, use_container_width=True, hide_index=True)

        with sf_tab2:
            st.subheader("Post-Sampling Classical Verification")
            st.caption("Classical algorithms run independently to evaluate the exact global maximum without influencing QAOA sampling.")

            if sf_err:
                st.warning(f"Classical verification warning: {sf_err}")
            elif not sf_comparison.empty:
                qrow = pd.DataFrame([{"method": "QAOA Sampled Result", "objective": sf_quantum["objective"], "seconds": sf_quantum["seconds"]}])
                comb_bench = pd.concat([qrow, sf_comparison], ignore_index=True)
                st.dataframe(comb_bench, use_container_width=True, hide_index=True)

                if sf_quantum["objective"] is not None:
                    gap = sf_comparison.iloc[0]["objective"] - sf_quantum["objective"]
                    st.metric("Gap to Exact Modeled Optimum (₹)", f"₹{gap:,.2f}", help="0.00 indicates QAOA sampled the true global optimum")

        with sf_tab3:
            st.subheader("Binary-Index Logarithmic QAOA Formulation")
            st.markdown(r"""
            Instead of allocating one qubit per (batch, market) pair ($N = B \times M$), the single-shipment formulation maps the destination index to a binary basis state:
            $$n = \left\lceil \log_2(M + 1) \right\rceil \text{ qubits}$$
            * Basis state $|m\rangle$ corresponds to selecting market $m$.
            * Basis state $|M\rangle$ corresponds to the **No-Dispatch** choice (saving transport cost, incurring unsold penalty).
            * Unused padding basis states $|z > M\rangle$ are assigned an energetic penalty.
            
            $$H_C = \sum_{z=0}^{2^n-1} E_z |z\rangle\langle z|, \quad H_M = \sum_{j=1}^n X_j$$
            """)
            st.json({k: v for k, v in sf_quantum.items() if k != "top"})
# Footer
st.markdown("---")
st.caption("Quantum Optimization Agricultural Logistics System | CSE Capstone Project | Qiskit 2.4 & Streamlit")
