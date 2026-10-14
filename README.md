# AgriQuantum: Quantum Optimization for Agricultural Supply Chain Logistics

A hybrid Classical-Quantum optimization platform designed for fresh produce distribution across Tamil Nadu, India.

---

## 📌 Project Overview
AgriQuantum solves agricultural dispatch and routing problems under perishability deadlines, market capacity constraints, and transport economics. It features two core optimization scopes:

1. **🚚 Multi-Batch Fleet Dispatch (Joint Portfolio Model)**
   - **Classical Exact**: Solved via MILP (HiGHS solver via PuLP/SciPy).
   - **Classical Heuristics**: Greedy sorting baseline and Simulated Annealing.
   - **Quantum Optimization**: Quadratic Unconstrained Binary Optimization (QUBO) mapped to an Ising Hamiltonian ($H_C$) solved using Qiskit QAOA ($p$-depth alternating cost and mixer unitaries).

2. **🌾 Single-Farmer Village Route (Logarithmic Binary Index QAOA)**
   - Uses logarithmic binary indexing ($n = \lceil\log_2(M + 1)\rceil$ qubits) to evaluate all candidate wholesale markets statewide without truncation.
   - Outputs top 3 ranked routes with turn-by-turn navigation deep-links and simulated gate counts.

---

## 🚀 Quick Start Guide

### 1. Requirements & Environment
Python 3.10+ is recommended. Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Launch the Interactive Dashboard
To launch the Streamlit frontend:
```bash
streamlit run app.py
```

### 3. Run Headless Benchmarks & Optimization
To run the end-to-end command line solver comparison and generate plots:
```bash
python main.py
```

### 4. Run Unit Tests
```bash
python -m unittest test_farm_planning.py test_quantum_routes.py
```

### 5. Generate Presentation Slides
To build the PowerPoint slide deck (`AgriQuantum_Capstone_Presentation.pptx`):
```bash
python generate_ppt.py
```

---

## 📂 Project Directory Structure

```text
capstone2/
├── .streamlit/
│   └── config.toml          # Custom theme settings (InspoAI Swiss-Mono styling)
├── data/                    # Tamil Nadu supply chain datasets
│   ├── crop_master.csv
│   ├── daily_batches.csv
│   ├── handling_parameters.csv
│   ├── market_crop_eligibility.csv
│   ├── market_master_model_ready.csv
│   ├── supply_locations.csv
│   ├── travel_distance_time_matrix.csv
│   ├── uzhavar_daily_prices_*.csv
│   └── vehicle_fleet.csv
├── inspo_design/            # UI design templates & HTML prototypes
├── output/                  # Generated benchmark charts, circuits & reports
│   └── ... (.png, .csv)
├── app.py                   # Streamlit web application
├── main.py                  # CLI pipeline and benchmark runner
├── problem_builder.py       # QUBO / MILP mathematical problem formulation
├── quantum_optimizer.py     # Multi-batch solvers (MILP, Greedy, Annealing, QAOA)
├── quantum_routes.py        # Single-farmer logarithmic binary-index QAOA solver
├── farm_planning.py         # Classical baseline farm planning algorithms
├── visualizer.py            # Matplotlib / visual chart generators
├── data_loader.py           # Dataset loading and validation utility
├── test_farm_planning.py    # Unit tests for farm planning
├── test_quantum_routes.py   # Unit tests for logarithmic QAOA
├── generate_ppt.py          # Automated PPTX slide generator
├── requirements.txt         # Dependency specifications
└── README.md                # Project documentation
```

---

## 🔬 Mathematical Formulation
- **QUBO Mapping**: Binary variables $x_{b,m} \in \{0, 1\}$ represent dispatching batch $b$ to market $m$.
- **Ising Hamiltonian**: Mapped via spin operator substitution $x_i = \frac{I - Z_i}{2}$:
  $$H_C = \sum_{i} h_i Z_i + \sum_{i < j} J_{ij} Z_i Z_j$$
- **QAOA State Preparation**:
  $$|\gamma, \beta\rangle = \prod_{k=1}^p e^{-i\beta_k H_M} e^{-i\gamma_k H_C} |+\rangle^{\otimes n}$$
