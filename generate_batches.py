import csv, random
from datetime import datetime, timedelta

# New Crop ID mapping (based on crop_master.csv)
# C009=Tomato, C010=Onion, C011=Brinjal, C001=Rice, C016=Banana
CROPS = [
    {"id": "C009", "name": "Tomato",   "max_delivery_hours": 24,  "perishable": True},
    {"id": "C001", "name": "Rice",     "max_delivery_hours": 72,  "perishable": False},
    {"id": "C016", "name": "Banana",   "max_delivery_hours": 48,  "perishable": True},
    {"id": "C010", "name": "Onion",    "max_delivery_hours": 168, "perishable": False},
    {"id": "C011", "name": "Brinjal",  "max_delivery_hours": 36,  "perishable": True},
]

TARGET_DATE = "2026-09-30"
NUM_BATCHES = 30

supply_file = r"c:\III year\5th sem\quantum computing\capstone2\supply_locations.csv"
source_ids = []
with open(supply_file, mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        source_ids.append(row["source_id"])

random.seed(42)  # for reproducibility

output_file = r"c:\III year\5th sem\quantum computing\capstone2\daily_batches.csv"
with open(output_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["batch_id", "source_id", "crop_id", "quantity_kg",
                     "harvest_time", "ready_time", "max_delivery_hours"])
    for i in range(1, NUM_BATCHES + 1):
        batch_id  = f"B{i:03d}"
        source_id = random.choice(source_ids)
        crop      = random.choices(CROPS, weights=[3, 2, 2, 2, 1], k=1)[0]

        # Quantity by crop type
        if crop["name"] == "Rice":
            qty = random.randint(1000, 5000)
        elif not crop["perishable"]:
            qty = random.randint(500, 3000)
        else:
            qty = random.randint(300, 2000)

        harvest_hour = random.randint(4, 8)
        harvest_min  = random.choice([0, 15, 30, 45])
        harvest_dt   = datetime.strptime(f"{TARGET_DATE} {harvest_hour:02d}:{harvest_min:02d}", "%Y-%m-%d %H:%M")
        ready_dt     = harvest_dt + timedelta(hours=random.randint(1, 2), minutes=random.choice([0, 30]))

        writer.writerow([
            batch_id, source_id, crop["id"], qty,
            harvest_dt.strftime("%Y-%m-%d %H:%M"),
            ready_dt.strftime("%Y-%m-%d %H:%M"),
            crop["max_delivery_hours"]
        ])

print(f"daily_batches.csv updated with correct crop IDs ({NUM_BATCHES} batches).")
