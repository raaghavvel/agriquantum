import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    # 16:9 widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette
    DARK_BG = RGBColor(15, 23, 42)      # #0F172A (Deep Slate/Navy)
    LIGHT_BG = RGBColor(248, 250, 252)  # #F8FAFC (Soft Off-White)
    CARD_BG = RGBColor(255, 255, 255)   # #FFFFFF
    CARD_BORDER = RGBColor(226, 232, 240)# #E2E8F0
    TEXT_MAIN = RGBColor(15, 23, 42)    # #0F172A
    TEXT_MUTED = RGBColor(71, 85, 105)  # #475569
    ACCENT_TEAL = RGBColor(13, 148, 136)# #0D9488 (Teal/Emerald)
    ACCENT_BLUE = RGBColor(2, 132, 199) # #0284C7 (Quantum Cyan/Blue)
    ACCENT_PURPLE = RGBColor(124, 58, 237) # #7C3AED
    WHITE = RGBColor(255, 255, 255)

    def add_header(slide, title_text, category_text="QUANTUM COMPUTING CAPSTONE"):
        # Header banner
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_TEAL
        p_cat.font.name = "Arial"

        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_MAIN
        p_title.font.name = "Arial"

    def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
        return shape

    # =========================================================================
    # SLIDE 1: Title Slide (Dark Theme)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = DARK_BG
    bg1.line.fill.background()

    # Title & Subtitle
    t_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.333), Inches(2.5))
    tf1 = t_box.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "QUANTUM COMPUTING CAPSTONE PROJECT"
    p0.font.size = Pt(14)
    p0.font.bold = True
    p0.font.color.rgb = ACCENT_TEAL
    p0.font.name = "Arial"
    p0.space_after = Pt(10)

    p1 = tf1.add_paragraph()
    p1.text = "AgriQuantum: Quantum Optimization-Based\nAgricultural Supply Chain Allocation"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    p1.font.name = "Arial"
    p1.space_after = Pt(14)

    p2 = tf1.add_paragraph()
    p2.text = "A Zero-Slack QUBO & QAOA Approach for Capacitated Farm-to-Market Dispatch in Tamil Nadu"
    p2.font.size = Pt(16)
    p2.font.color.rgb = RGBColor(148, 163, 184)
    p2.font.name = "Arial"

    # Team Members Card
    c1 = add_card(s1, Inches(1.0), Inches(4.5), Inches(5.4), Inches(2.0), RGBColor(30, 41, 59), RGBColor(51, 65, 85))
    c1_box = s1.shapes.add_textbox(Inches(1.2), Inches(4.6), Inches(5.0), Inches(1.8))
    tf_c1 = c1_box.text_frame
    p_mem_head = tf_c1.paragraphs[0]
    p_mem_head.text = "PROJECT TEAM MEMBERS"
    p_mem_head.font.size = Pt(11)
    p_mem_head.font.bold = True
    p_mem_head.font.color.rgb = ACCENT_TEAL
    p_mem_head.space_after = Pt(8)

    p_m1 = tf_c1.add_paragraph()
    p_m1.text = "1. Raaghav vel P"
    p_m1.font.size = Pt(15)
    p_m1.font.bold = True
    p_m1.font.color.rgb = WHITE
    p_r1 = tf_c1.add_paragraph()
    p_r1.text = "    Roll Number: CH.SC.u4cse24155"
    p_r1.font.size = Pt(13)
    p_r1.font.color.rgb = RGBColor(203, 213, 225)
    p_r1.space_after = Pt(6)

    p_m2 = tf_c1.add_paragraph()
    p_m2.text = "2. Srinivas R"
    p_m2.font.size = Pt(15)
    p_m2.font.bold = True
    p_m2.font.color.rgb = WHITE
    p_r2 = tf_c1.add_paragraph()
    p_r2.text = "    Roll Number: CH.SC.U4CSE24146"
    p_r2.font.size = Pt(13)
    p_r2.font.color.rgb = RGBColor(203, 213, 225)

    # Institution Card
    c2 = add_card(s1, Inches(6.8), Inches(4.5), Inches(5.5), Inches(2.0), RGBColor(30, 41, 59), RGBColor(51, 65, 85))
    c2_box = s1.shapes.add_textbox(Inches(7.0), Inches(4.6), Inches(5.1), Inches(1.8))
    tf_c2 = c2_box.text_frame
    p_inst_head = tf_c2.paragraphs[0]
    p_inst_head.text = "ACADEMIC DETAILS"
    p_inst_head.font.size = Pt(11)
    p_inst_head.font.bold = True
    p_inst_head.font.color.rgb = ACCENT_BLUE
    p_inst_head.space_after = Pt(8)

    p_d1 = tf_c2.add_paragraph()
    p_d1.text = "Department of Computer Science & Engineering"
    p_d1.font.size = Pt(14)
    p_d1.font.bold = True
    p_d1.font.color.rgb = WHITE
    p_d2 = tf_c2.add_paragraph()
    p_d2.text = "Course: Quantum Computing (5th Semester Capstone)"
    p_d2.font.size = Pt(13)
    p_d2.font.color.rgb = RGBColor(203, 213, 225)
    p_d3 = tf_c2.add_paragraph()
    p_d3.text = "Framework: Qiskit 2.4 & Hybrid Classical-Quantum Architecture"
    p_d3.font.size = Pt(13)
    p_d3.font.color.rgb = RGBColor(203, 213, 225)

    # =========================================================================
    # SLIDE 2: Problem Statement
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Problem Statement: Agricultural Dispatch Optimization")

    col_w = Inches(3.7)
    card_h = Inches(5.4)

    # Col 1: What is the problem?
    add_card(s2, Inches(0.8), Inches(1.6), col_w, card_h)
    tb = s2.shapes.add_textbox(Inches(1.0), Inches(1.8), col_w - Inches(0.4), card_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "WHAT IS THE PROBLEM?"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_TEAL
    p.space_after = Pt(12)

    bullets1 = [
        "Daily Farm-to-Market Dispatch: Allocating freshly harvested batches from rural collection centres to wholesale markets across Tamil Nadu.",
        "Multiple Competing Factors: Dynamic market prices, perishable crop shelf-life deadlines, transport freight costs, and market throughput limits.",
        "Operational Constraints: Each batch can go to at most 1 market, and aggregate shipment weight must never exceed destination capacity."
    ]
    for b in bullets1:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(12.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(10)

    # Col 2: Why solve it?
    add_card(s2, Inches(4.8), Inches(1.6), col_w, card_h)
    tb = s2.shapes.add_textbox(Inches(5.0), Inches(1.8), col_w - Inches(0.4), card_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "WHY MUST IT BE SOLVED?"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(12)

    bullets2 = [
        "Heavy Post-Harvest Losses: Perishable crops (tomatoes, onions) rot if transit times violate freshness deadlines.",
        "Suboptimal Farmer Returns: Produce is frequently dumped at nearby saturated markets at rock-bottom prices instead of high-demand markets.",
        "High Fuel & Freight Costs: Uncoordinated dispatch routes result in empty return trips and excessive diesel consumption.",
        "Market Bottlenecks: Overloading Uzhavar Santhai stalls leads to severe municipal logistics chaos."
    ]
    for b in bullets2:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(12.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(10)

    # Col 3: Significance
    add_card(s2, Inches(8.8), Inches(1.6), col_w, card_h)
    tb = s2.shapes.add_textbox(Inches(9.0), Inches(1.8), col_w - Inches(0.4), card_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "SIGNIFICANCE OF THE SOLUTION"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_PURPLE
    p.space_after = Pt(12)

    bullets3 = [
        "NP-Hard Combinatorial Problem: Assigning B batches to M candidate markets has a search space of O(M^B).",
        "Exponential Scaling: Classical Branch-and-Cut exact solvers scale exponentially as supply networks expand state-wide.",
        "Quantum Computing Value: Quadratic Unconstrained Binary Optimization (QUBO) maps directly to physical quantum spin systems.",
        "Real-World Impact: Maximizes net farmer profit, guarantees zero food spoilage, and enforces strict market capacity compliance."
    ]
    for b in bullets3:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(12.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(10)

    # =========================================================================
    # SLIDE 3: Objectives
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Project Objectives & Technical Approach")

    # 3 Horizontal Cards
    card_h = Inches(1.6)
    w_full = Inches(11.7)

    # Obj 1
    add_card(s3, Inches(0.8), Inches(1.6), w_full, card_h)
    tb = s3.shapes.add_textbox(Inches(1.1), Inches(1.75), w_full - Inches(0.6), card_h - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. HOW WE PLAN TO SOLVE THE PROBLEM (Mathematical QUBO Formulation)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_TEAL
    p.space_after = Pt(6)
    p2 = tf.add_paragraph()
    p2.text = "Model the agricultural dispatch challenge as a Quadratic Unconstrained Binary Optimization (QUBO) problem. Objective maximizes Net Profit = (Revenue - Transport Cost - Lateness Penalty + Unsold Produce Saved). Pairwise quadratic penalty terms bake batch exclusivity and market capacity limits into the objective function without auxiliary slack qubits."
    p2.font.size = Pt(12.5)
    p2.font.color.rgb = TEXT_MUTED

    # Obj 2
    add_card(s3, Inches(0.8), Inches(3.4), w_full, card_h)
    tb = s3.shapes.add_textbox(Inches(1.1), Inches(3.55), w_full - Inches(0.6), card_h - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "2. THE APPROACH WE ARE FOLLOWING (Rigorous Ising Hamiltonian Mapping & Pruning)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(6)
    p2 = tf.add_paragraph()
    p2.text = "Apply a static pre-solve pruning filter to drop provably infeasible batch-market pairs (violating shelf-life deadlines or crop eligibility). Transform binary decision variables x_i in {0, 1} to Pauli-Z spin operators Z_i in {+1, -1} via x_i = (I - Z_i)/2, deriving exact longitudinal fields h_i and two-qubit Ising couplings J_ij with verified mathematical equivalence."
    p2.font.size = Pt(12.5)
    p2.font.color.rgb = TEXT_MUTED

    # Obj 3
    add_card(s3, Inches(0.8), Inches(5.2), w_full, card_h)
    tb = s3.shapes.add_textbox(Inches(1.1), Inches(5.35), w_full - Inches(0.6), card_h - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "3. THE QUANTUM ALGORITHM USED (Multi-Layer Parameterized QAOA Benchmark)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_PURPLE
    p.space_after = Pt(6)
    p2 = tf.add_paragraph()
    p2.text = "Implement the Quantum Approximate Optimization Algorithm (QAOA) with circuit depth p. Initialize angles with a greedy warm-start bias, evolve the statevector via vectorized butterfly operations, draw 2,048 quantum measurement shots, and benchmark against Classical Exact (HiGHS MILP Branch-and-Cut), Greedy Heuristic, and Simulated Annealing."
    p2.font.size = Pt(12.5)
    p2.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 4: Proposed Algorithm (Part 1 - Concept & Hamiltonian Formulation)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Proposed Algorithm: Quantum Approximate Optimization Algorithm (QAOA)", "ALGORITHM SPECIFICATION — PART 1")

    # Left Column: Overview & Theory
    add_card(s4, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.4))
    tb = s4.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(5.0))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "ALGORITHM OVERVIEW & PRINCIPLE"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_TEAL
    p.space_after = Pt(10)

    overview_bullets = [
        "Algorithm Name: Quantum Approximate Optimization Algorithm (QAOA)",
        "Class: Hybrid Quantum-Classical Variational Algorithm designed for NISQ hardware.",
        "Operating Principle: QAOA prepares a parameterized quantum state |psi(gamma, beta)> by alternating between a problem Cost Hamiltonian U(C, gamma) and a Mixer Hamiltonian U(B, beta).",
        "Cost Hamiltonian H_C: Encodes the supply chain objective and constraint penalties into diagonal Ising phase rotations.",
        "Mixer Hamiltonian H_M: Applies transverse magnetic fields (sum of Pauli X operators) enabling quantum tunneling between configuration states.",
        "Variational Loop: A classical optimizer (COBYLA) tunes angles (gamma, beta) to converge onto the ground state energy."
    ]
    for b in overview_bullets:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(8)

    # Right Column: Math Formulation
    add_card(s4, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.4))
    tb = s4.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(5.0))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "MATHEMATICAL & ISING FORMULATION"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(10)

    math_text = [
        "1. Decision Variables:",
        "    x_{b,m} in {0, 1} indicates batch b is dispatched to market m.",
        "2. Objective Function (Net Margin):",
        "    min  E(x) = sum_i c_i x_i + sum_{i<j} Q_{ij} x_i x_j",
        "    where c_i = -ProfitGain_i / Scale.",
        "3. Zero-Slack Batch Exclusivity Penalty:",
        "    Penalty_{batch} = P_{batch} * sum_{i<j, same b} x_i * x_j",
        "    (Strictly 0 if <= 1 market chosen; penalizes multiple assignments).",
        "4. Pairwise Capacity Penalties:",
        "    Penalty_{cap} = sum_{u<v, same m} (P_{hard} * I(q_u+q_v > C_m)) * x_u * x_v",
        "5. Exact Ising Spin Transformation [x_i = (I - Z_i)/2]:",
        "    h_i = -c_i / 2 - sum_{j != i} Q_{ij} / 4",
        "    J_{ij} = Q_{ij} / 4",
        "    H_C = sum_i h_i Z_i + sum_{i<j} J_{ij} Z_i Z_j + Offset"
    ]
    for line in math_text:
        p = tf.add_paragraph()
        p.text = line
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_MAIN if line.startswith(("1.", "2.", "3.", "4.", "5.")) else TEXT_MUTED
        p.font.bold = True if line.startswith(("1.", "2.", "3.", "4.", "5.")) else False
        p.space_after = Pt(3)

    # =========================================================================
    # SLIDE 5: Proposed Algorithm (Part 2 - Step-by-Step & Pseudocode)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Proposed Algorithm: Execution Workflow & Pseudocode", "ALGORITHM SPECIFICATION — PART 2")

    # Left Column: Step-by-step Execution Flowchart Diagram
    add_card(s5, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.4))
    tb = s5.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(5.2), Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "STEP-BY-STEP EXECUTION FLOW"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_TEAL

    flowchart_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "output", "qaoa_execution_flowchart.png"))
    if os.path.exists(flowchart_path):
        s5.shapes.add_picture(flowchart_path, Inches(0.95), Inches(2.2), width=Inches(5.3), height=Inches(4.65))
    else:
        steps = [
            "Step 1: Superposition Initialization\nApply Hadamard gates H to all n qubits: |+>^n = 1/sqrt(2^n) sum |z>.",
            "Step 2: Cost Unitary Application [Depth p]\nFor layer k=1..p, apply e^{-i * gamma_k * H_C} via RZ and CX-RZ-CX.",
            "Step 3: Mixer Unitary Application\nApply transverse rotations e^{-i * beta_k * H_M} via single-qubit RX(2*beta_k).",
            "Step 4: Energy Expectation Evaluation\nCompute <psi| H_C |psi> using exact butterfly statevector evolution.",
            "Step 5: Classical Parameter Tuning\nCOBYLA optimizer iterates angles (gamma, beta) to minimize energy.",
            "Step 6: Quantum Measurement & Decoding\nSample 2,048 shots from |psi|^2. Validate and decode optimal plan."
        ]
        for s in steps:
            p = tf.add_paragraph()
            p.text = s
            p.font.size = Pt(10.5)
            p.font.color.rgb = TEXT_MUTED
            p.space_after = Pt(5)

    # Right Column: Pseudocode Card
    add_card(s5, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.4), RGBColor(30, 41, 59), RGBColor(51, 65, 85))
    tb = s5.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(5.0))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "ALGORITHM PSEUDOCODE"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(8)

    code_lines = [
        "Algorithm: Capacitated-QAOA-Optimizer(Problem, p, maxiter):",
        "  1: active_vars <- SelectActiveVariables(Problem, max_qubits=10)",
        "  2: (c, Q) <- BuildZeroSlackQUBO(Problem, active_vars)",
        "  3: (h, J) <- MapToIsingHamiltonian(c, Q)  # x_i = (I-Z_i)/2",
        "  4: (gamma_0, beta_0) <- GreedyWarmStartAngles(Problem, p)",
        "  5: Function CostFunction(gamma, beta):",
        "  6:     |psi> <- |+>^n",
        "  7:     for k = 1 to p do:",
        "  8:         |psi> <- exp(-i * gamma_k * H_C) |psi>",
        "  9:         |psi> <- exp(-i * beta_k * H_M) |psi>",
        " 10:     return <psi| H_C |psi>",
        " 11: (gamma*, beta*) <- COBYLA.minimize(CostFunction, init_pt)",
        " 12: |psi_final> <- PrepareState(gamma*, beta*)",
        " 13: shots <- MeasureSamples(|psi_final|^2, count=2048)",
        " 14: best_plan <- IndependentValidator.select_best_feasible(shots)",
        " 15: return best_plan, OptimalProfit, ApproxRatio"
    ]
    for cl in code_lines:
        p = tf.add_paragraph()
        p.text = cl
        p.font.size = Pt(10.5)
        p.font.name = "Consolas"
        p.font.color.rgb = RGBColor(56, 189, 248) if "Function" in cl or "Algorithm" in cl else RGBColor(226, 232, 240)
        p.space_after = Pt(2)

    # =========================================================================
    # SLIDE 6: Algorithm Complexity
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Computational Complexity Analysis")

    w_half = Inches(5.6)
    card_h = Inches(5.4)

    # Left: Time & Space Complexity Cards
    add_card(s6, Inches(0.8), Inches(1.6), w_half, card_h)
    tb = s6.shapes.add_textbox(Inches(1.0), Inches(1.8), w_half - Inches(0.4), card_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "TIME & SPACE COMPLEXITY METRICS"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_TEAL
    p.space_after = Pt(12)

    metrics = [
        ("Quantum Circuit Time Complexity:", "O(p * N^2) gate executions per shot on physical quantum hardware (where p is circuit depth and N is number of qubits)."),
        ("Statevector Simulation Time:", "O(K * p * 2^N) for classical simulation across K classical optimizer iterations. Drops to sub-second (0.05s) via vectorized butterfly array operations."),
        ("Physical Qubit Space Complexity:", "O(N) physical qubits. Zero-Slack formulation guarantees exactly N = len(active_vars) qubits with 0 auxiliary slack qubits."),
        ("Statevector Simulation Space:", "O(2^N) complex state amplitudes in classical host memory. Capping active qubits at N <= 10 limits memory consumption to under 1 MB."),
        ("Classical Exact (MILP) Baseline:", "O(2^N) worst-case time complexity for Branch-and-Cut simplex tree search.")
    ]
    for title, desc in metrics:
        p = tf.add_paragraph()
        p.text = title
        p.font.size = Pt(12.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(11.5)
        p_desc.font.color.rgb = TEXT_MUTED
        p_desc.space_after = Pt(8)

    # Right: Complexity Explanation & Comparison
    add_card(s6, Inches(6.8), Inches(1.6), Inches(5.7), card_h)
    tb = s6.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), card_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "ANALYTICAL EXPLANATION & INSIGHTS"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(12)

    explanations = [
        "1. Classical vs. Quantum Scaling Paradigm:\nOn classical CPUs, solving NP-hard combinatorial optimization scales exponentially. On fault-tolerant quantum processors (QPUs), QAOA evaluates the superposition of all 2^N states simultaneously in O(p) circuit execution depth.",
        "2. The Simulation Bottleneck Justification:\nDuring classical simulation on a laptop, simulating N=10 qubits requires repeatedly transforming a 1,024-element complex vector. This mathematical overhead illustrates exactly why physical quantum hardware is necessary for large-scale logistics.",
        "3. Zero-Slack Memory Advantage:\nStandard constraint converters add 1 integer slack qubit per inequality constraint, inflating 9 decision variables to 12 qubits (4,096 states, an 8x memory surge). Our Zero-Slack quadratic formulation strictly preserves N=9 qubits.",
        "4. Polynomial Parameter Space:\nQAOA optimizes only 2p continuous variational angles regardless of problem dimension N. For depth p=1, only 2 parameters (gamma, beta) are tuned."
    ]
    for exp in explanations:
        p = tf.add_paragraph()
        p.text = exp
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(10)

    # =========================================================================
    # SLIDE 7: Implementation
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "System Implementation & Technology Stack")

    # Left: Tech Stack & Architecture
    add_card(s7, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.4))
    tb = s7.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(5.0))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "SOFTWARE & FRAMEWORK STACK"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_TEAL
    p.space_after = Pt(10)

    stack_items = [
        ("Programming Language:", "Python 3.12 (High-performance scientific computing)"),
        ("Quantum SDK:", "Qiskit 2.4 (QuantumCircuit, gate-level synthesis, Pauli operators)"),
        ("Classical Mathematical Solvers:", "SciPy 1.14 (HiGHS Branch-and-Cut MILP, COBYLA optimizer)"),
        ("Data Ingestion & Indexing:", "Pandas 2.2 & NumPy (O(1) hash lookups across 124k route matrix rows)"),
        ("Interactive Frontend Dashboard:", "Streamlit 1.38 with PyDeck 3D geospatial road arc layer"),
        ("Visualization Engine:", "Matplotlib 3.9 (Automated multi-solver benchmark charts & heatmaps)")
    ]
    for title, desc in stack_items:
        p = tf.add_paragraph()
        p.text = title + " "
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(8)

    # Right Top: Quantum Circuit Diagram Card
    add_card(s7, Inches(6.8), Inches(1.6), Inches(5.7), Inches(2.9), CARD_BG, CARD_BORDER)
    tb_circ = s7.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.3), Inches(0.4))
    tf_circ = tb_circ.text_frame
    tf_circ.word_wrap = True
    p_circ = tf_circ.paragraphs[0]
    p_circ.text = "SYNTHESIZED QAOA QUANTUM CIRCUIT (9 QUBITS, DEPTH 37)"
    p_circ.font.size = Pt(12)
    p_circ.font.bold = True
    p_circ.font.color.rgb = ACCENT_PURPLE

    circuit_img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "output", "qaoa_circuit_slide_wide.png"))
    if os.path.exists(circuit_img_path):
        s7.shapes.add_picture(circuit_img_path, Inches(7.0), Inches(2.1), width=Inches(5.3), height=Inches(2.3))

    # Right Bottom: Code Snippet Card
    add_card(s7, Inches(6.8), Inches(4.65), Inches(5.7), Inches(2.35), RGBColor(30, 41, 59), RGBColor(51, 65, 85))
    tb = s7.shapes.add_textbox(Inches(7.0), Inches(4.75), Inches(5.3), Inches(2.15))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "CORE QAOA CIRCUIT SYNTHESIS (QISKIT 2.4)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(4)

    snippet = [
        "def _build_qaoa_circuit(n_q, h, J, reps, gamma, beta):",
        "    qc = QuantumCircuit(n_q, name=f'QAOA_p{reps}')",
        "    qc.h(range(n_q))  # Step 1: Initial Superposition |+>^n",
        "    for p_idx in range(reps):",
        "        for i in range(n_q): qc.rz(2.0 * gamma[p_idx] * h[i], i)",
        "        for (i, j), J_val in J.items():",
        "            qc.cx(i, j); qc.rz(2.0 * gamma[p_idx] * J_val, j); qc.cx(i, j)",
        "        for i in range(n_q): qc.rx(2.0 * beta[p_idx], i)",
        "    qc.measure_all()",
        "    return qc  # Native Gates: 36 CX, 27 RZ, 9 H, 9 RX, 9 Meas"
    ]
    for line in snippet:
        p = tf.add_paragraph()
        p.text = line
        p.font.size = Pt(9.5)
        p.font.name = "Consolas"
        if line.startswith("def") or line.startswith("    qc ="):
            p.font.color.rgb = RGBColor(56, 189, 248)
        elif line.strip().startswith("#") or "Native Gates" in line:
            p.font.color.rgb = RGBColor(148, 163, 184)
        else:
            p.font.color.rgb = RGBColor(226, 232, 240)
        p.space_after = Pt(1)

    # =========================================================================
    # SLIDE 8: Results and Analysis
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Experimental Results & Solver Performance Benchmarks")

    # Top Table Card
    add_card(s8, Inches(0.8), Inches(1.6), Inches(11.7), Inches(2.9))
    tb = s8.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(11.3), Inches(2.6))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "MULTI-SOLVER BENCHMARK RESULTS (TESTED ON REAL TAMIL NADU DATASETS)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_TEAL
    p.space_after = Pt(6)

    table_lines = [
        "Scenario 1: 3 Batches x 3 Markets (9 Decision Variables, 9 Qubits) — Pure Quantum QAOA",
        "  • Classical Exact (MILP HiGHS) : Net Profit = Rs 194,289.10 | Capacity Valid = YES | Ratio = 100.0% | Runtime = 0.005s",
        "  • Classical Greedy Heuristic   : Net Profit = Rs 194,289.10 | Capacity Valid = YES | Ratio = 100.0% | Runtime = 0.0001s",
        "  • Simulated Annealing (QUBO)   : Net Profit = Rs 188,322.72 | Capacity Valid = YES | Ratio =  96.9% | Runtime = 0.006s",
        "  • Pure Quantum QAOA (p=1)      : Net Profit = Rs 194,289.10 | Capacity Valid = YES | Ratio = 100.0% | Runtime = 0.050s",
        "",
        "Scenario 2: 4 Batches x 4 Markets (16 Decision Variables, 10 Active Qubits) — Capacity Bottleneck Test",
        "  • Classical Exact (MILP HiGHS) : Net Profit = Rs 330,067.10 | Capacity Valid = YES | Ratio = 100.0% | Runtime = 0.015s",
        "  • Hybrid QAOA + Backfill (p=1) : Net Profit = Rs 315,542.44 | Capacity Valid = YES | Ratio =  95.6% | Runtime = 0.058s"
    ]
    for tl in table_lines:
        p = tf.add_paragraph()
        p.text = tl
        if "Scenario" in tl:
            p.font.size = Pt(11.5)
            p.font.bold = True
            p.font.color.rgb = TEXT_MAIN
        else:
            p.font.size = Pt(11)
            p.font.name = "Consolas"
            p.font.color.rgb = ACCENT_BLUE if "Quantum QAOA" in tl or "Hybrid QAOA" in tl else TEXT_MUTED
        p.space_after = Pt(2)

    # Bottom Left: Key Observations
    add_card(s8, Inches(0.8), Inches(4.7), Inches(5.7), Inches(2.3))
    tb = s8.shapes.add_textbox(Inches(1.0), Inches(4.8), Inches(5.3), Inches(2.1))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "KEY EXPERIMENTAL OBSERVATIONS"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(6)

    obs = [
        "100% Feasibility Enforced: Independent validator verifies zero capacity overloads across all reporting solvers.",
        "Zero-Slack Speedup: Pairwise quadratic penalties enabled sub-second QAOA execution (0.05s) with zero auxiliary qubits.",
        "Ground Truth Alignment: QAOA achieved 95.6% to 100% of the provable global optimum across all test instances."
    ]
    for o in obs:
        p = tf.add_paragraph()
        p.text = "• " + o
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(4)

    # Bottom Right: Dashboard & Application
    add_card(s8, Inches(6.8), Inches(4.7), Inches(5.7), Inches(2.3))
    tb = s8.shapes.add_textbox(Inches(7.0), Inches(4.8), Inches(5.3), Inches(2.1))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "APPLICATION & INTERACTIVE DASHBOARD"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_PURPLE
    p.space_after = Pt(6)

    app_bullets = [
        "Streamlit Web Dashboard: Real-time UI with dynamic sliders for batches, candidate markets, QAOA circuit depth p, and max iterations.",
        "PyDeck 3D Geospatial Map: Renders road transit connections between farm collection centres and Uzhavar Santhais in Tamil Nadu.",
        "Dispatch Plan Export: One-click CSV export of truck allocation, expected revenue, transport diesel costs, and net margin."
    ]
    for ab in app_bullets:
        p = tf.add_paragraph()
        p.text = "• " + ab
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(4)

    # =========================================================================
    # SLIDE 9: Conclusion
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Project Conclusion & Research Summary")

    card_w = Inches(5.6)
    card_h = Inches(2.5)

    # Card 1: What was achieved
    add_card(s9, Inches(0.8), Inches(1.6), card_w, card_h)
    tb = s9.shapes.add_textbox(Inches(1.0), Inches(1.75), card_w - Inches(0.4), card_h - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "WHAT WAS ACHIEVED"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_TEAL
    p.space_after = Pt(6)
    bullets = [
        "Engineered an end-to-end quantum agricultural dispatch pipeline on real Tamil Nadu geospatial and wholesale pricing data.",
        "Formulated a Zero-Slack QUBO model enforcing batch exclusivity and market throughput limits with zero auxiliary qubits.",
        "Implemented mathematically verified QAOA with exact Ising spin mapping (TVD = 0.0) and true multi-layer depth p."
    ]
    for b in bullets:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(4)

    # Card 2: Problem Addressed
    add_card(s9, Inches(6.8), Inches(1.6), card_w, card_h)
    tb = s9.shapes.add_textbox(Inches(7.0), Inches(1.75), card_w - Inches(0.4), card_h - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "PROBLEM ADDRESSAL & REAL-WORLD FEASIBILITY"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(6)
    bullets = [
        "The proposed problem was successfully addressed: all generated dispatch plans strictly respect transit shelf-life deadlines.",
        "Guaranteed zero market capacity violations via independent validation and pairwise penalty tuning.",
        "Significant financial improvement: net profit increases by allocating produce to optimal high-value wholesale markets."
    ]
    for b in bullets:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(4)

    # Card 3: Key Observations
    add_card(s9, Inches(0.8), Inches(4.4), card_w, card_h)
    tb = s9.shapes.add_textbox(Inches(1.0), Inches(4.55), card_w - Inches(0.4), card_h - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "KEY SCIENTIFIC OBSERVATIONS"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_PURPLE
    p.space_after = Pt(6)
    bullets = [
        "Classical statevector simulation is computationally expensive (O(2^N)), proving the fundamental necessity of physical QPUs.",
        "Greedy warm-start angle initialization steers variational optimizers directly into the global energy minimum.",
        "Transparent attribution separates pure quantum sampling from classical hybrid post-processing."
    ]
    for b in bullets:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(4)

    # Card 4: Effectiveness of Algorithm
    add_card(s9, Inches(6.8), Inches(4.4), card_w, card_h)
    tb = s9.shapes.add_textbox(Inches(7.0), Inches(4.55), card_w - Inches(0.4), card_h - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "EFFECTIVENESS OF THE ALGORITHM"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = RGBColor(22, 163, 74)
    p.space_after = Pt(6)
    bullets = [
        "High Solution Quality: QAOA consistently attained 95.6% to 100% approximation ratio relative to the global exact optimum.",
        "Fast Execution: Vectorized butterfly transformations execute in 0.05 seconds, suitable for live production web services.",
        "Scalability Path: Provides a verified quantum blueprint ready for deployment on IBM Quantum Heron/Eagle hardware backends."
    ]
    for b in bullets:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(4)

    # =========================================================================
    # SLIDE 10: Thank You
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    bg10 = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg10.fill.solid()
    bg10.fill.fore_color.rgb = DARK_BG
    bg10.line.fill.background()

    tb = s10.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.333), Inches(4.0))
    tf10 = tb.text_frame
    tf10.word_wrap = True

    p = tf10.paragraphs[0]
    p.text = "THANK YOU!"
    p.font.size = Pt(48)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER
    p.space_after = Pt(14)

    p2 = tf10.add_paragraph()
    p2.text = "Questions & Discussion"
    p2.font.size = Pt(22)
    p2.font.color.rgb = ACCENT_TEAL
    p2.alignment = PP_ALIGN.CENTER
    p2.space_after = Pt(28)

    p3 = tf10.add_paragraph()
    p3.text = "Raaghav vel P (CH.SC.u4cse24155)  |  Srinivas R (CH.SC.U4CSE24146)"
    p3.font.size = Pt(18)
    p3.font.bold = True
    p3.font.color.rgb = RGBColor(226, 232, 240)
    p3.alignment = PP_ALIGN.CENTER
    p3.space_after = Pt(12)

    p4 = tf10.add_paragraph()
    p4.text = "Department of Computer Science & Engineering | 5th Semester Quantum Computing Capstone"
    p4.font.size = Pt(14)
    p4.font.color.rgb = RGBColor(148, 163, 184)
    p4.alignment = PP_ALIGN.CENTER

    output_path = "AgriQuantum_Capstone_Presentation.pptx"
    try:
        prs.save(output_path)
        print(f"Presentation saved successfully to: {os.path.abspath(output_path)}")
    except PermissionError:
        alt_path = "AgriQuantum_Capstone_Presentation_Updated.pptx"
        prs.save(alt_path)
        print(f"File was locked by PowerPoint. Saved successfully to: {os.path.abspath(alt_path)}")

if __name__ == "__main__":
    create_presentation()
