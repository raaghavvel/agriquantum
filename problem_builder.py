"""
problem_builder.py
──────────────────
Builds an optimized, realistic farm-to-market allocation instance.
Supports:
  1. Dense representation (all b x m variables)
  2. Pruned / Compact representation (only feasible pairs -> minimal qubits)
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from data_loader import DataLoader


class ProblemInstance:
    """A mathematically grounded problem instance for classical and quantum optimization."""

    def __init__(
        self,
        batches: pd.DataFrame,
        markets: pd.DataFrame,
        revenue: np.ndarray,          # shape (n_batches, n_markets)
        transport_cost: np.ndarray,   # shape (n_batches, n_markets)
        late_penalty: np.ndarray,     # shape (n_batches, n_markets)
        unsold_penalty: np.ndarray,   # shape (n_batches,)
        feasible: np.ndarray,         # shape (n_batches, n_markets), bool
        market_capacity_kg: np.ndarray, # shape (n_markets,)
        batch_ids: List[str],
        market_ids: List[str],
        pair_to_var: Dict[Tuple[int, int], int],  # (b, m) -> variable index
        var_to_pair: Dict[int, Tuple[int, int]],  # variable index -> (b, m)
    ):
        self.batches = batches
        self.markets = markets
        self.revenue = revenue
        self.transport_cost = transport_cost
        self.late_penalty = late_penalty
        self.unsold_penalty = unsold_penalty
        self.feasible = feasible
        self.market_capacity_kg = market_capacity_kg
        self.batch_ids = batch_ids
        self.market_ids = market_ids
        self.n_batches = len(batch_ids)
        self.n_markets = len(market_ids)

        self.pair_to_var = pair_to_var
        self.var_to_pair = var_to_pair
        self.n_vars = len(pair_to_var)

        # Net profit gained by assigning (b, m) over leaving unsold:
        # Profit(b, m) = Revenue(b, m) - TransportCost(b, m) - LatePenalty(b, m) + UnsoldSaved(b)
        self.profit_gain = np.zeros((self.n_batches, self.n_markets))
        for b in range(self.n_batches):
            for m in range(self.n_markets):
                if self.feasible[b, m]:
                    self.profit_gain[b, m] = (
                        self.revenue[b, m]
                        - self.transport_cost[b, m]
                        - self.late_penalty[b, m]
                        + self.unsold_penalty[b]
                    )
                else:
                    self.profit_gain[b, m] = -1e6

        # Alias for visualizer compatibility
        self.profit = self.profit_gain

    def validate_solution(self, x_vec: np.ndarray) -> dict:
        """
        Independent solution validator verifying:
          1. Batch exclusivity: at most one market per batch
          2. Market capacity: total weight assigned to market <= capacity
          3. Pair feasibility: pairs assigned must be feasible
          4. Objective decomposition: revenue, transport, late penalties, unsold penalties, net business objective
        """
        batch_assigned: Dict[int, List[int]] = {}
        for var_idx, val in enumerate(x_vec):
            if val > 0.5 and var_idx in self.var_to_pair:
                b, m = self.var_to_pair[var_idx]
                if b not in batch_assigned:
                    batch_assigned[b] = []
                batch_assigned[b].append(m)

        batch_conflicts = {b: mkts for b, mkts in batch_assigned.items() if len(mkts) > 1}

        # Market load calculation
        market_load = np.zeros(self.n_markets)
        infeasible_pairs = []
        for b, mkts in batch_assigned.items():
            qty = float(self.batches.iloc[b]["quantity_kg"])
            for m in mkts:
                market_load[m] += qty
                if not self.feasible[b, m]:
                    infeasible_pairs.append((b, m))

        overloads = {}
        for m in range(self.n_markets):
            cap = float(self.market_capacity_kg[m])
            if market_load[m] > cap + 1e-3:
                overloads[self.market_ids[m]] = float(market_load[m] - cap)

        is_batch_feasible = len(batch_conflicts) == 0
        is_capacity_feasible = len(overloads) == 0
        is_pair_feasible = len(infeasible_pairs) == 0
        is_feasible = is_batch_feasible and is_capacity_feasible and is_pair_feasible

        # Financial objective calculation
        tot_rev = 0.0
        tot_trans = 0.0
        tot_late = 0.0
        assigned_batches = set()
        for b, mkts in batch_assigned.items():
            if len(mkts) == 1:
                m = mkts[0]
                if self.feasible[b, m]:
                    assigned_batches.add(b)
                    tot_rev += float(self.revenue[b, m])
                    tot_trans += float(self.transport_cost[b, m])
                    tot_late += float(self.late_penalty[b, m])

        sold_margin = tot_rev - tot_trans - tot_late
        unsold_penalties_incurred = sum(
            float(self.unsold_penalty[b]) for b in range(self.n_batches) if b not in assigned_batches
        )
        net_objective = sold_margin - unsold_penalties_incurred

        if not is_batch_feasible:
            status = "INFEASIBLE (Multiple markets assigned to batch)"
        elif not is_capacity_feasible:
            max_ov = max(overloads.values())
            status = f"INFEASIBLE (Capacity overload {max_ov:.0f} kg)"
        elif not is_pair_feasible:
            status = "INFEASIBLE (Infeasible pair assigned)"
        else:
            status = "FEASIBLE"

        return {
            "is_feasible": is_feasible,
            "is_capacity_feasible": is_capacity_feasible,
            "is_batch_feasible": is_batch_feasible,
            "overloads": overloads,
            "max_overload_kg": max(overloads.values()) if overloads else 0.0,
            "status": status,
            "revenue": tot_rev,
            "transport_cost": tot_trans,
            "late_penalty": tot_late,
            "sold_margin": sold_margin,
            "unsold_penalty": unsold_penalties_incurred,
            "net_objective": net_objective,
            "batches_assigned": len(assigned_batches),
            "market_loads": {self.market_ids[m]: float(market_load[m]) for m in range(self.n_markets)},
        }

    def decode_solution(self, x_vec: np.ndarray, enforce_capacity: bool = False) -> pd.DataFrame:
        """
        Decode binary vector into structured allocation DataFrame (at most 1 market per batch).
        If enforce_capacity is True, drops or adjusts over-capacity allocations in order of lowest margin.
        """
        # Pick best market per batch among active assignments
        candidates = []
        for var_idx, val in enumerate(x_vec):
            if val > 0.5 and var_idx in self.var_to_pair:
                b, m = self.var_to_pair[var_idx]
                if self.feasible[b, m]:
                    prof = float(self.revenue[b, m] - self.transport_cost[b, m] - self.late_penalty[b, m])
                    candidates.append((prof, b, m, var_idx))

        # Sort descending by profit
        candidates.sort(key=lambda x: x[0], reverse=True)

        assigned_b = set()
        market_load = np.zeros(self.n_markets)
        batch_assignment: Dict[int, int] = {}

        for prof, b, m, var_idx in candidates:
            if b in assigned_b:
                continue
            qty = float(self.batches.iloc[b]["quantity_kg"])
            if enforce_capacity:
                if market_load[m] + qty <= float(self.market_capacity_kg[m]) + 1e-3:
                    assigned_b.add(b)
                    batch_assignment[b] = m
                    market_load[m] += qty
            else:
                assigned_b.add(b)
                batch_assignment[b] = m
                market_load[m] += qty

        rows = []
        for b, m in batch_assignment.items():
            qty = float(self.batches.iloc[b]["quantity_kg"])
            rev = float(self.revenue[b, m])
            cost = float(self.transport_cost[b, m])
            late = float(self.late_penalty[b, m])
            net_prof = rev - cost - late

            rows.append({
                "batch_id": self.batch_ids[b],
                "market_id": self.market_ids[m],
                "crop_id": self.batches.iloc[b]["crop_id"],
                "quantity_kg": qty,
                "revenue": rev,
                "transport_cost": cost,
                "late_penalty": late,
                "net_profit": net_prof,
                "feasible": bool(self.feasible[b, m]),
            })
        return pd.DataFrame(rows)


class ProblemBuilder:
    """Builds the instance from raw datasets with smart selection and pruning."""

    DEFAULT_PRICES = {
        "C015": 28.0,  # Tomato
        "C016": 24.0,  # Onion
        "C023": 32.0,  # Banana
        "C001": 25.0,  # Rice
        "C002": 20.0,  # Maize
        "C025": 18.0,  # Coconut
        "C029": 55.0,  # Groundnut
    }

    def __init__(self, loader: DataLoader):
        self.loader = loader

    def build(
        self,
        max_batches: int = 4,
        max_markets: int = 4,
        target_districts: Optional[List[str]] = None,
        prune_infeasible: bool = True,
        all_markets: bool = False,
    ) -> ProblemInstance:
        """
        Build an optimization instance.

        Args:
            max_batches: Number of supply batches.
            max_markets: Number of destination markets.
            target_districts: Filter markets by district.
            prune_infeasible: If True, only feasible pairs become binary variables
                              (essential for quantum simulations).
            all_markets: If True, include all eligible markets without nearest-market truncation.
        """
        # Select batches
        batches = self.loader.batches.copy().head(max_batches)
        batch_ids = batches["batch_id"].tolist()
        batch_sources = batches["source_id"].unique()
        batch_crops = batches["crop_id"].unique()

        # Select candidate markets
        search_all = all_markets
        all_markets = self.loader.markets.copy()
        if target_districts:
            # Map canonical names and spelling variants
            dist_set = set(target_districts)
            if "Tiruchirappalli" in dist_set:
                dist_set.add("Tiruchirapalli")
            if "Tiruchirapalli" in dist_set:
                dist_set.add("Tiruchirappalli")
            all_markets = all_markets[all_markets["district"].isin(dist_set)]

        # Filter markets that have prices and are accessible
        candidate_markets = []
        for _, mkt in all_markets.iterrows():
            m_id = mkt["market_id"]
            # Check if this market is eligible for at least one batch crop
            can_serve = any(self.loader.is_eligible(m_id, c) for c in batch_crops)
            if can_serve:
                candidate_markets.append(mkt)

        candidate_df = pd.DataFrame(candidate_markets)
        if candidate_df.empty:
            candidate_df = all_markets.head(max_markets)

        # Prioritize markets nearest to the selected batch sources unless search_all is True
        markets = candidate_df.copy() if search_all else self._select_nearest_markets(candidate_df, batch_sources, max_markets)
        market_ids = markets["market_id"].tolist()

        n_b = len(batch_ids)
        n_m = len(market_ids)

        revenue = np.zeros((n_b, n_m))
        transport_cost = np.zeros((n_b, n_m))
        late_penalty_mat = np.zeros((n_b, n_m))
        unsold_penalty_vec = np.zeros(n_b)
        feasible = np.zeros((n_b, n_m), dtype=bool)
        market_cap_kg = markets["capacity_kg"].to_numpy()

        # Use vehicle fleet representative (V001)
        vehicle = self.loader.vehicles.iloc[0]

        for bi, (_, batch) in enumerate(batches.iterrows()):
            src_id = batch["source_id"]
            c_id = batch["crop_id"]
            qty = float(batch["quantity_kg"])
            max_h = float(batch["max_delivery_hours"])

            # Unsold penalty for leaving batch at farm
            unsold_rate = self.loader.get_param("unsold_penalty", c_id)
            if unsold_rate <= 0:
                unsold_rate = 10.0
            unsold_penalty_vec[bi] = unsold_rate * qty

            for mi, (_, mkt) in enumerate(markets.iterrows()):
                m_id = mkt["market_id"]

                # 1. Eligibility check
                if not self.loader.is_eligible(m_id, c_id):
                    continue

                # 2. Travel distance and time
                dist_km = self.loader.get_travel_distance(src_id, m_id)
                tm_min = self.loader.get_travel_time(src_id, m_id)
                if dist_km is None or tm_min is None:
                    continue

                # 3. Freshness constraint
                travel_h = tm_min / 60.0
                load_h = self.loader.get_param("loading_time") / 60.0
                unload_h = self.loader.get_param("unloading_time") / 60.0
                total_h = travel_h + load_h + unload_h

                if total_h > max_h:
                    continue  # Freshness deadline violated

                feasible[bi, mi] = True

                # Revenue calculation
                price = self.loader.get_market_price(m_id, c_id)
                if price is None:
                    price = self.DEFAULT_PRICES.get(c_id, 25.0)
                revenue[bi, mi] = price * qty

                # Transport cost
                transport_cost[bi, mi] = self.loader.compute_transport_cost(dist_km, vehicle)

                # Late penalty (if within 2 hours of deadline)
                slack = max_h - total_h
                if slack < 2.0:
                    penalty_rate = self.loader.get_param("late_penalty", c_id)
                    late_penalty_mat[bi, mi] = penalty_rate * qty * max(0.0, 2.0 - slack)

        # Build variable index mappings
        pair_to_var: Dict[Tuple[int, int], int] = {}
        var_to_pair: Dict[int, Tuple[int, int]] = {}

        var_count = 0
        for b in range(n_b):
            for m in range(n_m):
                if prune_infeasible:
                    if feasible[b, m]:
                        pair_to_var[(b, m)] = var_count
                        var_to_pair[var_count] = (b, m)
                        var_count += 1
                else:
                    pair_to_var[(b, m)] = var_count
                    var_to_pair[var_count] = (b, m)
                    var_count += 1

        print(f"Problem formulated: {n_b} batches, {n_m} markets.")
        print(f"Feasible pairs: {feasible.sum()} / {n_b * n_m} -> {len(pair_to_var)} decision variables.")

        return ProblemInstance(
            batches=batches,
            markets=markets,
            revenue=revenue,
            transport_cost=transport_cost,
            late_penalty=late_penalty_mat,
            unsold_penalty=unsold_penalty_vec,
            feasible=feasible,
            market_capacity_kg=market_cap_kg,
            batch_ids=batch_ids,
            market_ids=market_ids,
            pair_to_var=pair_to_var,
            var_to_pair=var_to_pair,
        )

    def _select_nearest_markets(
        self, markets: pd.DataFrame, sources: np.ndarray, n: int
    ) -> pd.DataFrame:
        """Pick n markets nearest on average to given sources."""
        scores = []
        for _, row in markets.iterrows():
            m_id = row["market_id"]
            dists = [self.loader.get_travel_distance(s, m_id) for s in sources]
            valid_dists = [d for d in dists if d is not None]
            avg_d = np.mean(valid_dists) if valid_dists else 1e9
            scores.append((avg_d, row["market_id"]))

        scores.sort(key=lambda x: x[0])
        selected_ids = [m_id for _, m_id in scores[:n]]
        return markets[markets["market_id"].isin(selected_ids)].copy()


if __name__ == "__main__":
    loader = DataLoader()
    builder = ProblemBuilder(loader)
    p = builder.build(max_batches=4, max_markets=4, prune_infeasible=True)
    print("Feasible pairs:", p.feasible.sum())
    print("Profit gain matrix:\n", p.profit_gain)
