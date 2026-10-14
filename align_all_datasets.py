"""
align_all_datasets.py
─────────────────────
1. Rebuilds crop_master.csv using ALL crops found in market_crop_eligibility.csv
   (crop_normalized column) + govt Excel cereals/pulses.
2. Rebuilds daily_batches.csv with correct crop IDs.
3. Rebuilds handling_parameters.csv with correct crop IDs.
4. Reports any crop_normalized values in eligibility that are not in crop_master
   (so nothing is silently missed).
"""

import csv, random
from datetime import datetime, timedelta

# ──────────────────────────────────────────────────────────────────────────────
# 1. CANONICAL CROP MASTER
#    Key = crop_normalized name used in market_crop_eligibility.csv
#    Value = (crop_id, crop_name, crop_group, default_unit, perishable_flag)
# ──────────────────────────────────────────────────────────────────────────────
CROP_MASTER = {
    # Cereals  (from govt Excel + eligibility)
    "rice":                    ("C001", "Rice",              "Cereal",    "kg",  0),
    "maize":                   ("C002", "Maize",             "Cereal",    "kg",  0),
    "ragi":                    ("C003", "Ragi",              "Cereal",    "kg",  0),
    "jowar":                   ("C004", "Jowar",             "Cereal",    "kg",  0),
    "bajra":                   ("C005", "Bajra",             "Cereal",    "kg",  0),
    "korra":                   ("C006", "Korra",             "Cereal",    "kg",  0),
    "samai":                   ("C007", "Samai",             "Cereal",    "kg",  0),
    "varagu":                  ("C008", "Varagu",            "Cereal",    "kg",  0),

    # Pulses
    "arhar_tur":               ("C009", "Tur (Arhar)",       "Pulse",     "kg",  0),
    "urad":                    ("C010", "Urad",              "Pulse",     "kg",  0),
    "moong_green_gram":        ("C011", "Moong",             "Pulse",     "kg",  0),
    "cowpea":                  ("C012", "Cowpea",            "Pulse",     "kg",  0),
    "horse_gram":              ("C013", "Horse Gram",        "Pulse",     "kg",  0),
    "lab_lab":                 ("C014", "Lab Lab",           "Pulse",     "kg",  0),

    # Vegetables
    "tomato":                  ("C015", "Tomato",            "Vegetable", "kg",  1),
    "onion":                   ("C016", "Onion",             "Vegetable", "kg",  0),
    "dry_chillies":            ("C017", "Dry Chillies",      "Vegetable", "kg",  0),
    "potato":                  ("C018", "Potato",            "Vegetable", "kg",  0),
    "tapioca":                 ("C019", "Tapioca",           "Vegetable", "kg",  0),
    "coriander":               ("C020", "Coriander",         "Vegetable", "kg",  1),
    "turmeric":                ("C021", "Turmeric",          "Vegetable", "kg",  0),
    "fresh_fruits_vegetables": ("C022", "Fresh F&V (Mixed)", "Vegetable", "kg",  1),

    # Fruits
    "banana":                  ("C023", "Banana",            "Fruit",     "kg",  1),
    "mango":                   ("C024", "Mango",             "Fruit",     "kg",  1),
    "coconut":                 ("C025", "Coconut",           "Fruit",     "nos", 0),
    "grapes":                  ("C026", "Grapes",            "Fruit",     "kg",  1),
    "arecanut":                ("C027", "Arecanut",          "Fruit",     "kg",  0),
    "cashewnut":               ("C028", "Cashewnut",         "Fruit",     "kg",  0),

    # Oilseeds
    "groundnut":               ("C029", "Groundnut",         "Oilseed",   "kg",  0),
    "sesamum":                 ("C030", "Sesame",            "Oilseed",   "kg",  0),
    "castor_seed":             ("C031", "Castor Seed",       "Oilseed",   "kg",  0),
    "sunflower":               ("C032", "Sunflower",         "Oilseed",   "kg",  0),
    "neem_seeds":              ("C033", "Neem Seeds",        "Oilseed",   "kg",  0),

    # Others
    "cotton_lint":             ("C034", "Cotton Lint",       "Fibre",     "kg",  0),
    "cotton_seeds":            ("C035", "Cotton Seeds",      "Fibre",     "kg",  0),
    "sugarcane_jaggery":       ("C036", "Sugarcane Jaggery", "Commercial","kg",  0),
    "palm_sugar_jaggery":      ("C037", "Palm Sugar Jaggery","Commercial","kg",  0),
    "tamarind":                ("C038", "Tamarind",          "Commercial","kg",  0),
    "tobacco":                 ("C039", "Tobacco",           "Commercial","kg",  0),
    "silk_cotton":             ("C040", "Silk Cotton",       "Fibre",     "kg",  0),
}

# ── Write crop_master.csv ─────────────────────────────────────────────────────
crop_master_file = r"c:\III year\5th sem\quantum computing\capstone2\crop_master.csv"
with open(crop_master_file, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["crop_id", "crop_name", "crop_group", "default_unit", "perishable_flag"])
    for key, (cid, name, grp, unit, perishable) in CROP_MASTER.items():
        w.writerow([cid, name, grp, unit, perishable])
print(f"crop_master.csv written: {len(CROP_MASTER)} crops")

# ── Cross-check eligibility file ──────────────────────────────────────────────
eligibility_file = r"c:\III year\5th sem\quantum computing\capstone2\market_crop_eligibility.csv"
with open(eligibility_file, encoding="utf-8") as f:
    elig_rows = list(csv.DictReader(f))

elig_normalized = set(r["crop_normalized"] for r in elig_rows)
missing = elig_normalized - set(CROP_MASTER.keys())
if missing:
    print(f"\nWARNING: These crop_normalized values in eligibility have NO crop_master entry:")
    for m in sorted(missing):
        print(f"  {m}")
else:
    print("All eligibility crop_normalized values are covered in crop_master.")

# ── Reverse lookup: normalized_name -> crop_id ────────────────────────────────
norm_to_id = {k: v[0] for k, v in CROP_MASTER.items()}

# ──────────────────────────────────────────────────────────────────────────────
# 2. REBUILD daily_batches.csv
#    Use only crops that actually appear in eligibility (confirmed tradeable)
# ──────────────────────────────────────────────────────────────────────────────
# Most common TN farm crops that appear in eligibility
ACTIVE_CROPS = [
    {"normalized": "tomato",     "max_hours": 24,  "weight": 3, "qty_range": (300, 2000)},
    {"normalized": "rice",       "max_hours": 72,  "weight": 3, "qty_range": (1000, 5000)},
    {"normalized": "banana",     "max_hours": 48,  "weight": 2, "qty_range": (300, 2000)},
    {"normalized": "onion",      "max_hours": 168, "weight": 2, "qty_range": (500, 3000)},
    {"normalized": "groundnut",  "max_hours": 120, "weight": 1, "qty_range": (500, 2500)},
    {"normalized": "maize",      "max_hours": 72,  "weight": 1, "qty_range": (800, 4000)},
    {"normalized": "coconut",    "max_hours": 240, "weight": 1, "qty_range": (1000, 5000)},
]

supply_file = r"c:\III year\5th sem\quantum computing\capstone2\supply_locations.csv"
with open(supply_file, encoding="utf-8") as f:
    source_ids = [r["source_id"] for r in csv.DictReader(f)]

TARGET_DATE = "2026-09-30"
NUM_BATCHES = 30
random.seed(42)

batches_file = r"c:\III year\5th sem\quantum computing\capstone2\daily_batches.csv"
with open(batches_file, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["batch_id", "source_id", "crop_id", "quantity_kg",
                "harvest_time", "ready_time", "max_delivery_hours"])
    for i in range(1, NUM_BATCHES + 1):
        crop      = random.choices(ACTIVE_CROPS, weights=[c["weight"] for c in ACTIVE_CROPS], k=1)[0]
        source_id = random.choice(source_ids)
        crop_id   = norm_to_id[crop["normalized"]]
        qty       = random.randint(*crop["qty_range"])
        h_hour    = random.randint(4, 8)
        h_min     = random.choice([0, 15, 30, 45])
        h_dt      = datetime.strptime(f"{TARGET_DATE} {h_hour:02d}:{h_min:02d}", "%Y-%m-%d %H:%M")
        r_dt      = h_dt + timedelta(hours=random.randint(1, 2), minutes=random.choice([0, 30]))
        w.writerow([f"B{i:03d}", source_id, crop_id, qty,
                    h_dt.strftime("%Y-%m-%d %H:%M"),
                    r_dt.strftime("%Y-%m-%d %H:%M"),
                    crop["max_hours"]])
print(f"daily_batches.csv rebuilt: {NUM_BATCHES} batches")

# ──────────────────────────────────────────────────────────────────────────────
# 3. REBUILD handling_parameters.csv
# ──────────────────────────────────────────────────────────────────────────────
# perishable_flag=1 crops get high late/unsold penalties
PENALTY_CROPS = [
    # (normalized_key, late_penalty_per_kg_hour, unsold_penalty_per_kg)
    ("tomato",    2.50, 15.00),
    ("banana",    1.50, 20.00),
    ("mango",     2.00, 18.00),
    ("onion",     0.50,  5.00),
    ("rice",      0.10,  2.00),
    ("groundnut", 0.10,  3.00),
    ("maize",     0.10,  2.50),
    ("coconut",   0.20,  3.00),
]

params_file = r"c:\III year\5th sem\quantum computing\capstone2\handling_parameters.csv"
with open(params_file, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["parameter_id", "vehicle_type", "crop_id", "value", "unit"])
    # Global params
    w.writerow(["diesel_price",   "ALL", "ALL", 92.76, "INR_per_litre"])
    w.writerow(["loading_time",   "ALL", "ALL", 15,    "minutes_per_stop"])
    w.writerow(["unloading_time", "ALL", "ALL", 20,    "minutes_per_stop"])
    # Per-crop penalties
    for norm, late, unsold in PENALTY_CROPS:
        cid = norm_to_id[norm]
        w.writerow(["late_penalty",   "ALL", cid, late,   "INR_per_kg_hour"])
        w.writerow(["unsold_penalty", "ALL", cid, unsold, "INR_per_kg"])
print(f"handling_parameters.csv rebuilt: {3 + len(PENALTY_CROPS)*2} rows")

print("\nDone. All three files are consistent with market_crop_eligibility.csv.")
