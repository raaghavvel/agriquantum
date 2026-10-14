"""
visualizer.py
─────────────
Visualization module for the Farm-to-Market Quantum Optimization system.
Generates charts, maps, and comparison plots.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from typing import Dict, Optional

from data_loader import DataLoader
from problem_builder import ProblemInstance


class Visualizer:
    """Generates all visualization outputs."""

    OUTPUT_DIR = Path("output")
    COLORS = {
        "greedy": "#2196F3",
        "classical_exact": "#4CAF50",
        "qaoa": "#FF9800",
        "vqe": "#9C27B0",
    }

    def __init__(self):
        self.OUTPUT_DIR.mkdir(exist_ok=True)

    def plot_solver_comparison(
        self, results: Dict[str, dict], save_name: str = "solver_comparison.png"
    ):
        """Bar chart comparing profit and computation time across solvers."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        solvers = list(results.keys())
        profits = [results[s].get("total_profit", 0) for s in solvers]
        times = [results[s].get("time_seconds", 0) for s in solvers]
        colors = [self.COLORS.get(s, "#607D8B") for s in solvers]

        # Profit comparison
        bars1 = ax1.bar(solvers, profits, color=colors, edgecolor="white", linewidth=1.2)
        ax1.set_title("Total Profit by Solver", fontsize=14, fontweight="bold")
        ax1.set_ylabel("Profit (INR)", fontsize=12)
        for bar, val in zip(bars1, profits):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
                     f"Rs {val:,.0f}", ha="center", va="bottom", fontsize=10)

        # Time comparison
        bars2 = ax2.bar(solvers, times, color=colors, edgecolor="white", linewidth=1.2)
        ax2.set_title("Computation Time by Solver", fontsize=14, fontweight="bold")
        ax2.set_ylabel("Time (seconds)", fontsize=12)
        for bar, val in zip(bars2, times):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                     f"{val:.3f}s", ha="center", va="bottom", fontsize=10)

        plt.tight_layout()
        path = self.OUTPUT_DIR / save_name
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"Saved: {path}")

    def plot_assignment_map(
        self,
        problem: ProblemInstance,
        assignments: pd.DataFrame,
        loader: DataLoader,
        solver_name: str = "Optimizer",
        save_name: str = "assignment_map.png",
    ):
        """
        Plot supply-to-market assignment on a geographic scatter plot.
        Lines connect assigned sources to their destination markets.
        """
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))

        # Plot all supply locations (blue triangles)
        for _, src in loader.sources.iterrows():
            ax.scatter(
                float(src["longitude"]), float(src["latitude"]),
                marker="^", s=80, c="#1565C0", zorder=5, edgecolors="white"
            )
            ax.annotate(
                src["source_name"].replace(" Collection Centre", ""),
                (float(src["longitude"]), float(src["latitude"])),
                fontsize=6, ha="left", va="bottom", alpha=0.7
            )

        # Plot assigned markets (green circles)
        assigned_market_ids = set(assignments["market_id"]) if not assignments.empty else set()
        for _, mkt in loader.markets.iterrows():
            if mkt["market_id"] in assigned_market_ids:
                color, size, alpha = "#4CAF50", 120, 1.0
            else:
                color, size, alpha = "#BDBDBD", 40, 0.4
            ax.scatter(
                float(mkt["longitude_num"]), float(mkt["latitude_num"]),
                marker="o", s=size, c=color, zorder=4, alpha=alpha, edgecolors="white"
            )

        # Draw assignment lines
        if not assignments.empty:
            for _, row in assignments.iterrows():
                batch = problem.batches[problem.batches["batch_id"] == row["batch_id"]].iloc[0]
                src = loader.sources[loader.sources["source_id"] == batch["source_id"]].iloc[0]
                mkt = loader.markets[loader.markets["market_id"] == row["market_id"]].iloc[0]

                ax.plot(
                    [float(src["longitude"]), float(mkt["longitude_num"])],
                    [float(src["latitude"]), float(mkt["latitude_num"])],
                    "r-", alpha=0.6, linewidth=1.5, zorder=3
                )

        # Legend
        legend_elements = [
            mpatches.Patch(color="#1565C0", label="Supply Locations"),
            mpatches.Patch(color="#4CAF50", label="Assigned Markets"),
            mpatches.Patch(color="#BDBDBD", label="Other Markets"),
            plt.Line2D([0], [0], color="red", alpha=0.6, linewidth=2, label="Assignments"),
        ]
        ax.legend(handles=legend_elements, loc="lower right", fontsize=9)

        ax.set_xlabel("Longitude", fontsize=12)
        ax.set_ylabel("Latitude", fontsize=12)
        ax.set_title(
            f"Farm-to-Market Assignments ({solver_name})\n"
            f"Tamil Nadu Agricultural Supply Chain",
            fontsize=14, fontweight="bold"
        )
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        path = self.OUTPUT_DIR / save_name
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"Saved: {path}")

    def plot_profit_breakdown(
        self,
        assignments: pd.DataFrame,
        solver_name: str = "Optimizer",
        save_name: str = "profit_breakdown.png",
    ):
        """Stacked bar chart showing revenue, cost, penalty per batch."""
        if assignments.empty:
            print("No assignments to plot.")
            return

        fig, ax = plt.subplots(figsize=(12, 6))

        batch_ids = assignments["batch_id"].tolist()
        revenues = assignments["revenue"].values
        costs = assignments["transport_cost"].values
        penalties = assignments["late_penalty"].values
        profits = assignments["net_profit"].values

        x = np.arange(len(batch_ids))
        width = 0.6

        ax.bar(x, revenues, width, label="Revenue", color="#4CAF50", alpha=0.85)
        ax.bar(x, -costs, width, label="Transport Cost", color="#F44336", alpha=0.85)
        ax.bar(x, -penalties, width, bottom=-costs,
               label="Late Penalty", color="#FF9800", alpha=0.85)

        # Net profit line
        ax.plot(x, profits, "ko-", markersize=6, linewidth=2, label="Net Profit", zorder=5)

        ax.set_xticks(x)
        ax.set_xticklabels(batch_ids, rotation=45, fontsize=9)
        ax.set_xlabel("Batch", fontsize=12)
        ax.set_ylabel("Amount (INR)", fontsize=12)
        ax.set_title(
            f"Profit Breakdown per Batch ({solver_name})",
            fontsize=14, fontweight="bold"
        )
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis="y")
        ax.axhline(y=0, color="black", linewidth=0.8)

        plt.tight_layout()
        path = self.OUTPUT_DIR / save_name
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"Saved: {path}")

    def plot_feasibility_heatmap(
        self,
        problem: ProblemInstance,
        save_name: str = "feasibility_heatmap.png",
    ):
        """Heatmap showing which batch-market assignments are feasible and profitable."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        # Feasibility
        im1 = ax1.imshow(
            problem.feasible.astype(int), cmap="RdYlGn",
            aspect="auto", interpolation="nearest"
        )
        ax1.set_title("Feasibility Matrix", fontsize=13, fontweight="bold")
        ax1.set_xlabel("Market Index")
        ax1.set_ylabel("Batch Index")
        ax1.set_xticks(range(problem.n_markets))
        ax1.set_xticklabels(problem.market_ids, rotation=90, fontsize=7)
        ax1.set_yticks(range(problem.n_batches))
        ax1.set_yticklabels(problem.batch_ids, fontsize=8)
        plt.colorbar(im1, ax=ax1, shrink=0.8)

        # Profit (masked for feasible only)
        profit_display = np.where(problem.feasible, problem.profit, np.nan)
        im2 = ax2.imshow(
            profit_display, cmap="YlGn",
            aspect="auto", interpolation="nearest"
        )
        ax2.set_title("Profit Matrix (INR)", fontsize=13, fontweight="bold")
        ax2.set_xlabel("Market Index")
        ax2.set_ylabel("Batch Index")
        ax2.set_xticks(range(problem.n_markets))
        ax2.set_xticklabels(problem.market_ids, rotation=90, fontsize=7)
        ax2.set_yticks(range(problem.n_batches))
        ax2.set_yticklabels(problem.batch_ids, fontsize=8)
        plt.colorbar(im2, ax=ax2, shrink=0.8)

        plt.tight_layout()
        path = self.OUTPUT_DIR / save_name
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"Saved: {path}")

    def plot_quantum_vs_classical(
        self,
        results: Dict[str, dict],
        save_name: str = "quantum_vs_classical.png",
    ):
        """
        Radar / multi-metric comparison between quantum and classical solvers.
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        solvers = list(results.keys())
        metrics = ["Total Profit", "Batches Assigned", "Speed Score"]

        data = []
        for s in solvers:
            r = results[s]
            profit = r.get("total_profit", 0)
            assigned = (
                len(r["assignments"])
                if "assignments" in r and isinstance(r.get("assignments"), pd.DataFrame) and not r["assignments"].empty
                else 0
            )
            speed = 1.0 / max(r.get("time_seconds", 1), 0.001)
            data.append([profit, assigned, speed])

        data = np.array(data)
        # Normalize to [0, 1]
        maxvals = data.max(axis=0)
        maxvals[maxvals == 0] = 1
        normed = data / maxvals

        x = np.arange(len(metrics))
        width = 0.8 / len(solvers)

        for i, solver in enumerate(solvers):
            color = self.COLORS.get(solver, "#607D8B")
            ax.bar(x + i * width, normed[i], width,
                   label=solver, color=color, alpha=0.85)

        ax.set_xticks(x + width * (len(solvers) - 1) / 2)
        ax.set_xticklabels(metrics, fontsize=12)
        ax.set_ylabel("Normalized Score", fontsize=12)
        ax.set_title(
            "Quantum vs Classical: Multi-Metric Comparison",
            fontsize=14, fontweight="bold"
        )
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        path = self.OUTPUT_DIR / save_name
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"Saved: {path}")

    def plot_circuit(self, circuit, save_name: str = "qaoa_circuit.png"):
        """Save a visual drawing of the synthesized Qiskit QuantumCircuit."""
        if circuit is None:
            return
        try:
            fig = circuit.draw(output="mpl", fold=25, style={"backgroundcolor": "#FFFFFF"})
            path = self.OUTPUT_DIR / save_name
            fig.savefig(path, dpi=150, bbox_inches="tight")
            plt.close(fig)
            print(f"Saved: {path}")
        except Exception as e:
            print(f"Could not render circuit matplotlib figure: {e}")


if __name__ == "__main__":
    print("Visualizer module loaded. Use from main.py.")
