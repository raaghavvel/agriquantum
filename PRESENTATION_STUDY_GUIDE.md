# AGRIQUANTUM: COMPREHENSIVE PRESENTATION & TECHNICAL STUDY BRIEF
## Department of Computer Science & Engineering | 5th Semester Quantum Computing Capstone
**Project Title**: AgriQuantum — Quantum Optimization-Based Agricultural Supply Chain Management System  
**Region & Testbed**: Tamil Nadu Farm-to-Market Logistics (Uzhavar Santhais & Regulated Markets)  
**Primary Tech Stack**: Python 3.12, Qiskit 2.4, SciPy (HiGHS MILP), Streamlit, PyDeck 3D, Pandas, NumPy  

---

# 1. EXECUTIVE SUMMARY & ELEVATOR PITCH

### What is the project?
AgriQuantum is a hybrid Classical-Quantum optimization platform that solves the daily agricultural dispatch and route recommendation challenge for fresh, perishable produce across Tamil Nadu.

### Why does it matter?
1. **Perishability & Food Waste**: High-spoilage crops (tomatoes, onions, greens) spoil quickly if transit takes too long or arrives past freshness deadlines.
2. **Suboptimal Farmer Income**: Without coordinated allocation, farmers dump produce at nearby saturated local markets at low prices rather than distant high-demand wholesale centres.
3. **High Logistics Costs**: Fragmented transportation creates empty return trips, high diesel consumption, and market bottleneck congestion.
4. **Computational Complexity**: Assigning $B$ harvest batches across $M$ candidate wholesale markets is an **NP-hard combinatorial optimization problem** with a worst-case search space of $\mathcal{O}(M^B)$. Classical exact solvers experience exponential runtime scaling as the supply chain grows state-wide.

### What is the Quantum solution?
We formulate the supply chain allocation into a **Quadratic Unconstrained Binary Optimization (QUBO)** model, map it via spin transformation $x_i = \frac{I - Z_i}{2}$ to an **Ising Hamiltonian** ($H_C$), and solve it using the **Quantum Approximate Optimization Algorithm (QAOA)** with Qiskit 2.4 on parameterizable quantum circuits. We benchmark QAOA head-to-head against classical exact Mixed-Integer Linear Programming (HiGHS Branch-and-Cut), Simulated Annealing, and Greedy heuristics.

---

# 2. TWO OPERATIONAL MODES EXPLAINED

The platform solves agricultural logistics at two complementary tiers:

### Mode 1: 🚚 Multi-Batch Fleet Dispatch (Joint Portfolio Model)
- **Scope**: Cooperative multi-truck fleet dispatch coordinating multiple farm harvest batches across multiple municipal markets simultaneously.
- **Formulation**: QUBO with pairwise quadratic constraint penalties (Zero-Slack formulation).
- **Qubit Mapping**: $N = B \times M$ decision variables, one qubit per (batch, market) assignment pair.
- **Solvers Benchmarked**:
  1. **Classical Exact MILP** (HiGHS Branch-and-Cut via SciPy): Provable ground-truth global optimum ($100\%$ baseline).
  2. **Classical Greedy Heuristic**: Fast $\mathcal{O}(N \log N)$ margin-per-kg greedy sorting.
  3. **Simulated Annealing**: Stochastic thermal exploration over the binary QUBO matrix (500–1000 sweeps).
  4. **Quantum QAOA** (Qiskit 2.4): Parameterized circuit with depth $p$, variational COBYLA parameter optimizer, and statevector sampling.

### Mode 2: 🌾 Single-Farmer Village Route (Logarithmic Binary Index QAOA)
- **Scope**: Tailored for an individual farmer at a specific rural collection centre with a single crop batch (e.g., 100 kg of tomatoes).
- **Problem**: Which top 3 wholesale markets across the entire state yield the highest profit while meeting delivery deadlines?
- **Logarithmic Qubit Innovation**:
  Instead of allocating $M$ qubits for $M$ markets (which would exceed simulator and NISQ capacity for 300+ markets), it maps candidate destination indices into binary basis states:
  $$n = \left\lceil \log_2(M + 1) \right\rceil \text{ qubits}$$
  - Basis state $|m\rangle$ corresponds to market $m$.
  - Basis state $|M\rangle$ corresponds to the **No-Dispatch** choice (holding crop at farm to save transport loss).
  - Out-of-bounds states ($|z > M\rangle$) receive an energetic penalty.
- **Benefit**: Evaluates all statewide eligible markets (e.g., 200+ markets with just 8 qubits) without arbitrary geographical pre-truncation.

---

# 3. MATHEMATICAL & QUANTUM FORMULATION (DEEP DIVE)

### 3.1 Objective Function: Net Farm Profit
The goal is to maximize the total net financial return:
$$\text{Net Profit} = \sum_{b, m} \Big( \text{Revenue}_{b, m} - \text{Transport Cost}_{b, m} - \text{Late Penalty}_{b, m} + \text{Unsold Produce Saved}_b \Big) x_{b, m}$$

Where:
- $\text{Revenue}_{b, m} = \text{Price}_{m, \text{crop}} \times \text{Quantity}_b$
- $\text{Transport Cost}_{b, m} = \text{Fuel Rate} \times \text{Distance}_{b, m} + \text{Handling Fee}$
- $\text{Late Penalty}_{b, m} = \text{Penalty Rate} \times \max(0, \text{Transit Time}_{b, m} - \text{Shelf Life Deadline}_b)$

### 3.2 QUBO Construction (Minimization)
Since quantum annealing and QAOA minimize energy, we define the cost matrix:
$$c_i = -\frac{\text{Profit Gain}_i}{\text{Scale Factor}}$$
$$\min_{x \in \{0, 1\}^N} E(x) = \sum_{i=1}^N c_i x_i + \sum_{i < j} Q_{ij} x_i x_j$$

### 3.3 Zero-Slack Quadratic Constraints (No Auxiliary Qubits)
Traditional QUBO converts inequalities ($\sum x_i \le C$) into equalities using slack variables, requiring extra slack qubits ($+5$ to $+15$ qubits per constraint), which blows up circuit registers. **AgriQuantum eliminates all slack qubits:**

1. **Batch Exclusivity Constraint (At most 1 market per batch)**:
   $$P_{\text{batch}} \sum_{i < j, \text{ same } b} x_i x_j$$
   *If $x_i = 1$ and $x_j = 1$ for the same batch, a heavy quadratic penalty $P_{\text{batch}}$ is incurred.*
2. **Pairwise Market Capacity Constraints**:
   $$P_{\text{cap}} \sum_{u < v, \text{ same } m} \mathbb{I}(q_u + q_v > \text{Capacity}_m) \cdot x_u x_v$$
   *Pre-computed conflict graph: If batches $u$ and $v$ together exceed market $m$'s throughput, quadratic penalty $Q_{uv}$ activates.*

### 3.4 Mapping QUBO to Ising Spin Hamiltonian
Using the canonical spin transformation $x_i = \frac{I - Z_i}{2}$ (where $Z_i$ is the Pauli-$Z$ operator with eigenvalues $\pm 1$):
- $x_i = 0 \implies Z_i = +1$ (Spin Up / No dispatch)
- $x_i = 1 \implies Z_i = -1$ (Spin Down / Dispatched)

Substituting into QUBO yields the **Cost Hamiltonian**:
$$H_C = \sum_{i=1}^N h_i Z_i + \sum_{i < j} J_{ij} Z_i Z_j + \text{Offset}$$
Where:
- Longitudinal magnetic field: $h_i = -\frac{c_i}{2} - \sum_{j \ne i} \frac{Q_{ij}}{4}$
- Two-qubit Ising coupling: $J_{ij} = \frac{Q_{ij}}{4}$

### 3.5 QAOA Circuit Architecture & Unitaries
QAOA alternates two quantum operators over depth $p$:
$$|\gamma, \beta\rangle = \prod_{k=1}^p U(B, \beta_k) U(C, \gamma_k) |+\rangle^{\otimes n}$$

1. **Initial State Superposition**:
   $$|+\rangle^{\otimes n} = H^{\otimes n} |0\rangle^{\otimes n} = \frac{1}{\sqrt{2^n}} \sum_{z \in \{0, 1\}^n} |z\rangle$$
2. **Cost Unitary $U(C, \gamma_k) = e^{-i \gamma_k H_C}$**:
   - Single-qubit phase rotation: $R_Z(2 \gamma_k h_i)$ on qubit $i$.
   - Two-qubit interaction: $CX(i, j) \to R_Z(2 \gamma_k J_{ij}) \to CX(i, j)$.
3. **Mixer Unitary $U(B, \beta_k) = e^{-i \beta_k H_M}$** (Transverse Mixer):
   $$H_M = \sum_{i=1}^n X_i \implies U(B, \beta_k) = \bigotimes_{i=1}^n R_X(2 \beta_k)$$
   Provides quantum tunneling across local energetic barriers.
4. **Classical Parameter Tuning (COBYLA)**:
   The classical optimizer iteratively updates $(\vec{\gamma}, \vec{\beta})$ to minimize $\langle \psi(\gamma, \beta) | H_C | \psi(\gamma, \beta) \rangle$.

---

# 4. BENCHMARK RESULTS & KEY EXPERIMENTAL FINDINGS

Tested on actual Tamil Nadu agricultural datasets (Coimbatore, Salem, Dharmapuri, Tiruchirappalli, Madurai, Tirunelveli, Erode, Dindigul, Theni):

| Scenario | Decision Vars / Qubits | Classical Exact (MILP) | Classical Greedy | Simulated Annealing | Quantum QAOA ($p=1$) |
|---|---|---|---|---|---|
| **Scenario 1 (3 Batches $\times$ 3 Markets)** | 9 vars, 9 qubits | ₹194,289.10 (0.005s) | ₹194,289.10 (0.0001s) | ₹188,322.72 (96.9%, 0.006s) | **₹194,289.10 (100.0%, 0.050s)** |
| **Scenario 2 (4 Batches $\times$ 4 Markets)** | 16 vars, 10 active qubits | ₹330,067.10 (0.015s) | ₹330,067.10 (0.0002s) | ₹318,400.00 (96.5%, 0.008s) | **₹315,542.44 (95.6%, 0.058s)** |

### Key Takeaways for the Presentation:
1. **Approximation Ratio**: QAOA achieves **95.6% to 100.0%** of the provable global optimum.
2. **Feasibility Guarantee**: Independent capacity validation confirms **zero market throughput violations** across all plans.
3. **Zero Spoilage**: Every route chosen satisfies the perishable harvest shelf-life deadline.
4. **Attribution Transparency**: Honest scientific reporting distinguishes pure QAOA states from hybrid classical backfill.

---

# 5. STEP-BY-STEP PRESENTATION SLIDE GUIDE (10 SLIDES)

When presenting, use this structured progression:

- **Slide 1: Title & Team Credentials**
  - Project Title, Course (Quantum Computing 5th Sem Capstone), Tech stack (Qiskit 2.4, SciPy, Streamlit).
- **Slide 2: Problem Statement**
  - Why agricultural dispatch? Spoilage losses, market price volatility, fuel overhead, exponential $\mathcal{O}(M^B)$ NP-hard complexity.
- **Slide 3: Project Objectives & Technical Approach**
  - Three pillars: (1) Mathematical QUBO mapping, (2) Qiskit QAOA execution, (3) Rigorous classical benchmarking against MILP.
- **Slide 4: Proposed Algorithm — Principle & Math Formulation**
  - QAOA concept: alternating Cost and Mixer Hamiltonians. Zero-slack penalty formulation, mapping $x_i = \frac{I - Z_i}{2}$ to Ising $h_i Z_i + J_{ij} Z_i Z_j$.
- **Slide 5: Execution Workflow & Pseudocode**
  - Flow: Superposition $\to$ Cost Unitary $\to$ Mixer Unitary $\to$ Energy expectation $\to$ COBYLA parameter loop $\to$ 2048-shot measurement.
- **Slide 6: Hardware Scaling & Circuit Complexity Analysis**
  - Asymptotic complexity: $\mathcal{O}(p \cdot N^2)$ gate depth. Gate counts for 9 qubits: 9 Hadamard, 27 $R_Z$, 36 $CX$, 9 $R_X$.
- **Slide 7: System Implementation & Architecture**
  - Modular pipeline: `data_loader` $\to$ `problem_builder` $\to$ `quantum_optimizer` $\to$ `visualizer` $\to$ `app.py`.
- **Slide 8: Experimental Results & Comparative Analysis**
  - Multi-solver table comparing MILP (100%), QAOA (95.6%–100%), Annealing (96.9%), and Greedy.
- **Slide 9: Project Conclusion & Scientific Takeaways**
  - Demonstrates feasibility of quadratic penalty optimization without slack qubits; statevector simulation shows why physical QPUs will provide future speedup.
- **Slide 10: Live Demonstration & Q&A**
  - Streamlit UI features: InspoAI Swiss-Mono dashboard, 3D PyDeck road transit arcs, dual mode toggle, gate decomposition charts.

---

# 6. ANTICIPATED VIVA / JURY QUESTIONS & MODEL ANSWERS

### Q1: Why use QAOA when Classical MILP runs in 0.005 seconds?
**Answer**: "On small benchmark instances (e.g., 9 to 16 variables), classical MILP is faster because classical CPUs operate at gigahertz frequencies. However, classical MILP scales exponentially in the worst case $\mathcal{O}(M^B)$. QAOA's value is foundational: it maps the combinatorial problem to quantum state evolution. As NISQ and fault-tolerant quantum hardware scale with error mitigation, QAOA polynomial circuit depth $\mathcal{O}(p \cdot N^2)$ offers quantum speedup potential over classical exponential search."

### Q2: What is the significance of eliminating slack qubits in your QUBO?
**Answer**: "Standard QUBO models inequality constraints ($\sum q_i x_i \le C$) using binary expansion slack variables ($\sum 2^k s_k$). This requires 5 to 15 auxiliary slack qubits per market constraint, easily demanding 60+ qubits for a 4-market problem. Our Zero-Slack formulation uses pairwise quadratic penalty terms $Q_{uv} = P_{\text{hard}} \cdot \mathbb{I}(q_u + q_v > C)$ between conflicting batch pairs. This strictly enforces capacity limits with **zero auxiliary qubits**, keeping the qubit count at exactly $N = B \times M$."

### Q3: How does the Single-Farmer Logarithmic mode differ from the Multi-Batch mode?
**Answer**: "Multi-batch uses a 1-qubit-per-pair binary assignment ($N = B \times M$). If we tested 200 markets, it would require 200 qubits, impossible for statevector simulation. The single-farmer mode maps the destination market index directly into binary basis states using logarithmic indexing: $n = \lceil \log_2(M + 1) \rceil$. For 200 markets, it requires only 8 qubits ($\lceil \log_2(201) \rceil = 8$). It tests all statewide markets simultaneously without any truncation."

### Q4: How is QAOA parameterized and trained?
**Answer**: "QAOA is a hybrid variational algorithm. The quantum circuit prepares the state $|\gamma, \beta\rangle$ using $p$ layers of cost rotations $\gamma_k$ and mixer rotations $\beta_k$. The classical computer evaluates the expectation value $\langle H_C \rangle$ and uses the COBYLA (Constrained Optimization BY Linear Approximation) derivative-free optimizer to update the angles $(\vec{\gamma}, \vec{\beta})$ until energy convergence."

### Q5: What datasets did you use?
**Answer**: "We compiled 9 integrated datasets from Tamil Nadu:
1. `crop_master.csv`: 40 crops with shelf-life and perishability flags.
2. `supply_locations.csv`: 36 rural village collection centres across 9 districts.
3. `market_master_model_ready.csv`: 319 wholesale markets and Uzhavar Santhais with throughput capacities.
4. `uzhavar_daily_prices_*.csv`: Daily market prices across commodities.
5. `travel_distance_time_matrix.csv`: 124,000+ precomputed road distance and transit time pairs.
6. `vehicle_fleet.csv` & `handling_parameters.csv`: Fuel rates (₹92.76/L), vehicle payload capacities, and labor handling fees."

---

# 7. HOW TO RUN THE PROJECT (QUICK INSTRUCTIONS)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the interactive Streamlit dashboard
streamlit run app.py

# 3. Run command-line multi-solver benchmarks & generate plots
python main.py

# 4. Run automated test suite
python -m unittest test_farm_planning.py test_quantum_routes.py

# 5. Re-generate PowerPoint presentation
python generate_ppt.py
```
