import csv
import openpyxl

# ─── Step 1: Extract unique TN crops from the Ministry file ──────────────────
wb = openpyxl.load_workbook(
    r'C:/Users/raaghav vel/.gemini/antigravity/brain/042dc5c3-c085-4021-9ee9-fd08382a841b/.user_uploaded/media_1790704635635.xlsx'
)
ws = wb.active
rows = list(ws.iter_rows(values_only=True))

# Aggregate TN crops at district level (Season != Total & has production > 0)
SKIP = {"Cereals", "Nutri/Coarse Cereals", "Shree Anna /Nutri Cereals",
        "Total Food Grains", "Total Pulses"}

tn_individual_crops = set()
in_tn = False
for row in rows:
    state, district, crop, season, area, prod, yld = row
    if state == "Tamil Nadu":
        in_tn = True
    elif state is not None:
        in_tn = False
    if in_tn and crop and str(crop).strip() not in SKIP and season != "Total":
        if prod and prod > 0:
            tn_individual_crops.add(str(crop).strip())

print("TN crops from govt file with production > 0:", sorted(tn_individual_crops))

# ─── Step 2: Define the full crop master ──────────────────────────────────────
# Merge govt cereals/pulses with vegetables & fruits typical to TN
# perishable_flag: 1 = spoils quickly, 0 = non-perishable
# crop_group: Cereal | Pulse | Vegetable | Fruit | Oilseed

CROPS = [
    # --- Cereals from govt file ---
    ("C001", "Rice",           "Cereal",    "kg",   0),
    ("C002", "Maize",          "Cereal",    "kg",   0),
    ("C003", "Ragi",           "Cereal",    "kg",   0),
    ("C004", "Jowar",          "Cereal",    "kg",   0),
    ("C005", "Bajra",          "Cereal",    "kg",   0),
    # --- Pulses from govt file ---
    ("C006", "Tur",            "Pulse",     "kg",   0),
    ("C007", "Urad",           "Pulse",     "kg",   0),
    ("C008", "Moong",          "Pulse",     "kg",   0),
    # --- Vegetables common in TN ---
    ("C009", "Tomato",         "Vegetable", "kg",   1),
    ("C010", "Onion",          "Vegetable", "kg",   0),
    ("C011", "Brinjal",        "Vegetable", "kg",   1),
    ("C012", "Chilli",         "Vegetable", "kg",   0),
    ("C013", "Bitter Gourd",   "Vegetable", "kg",   1),
    ("C014", "Drumstick",      "Vegetable", "kg",   1),
    ("C015", "Tapioca",        "Vegetable", "kg",   0),
    # --- Fruits common in TN ---
    ("C016", "Banana",         "Fruit",     "kg",   1),
    ("C017", "Mango",          "Fruit",     "kg",   1),
    ("C018", "Coconut",        "Fruit",     "nos",  0),
    # --- Oilseeds ---
    ("C019", "Groundnut",      "Oilseed",   "kg",   0),
    ("C020", "Sesame",         "Oilseed",   "kg",   0),
]

output_file = r"c:\III year\5th sem\quantum computing\capstone2\crop_master.csv"
with open(output_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["crop_id", "crop_name", "crop_group", "default_unit", "perishable_flag"])
    for row in CROPS:
        writer.writerow(row)

print(f"\nCrop master written: {output_file} ({len(CROPS)} crops)")

# ─── Step 3: Build a quick lookup for downstream fixes ────────────────────────
CROP_MAP = {name: cid for cid, name, *_ in CROPS}
print("\nCrop ID → Name mapping:")
for cid, name, *_ in CROPS:
    print(f"  {cid}: {name}")
