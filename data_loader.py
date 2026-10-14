"""
data_loader.py
──────────────
High-performance loader and indexer for all 9 agricultural supply chain datasets.
Uses O(1) hash maps for travel matrix, prices, and crop eligibility.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional, Set
import warnings


class DataLoader:
    """Loads, validates, indexes and cross-references all 9 datasets."""

    CROP_NAME_TO_PRICE_KEY = {
        "rice": "rice", "tomato": "tomato", "onion": "onion",
        "banana": "banana", "coconut": "coconut", "groundnut": "groundnut",
        "mango": "mango", "tapioca": "tapioca", "brinjal": "brinjal",
        "potato": "potato", "grapes": "grapes", "drumstick": "drumstick",
        "dry chillies": "red_chilli", "coriander": "coriander_leaf",
        "cowpea": "cowpea", "bitter gourd": "bitter_gourd",
        "maize": "maize", "bajra": "bajra", "tur (arhar)": "arhar_tur",
        "urad": "urad", "moong": "moong_green_gram",
    }

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self._validate_files()

        # Load raw dataframes
        self.crops = self._load_crops()
        self.markets = self._load_markets()
        self.eligibility = self._load_eligibility()
        self.prices = self._load_prices()
        self.sources = self._load_sources()
        self.batches = self._load_batches()
        self.vehicles = self._load_vehicles()
        self.travel = self._load_travel()
        self.params = self._load_params()

        # Build fast O(1) lookups
        self._build_indices()

    def _validate_files(self):
        required = [
            "crop_master.csv", "daily_batches.csv", "handling_parameters.csv",
            "market_crop_eligibility.csv", "market_master_model_ready.csv",
            "supply_locations.csv", "travel_distance_time_matrix.csv",
            "vehicle_fleet.csv",
        ]
        for fname in required:
            p = self.data_dir / fname
            if not p.exists():
                raise FileNotFoundError(f"Required file not found: {p}")

    def _load_crops(self) -> pd.DataFrame:
        df = pd.read_csv(self.data_dir / "crop_master.csv")
        df["perishable_flag"] = df["perishable_flag"].astype(int)
        return df

    def _load_markets(self) -> pd.DataFrame:
        df = pd.read_csv(self.data_dir / "market_master_model_ready.csv")
        df["latitude_num"] = pd.to_numeric(df["latitude_num"], errors="coerce")
        df["longitude_num"] = pd.to_numeric(df["longitude_num"], errors="coerce")
        df = df.dropna(subset=["latitude_num", "longitude_num"]).copy()

        # Compute normalized capacity in KG
        cap_kg = []
        for _, row in df.iterrows():
            arr_t = row.get("estimated_daily_arrival_tonnes")
            proxy_val = row.get("capacity_proxy_value")
            proxy_unit = str(row.get("capacity_proxy_unit", ""))

            if pd.notna(arr_t) and float(arr_t) > 0:
                cap_kg.append(float(arr_t) * 1000.0)  # tonnes to kg
            elif pd.notna(proxy_val) and "shops" in proxy_unit:
                cap_kg.append(float(proxy_val) * 400.0)  # 400 kg per shop stall
            elif pd.notna(proxy_val) and float(proxy_val) > 0:
                cap_kg.append(float(proxy_val) * 100.0)  # bags/quintals estimate
            else:
                cap_kg.append(15000.0)  # default 15 tonnes
        df["capacity_kg"] = cap_kg
        return df

    def _load_eligibility(self) -> pd.DataFrame:
        df = pd.read_csv(self.data_dir / "market_crop_eligibility.csv")
        df["eligibility"] = pd.to_numeric(df["eligibility"], errors="coerce").fillna(0).astype(int)
        return df

    def _load_prices(self) -> pd.DataFrame:
        price_files = list(self.data_dir.glob("*daily_prices*.csv"))
        if not price_files:
            warnings.warn("No daily price file found. Using empty DataFrame.")
            return pd.DataFrame()
        df = pd.read_csv(price_files[0])
        df["estimated_mid_price_rs_per_kg"] = pd.to_numeric(
            df["estimated_mid_price_rs_per_kg"], errors="coerce"
        )
        return df

    def _load_sources(self) -> pd.DataFrame:
        return pd.read_csv(self.data_dir / "supply_locations.csv")

    def _load_batches(self) -> pd.DataFrame:
        df = pd.read_csv(self.data_dir / "daily_batches.csv")
        df["harvest_time"] = pd.to_datetime(df["harvest_time"])
        df["ready_time"] = pd.to_datetime(df["ready_time"])
        return df

    def _load_vehicles(self) -> pd.DataFrame:
        return pd.read_csv(self.data_dir / "vehicle_fleet.csv")

    def _load_travel(self) -> pd.DataFrame:
        df = pd.read_csv(self.data_dir / "travel_distance_time_matrix.csv")
        df["distance_km"] = pd.to_numeric(df["distance_km"], errors="coerce")
        df["travel_minutes"] = pd.to_numeric(df["travel_minutes"], errors="coerce")
        return df

    def _load_params(self) -> pd.DataFrame:
        return pd.read_csv(self.data_dir / "handling_parameters.csv")

    def _build_indices(self):
        """Construct instant O(1) in-memory indices."""
        # 1. Travel lookup (origin, destination) -> (dist_km, time_min)
        self.travel_dict: Dict[Tuple[str, str], Tuple[float, float]] = {
            (o, d): (dist, tm)
            for o, d, dist, tm in zip(
                self.travel["origin_id"],
                self.travel["destination_id"],
                self.travel["distance_km"],
                self.travel["travel_minutes"],
            )
        }

        # 2. Crop dictionaries
        self.crop_id_to_name: Dict[str, str] = dict(
            zip(self.crops["crop_id"], self.crops["crop_name"])
        )
        self.crop_name_to_id: Dict[str, str] = {
            v.lower(): k for k, v in self.crop_id_to_name.items()
        }
        self.crop_id_to_perishable: Dict[str, bool] = dict(
            zip(self.crops["crop_id"], self.crops["perishable_flag"].astype(bool))
        )
        self.crop_id_to_group: Dict[str, str] = dict(
            zip(self.crops["crop_id"], self.crops["crop_group"])
        )

        # 3. Market price lookup (market_id, crop_key) -> price
        self.price_dict: Dict[Tuple[str, str], float] = {}
        if not self.prices.empty:
            for m_id, c_key, price in zip(
                self.prices["market_id"],
                self.prices["crop_key"],
                self.prices["estimated_mid_price_rs_per_kg"],
            ):
                if pd.notna(price) and price > 0:
                    self.price_dict[(m_id, str(c_key).lower())] = float(price)

        # 4. Market eligibility lookup
        # Set of (market_id, crop_normalized)
        self.eligible_pairs: Set[Tuple[str, str]] = set()
        self.general_fresh_markets: Set[str] = set()
        for m_id, c_norm, el in zip(
            self.eligibility["market_id"],
            self.eligibility["crop_normalized"],
            self.eligibility["eligibility"],
        ):
            if el == 1:
                norm = str(c_norm).lower().strip()
                if norm == "fresh_fruits_vegetables":
                    self.general_fresh_markets.add(m_id)
                else:
                    self.eligible_pairs.add((m_id, norm))

        # 5. Handling parameter lookup (param_id, crop_id) -> value
        self.param_dict: Dict[Tuple[str, str], float] = {
            (p_id, c_id): float(val)
            for p_id, c_id, val in zip(
                self.params["parameter_id"],
                self.params["crop_id"],
                self.params["value"],
            )
        }

    # ── High Performance Query Methods ────────────────────────────────────

    def get_param(self, param_id: str, crop_id: str = "ALL") -> float:
        """Get handling parameter with fallback to 'ALL'."""
        val = self.param_dict.get((param_id, crop_id))
        if val is not None:
            return val
        return self.param_dict.get((param_id, "ALL"), 0.0)

    def get_travel_time(self, origin: str, destination: str) -> Optional[float]:
        """O(1) lookup for travel time in minutes."""
        pair = self.travel_dict.get((origin, destination))
        return pair[1] if pair else None

    def get_travel_distance(self, origin: str, destination: str) -> Optional[float]:
        """O(1) lookup for travel distance in km."""
        pair = self.travel_dict.get((origin, destination))
        return pair[0] if pair else None

    def get_market_price(self, market_id: str, crop_id: str) -> Optional[float]:
        """O(1) lookup for crop price at market in INR/kg."""
        crop_name = self.crop_id_to_name.get(crop_id, "").lower()
        price_key = self.CROP_NAME_TO_PRICE_KEY.get(crop_name, crop_name)
        return self.price_dict.get((market_id, price_key))

    def is_eligible(self, market_id: str, crop_id: str) -> bool:
        """O(1) check if market accepts crop."""
        crop_name = self.crop_id_to_name.get(crop_id, "").lower()
        price_key = self.CROP_NAME_TO_PRICE_KEY.get(crop_name, crop_name)

        # Specific crop acceptance
        if (market_id, crop_name) in self.eligible_pairs or (market_id, price_key) in self.eligible_pairs:
            return True

        # Fresh produce general market (Uzhavar Santhai accepts fruits/veggies/perishables)
        if market_id in self.general_fresh_markets:
            is_perishable = self.crop_id_to_perishable.get(crop_id, False)
            group = self.crop_id_to_group.get(crop_id, "")
            if is_perishable or group in ["Vegetable", "Fruit"]:
                return True

        return False

    def compute_transport_cost(self, distance_km: float, vehicle_row: pd.Series) -> float:
        """Compute trip cost: fixed + fuel cost."""
        diesel_price = self.get_param("diesel_price")
        mileage = float(vehicle_row["mileage_km_per_litre"])
        fixed = float(vehicle_row["fixed_cost_per_trip"])
        fuel_cost = (distance_km / mileage) * diesel_price if mileage > 0 else 0.0
        return fixed + fuel_cost

    def summary(self):
        """Print data overview."""
        print("=" * 60)
        print("  AGRICULTURAL SUPPLY CHAIN - DATA SUMMARY")
        print("=" * 60)
        print(f"  Crops in master        : {len(self.crops)}")
        print(f"  Markets                : {len(self.markets)}")
        print(f"  Eligibility records    : {len(self.eligibility)}")
        print(f"  Price observations     : {len(self.prices)}")
        print(f"  Supply locations       : {len(self.sources)}")
        print(f"  Daily batches          : {len(self.batches)}")
        print(f"  Vehicles               : {len(self.vehicles)}")
        print(f"  Travel matrix entries  : {len(self.travel_dict):,}")
        print(f"  Diesel price           : Rs {self.get_param('diesel_price')}/L")
        print("=" * 60)


if __name__ == "__main__":
    loader = DataLoader()
    loader.summary()
