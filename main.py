"""
main.py
───────
Quantum Optimization-based Agricultural Supply Chain Management System
Tamil Nadu Farm-to-Market Logistics Optimizer

Main execution pipeline:
  1. Loads all 9 Tamil Nadu supply-chain datasets
  2. Formulates the QUBO / constrained optimization problem
  3. Executes Classical (Greedy, Exact MILP, Simulated Annealing) and Quantum (QAOA) solvers
  4. Generates benchmark comparison and optimality ratios
  5. Produces geographic dispatch maps and financial breakdowns
  6. Exports the final optimized dispatch plan to CSV
"""

import argparse
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

from data_loader import DataLoader
from problem_builder import ProblemBuilder
from quantum_optimizer import QuantumFarmOptimizer
from visualizer import Visualizer


def print_banner():
    print()
    print("=" * 70)
    print("  QUANTUM OPTIMIZATION-BASED AGRICULTURAL SUPPLY CHAIN")
    print("  Tamil Nadu Farm-to-Market Logistics Optimizer")
    print("=" * 70)
    print(f"  Execution Time : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()


def run_optimization(
    max_batches: int = 4,
    max_markets: int = 4,
    qaoa_reps: int = 1,
    qaoa_maxiter: int = 25,
    districts: list = None,
):
    """
    Run the end-to-end quantum agricultural optimization pipeline.
    """
    print_banner()

    # ── Step 1: Load Datasets ──────────────────────────────────────────────
    print("STEP 1: Loading & Indexing 9 Supply Chain Datasets...")
    loader = DataLoader()
    loader.summary()

    # ── Step 2: Formulate Problem ──────────────────────────────────────────
    print("\nSTEP 2: Formulating Farm-to-Market Optimization Model...")
    builder = ProblemBuilder(loader)
    problem = builder.build(
        max_batches=max_batches,
        max_markets=max_markets,
        target_districts=districts,
        prune_infeasible=True,
    )

    feasible_count = int(problem.feasible.sum())
    total_pairs = problem.n_batches * problem.n_markets
    print(f"  Feasible Links : {feasible_count}/{total_pairs} ({100.0 * feasible_count / max(total_pairs, 1):.1f}%)")
    print(f"  Qubits Needed  : {problem.n_vars} qubits (pruned from {total_pairs})")

    if problem.n_vars == 0:
        print("\n  [ERROR] No feasible batch-to-market assignments available!")
        print("  Check freshness deadlines and crop eligibility.")
        return None

    # ── Step 3: Run Quantum & Classical Solvers ───────────────────────────
    print("\nSTEP 3: Solving via Quantum and Classical Optimization...")
    optimizer = QuantumFarmOptimizer(problem)

    # 3a. Classical Greedy Heuristic
    optimizer.solve_greedy()

    # 3b. Classical Exact MILP (Highs Branch-and-Cut)
    optimizer.solve_classical_milp()

    # 3c. Simulated Annealing on QUBO
    optimizer.solve_simulated_annealing(sweeps=600)

    # 3d. Qiskit QAOA (Quantum Approximate Optimization Algorithm)
    optimizer.solve_qaoa(reps=qaoa_reps, maxiter=qaoa_maxiter)

    # ── Step 4: Solver Benchmarking ───────────────────────────────────────
    print("\n" + "=" * 70)
    print("  STEP 4: MULTI-SOLVER BENCHMARK SUMMARY")
    print("=" * 70)
    comparison_df = optimizer.compare_results()
    print(comparison_df.to_string(index=False))

    # ── Step 5: Optimal Allocation Plan ───────────────────────────────────
    # Use classical exact / greedy for primary schedule
    best_solver = "classical_exact"
    best_result = optimizer.results.get(best_solver, optimizer.results.get("greedy", {}))
    assignments = best_result.get("assignments", pd.DataFrame())

    if not assignments.empty:
        print("\n" + "=" * 70)
        print(f"  STEP 5: OPTIMAL ALLOCATION SCHEDULE ({best_solver.upper()})")
        print("=" * 70)

        enriched = assignments.copy()
        enriched["crop_name"] = enriched["crop_id"].map(loader.crop_id_to_name)
        mkt_map = dict(zip(loader.markets["market_id"], loader.markets["market_name"]))
        enriched["market_name"] = enriched["market_id"].map(mkt_map)

        # Source and distance details
        for idx, row in enriched.iterrows():
            batch_row = problem.batches[problem.batches["batch_id"] == row["batch_id"]].iloc[0]
            src_row = loader.sources[loader.sources["source_id"] == batch_row["source_id"]].iloc[0]
            enriched.at[idx, "source_name"] = src_row["source_name"]
            enriched.at[idx, "distance_km"] = loader.get_travel_distance(batch_row["source_id"], row["market_id"])
            enriched.at[idx, "travel_min"] = loader.get_travel_time(batch_row["source_id"], row["market_id"])

        display_cols = [
            "batch_id", "crop_name", "quantity_kg", "source_name",
            "market_name", "distance_km", "revenue", "transport_cost",
            "net_profit",
        ]
        available_cols = [c for c in display_cols if c in enriched.columns]
        print(enriched[available_cols].to_string(index=False))

        total_rev = enriched["revenue"].sum()
        total_cost = enriched["transport_cost"].sum()
        total_late = enriched["late_penalty"].sum()
        total_net = enriched["net_profit"].sum()

        print("-" * 70)
        print(f"  TOTAL REVENUE          : Rs {total_rev:>12,.2f}")
        print(f"  TOTAL TRANSPORT COST   : Rs {total_cost:>12,.2f}")
        print(f"  TOTAL LATE PENALTIES   : Rs {total_late:>12,.2f}")
        print("-" * 70)
        print(f"  NET OPTIMIZED PROFIT   : Rs {total_net:>12,.2f}")
        print("=" * 70)

        # Export schedule to output folder
        out_dir = Path("output")
        out_dir.mkdir(exist_ok=True)
        schedule_path = out_dir / "assignment_plan.csv"
        enriched.to_csv(schedule_path, index=False)
        print(f"\n  Schedule exported to: {schedule_path}")

    # ── Step 6: Generate Visualizations ───────────────────────────────────
    print("\nSTEP 6: Generating System Visualizations...")
    viz = Visualizer()

    viz.plot_solver_comparison(optimizer.results)
    viz.plot_feasibility_heatmap(problem)

    if not assignments.empty:
        viz.plot_profit_breakdown(assignments, best_solver)
        viz.plot_assignment_map(problem, assignments, loader, best_solver)

    viz.plot_quantum_vs_classical(optimizer.results)
    if "qaoa" in optimizer.results and "circuit" in optimizer.results["qaoa"]:
        viz.plot_circuit(optimizer.results["qaoa"]["circuit"])
    print("  Visualizations generated in: output/")

    # ── Final Quantum Analysis Summary ────────────────────────────────────
    print("\n" + "=" * 70)
    print("  QUANTUM SYSTEM PERFORMANCE REPORT")
    print("=" * 70)
    if "qaoa" in optimizer.results and "classical_exact" in optimizer.results:
        q_res = optimizer.results["qaoa"]
        c_res = optimizer.results["classical_exact"]
        q_profit = q_res.get("total_profit", 0.0)
        c_profit = c_res.get("total_profit", 1.0)
        ratio = (q_profit / c_profit) * 100.0 if c_profit > 0 else 0.0
        q_time = q_res.get("time_seconds", 0.0)
        c_time = c_res.get("time_seconds", 0.0)
        actual_q = q_res.get("num_qubits", min(problem.n_vars, 10))

        print(f"  * Classical Exact Optimal Profit : Rs {c_profit:,.2f}  (Time: {c_time:.4f}s)")
        print(f"  * Quantum QAOA Solution Profit   : Rs {q_profit:,.2f}  (Time: {q_time:.2f}s)")
        print(f"  * Quantum Approximation Ratio    : {ratio:.1f}%")
        print(f"  * QAOA Mode / Attribution        : {q_res.get('attribution', 'QAOA')}")
        print(f"  * Capacity Feasibility Status    : {q_res.get('status', 'FEASIBLE')}")
        print(f"  * Quantum Register Scale         : {actual_q} Active Qubits (Problem variables: {problem.n_vars}), Depth p={qaoa_reps}")
    print("=" * 70)
    print()

    return optimizer


def main():
    parser = argparse.ArgumentParser(
        description="Quantum Agricultural Supply Chain Optimizer"
    )
    parser.add_argument(
        "--batches", type=int, default=4,
        help="Number of supply batches (default: 4)"
    )
    parser.add_argument(
        "--markets", type=int, default=4,
        help="Number of destination markets (default: 4)"
    )
    parser.add_argument(
        "--qaoa-reps", type=int, default=1,
        help="QAOA circuit repetitions p (default: 1)"
    )
    parser.add_argument(
        "--qaoa-maxiter", type=int, default=25,
        help="QAOA optimizer iterations (default: 25)"
    )
    parser.add_argument(
        "--districts", nargs="+", default=None,
        help="Target Tamil Nadu districts (e.g., Coimbatore Salem)"
    )

    args = parser.parse_args()

    run_optimization(
        max_batches=args.batches,
        max_markets=args.markets,
        qaoa_reps=args.qaoa_reps,
        qaoa_maxiter=args.qaoa_maxiter,
        districts=args.districts,
    )


if __name__ == "__main__":
    main()
