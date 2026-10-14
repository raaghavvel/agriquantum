import csv
import random

# Read available supply locations to set valid start_source_ids
supply_file = r"c:\III year\5th sem\quantum computing\capstone2\supply_locations.csv"
source_ids = []

try:
    with open(supply_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            source_ids.append(row["source_id"])
except FileNotFoundError:
    print(f"Error: {supply_file} not found. Using dummy S001-S010 instead.")
    source_ids = [f"S{i:03d}" for i in range(1, 11)]

# Vehicle definitions based on real commonly used Indian trucks
VEHICLE_MODELS = [
    {
        "type": "Tata Ace (Mini Truck)",
        "capacity_kg": 1000,
        "mileage_kmpl": 15,
        "fixed_cost": 400
    },
    {
        "type": "Mahindra Bolero Pik-Up (Light Truck)",
        "capacity_kg": 1500,
        "mileage_kmpl": 13,
        "fixed_cost": 600
    },
    {
        "type": "Tata 407 (Light Commercial Vehicle)",
        "capacity_kg": 3000,
        "mileage_kmpl": 10,
        "fixed_cost": 1000
    },
    {
        "type": "Eicher Pro 1049 (Light Truck)",
        "capacity_kg": 4900,
        "mileage_kmpl": 8,
        "fixed_cost": 1300
    },
    {
        "type": "Tata 1109 (Medium Truck)",
        "capacity_kg": 7000,
        "mileage_kmpl": 6,
        "fixed_cost": 1800
    }
]

NUM_VEHICLES = 8
output_file = r"c:\III year\5th sem\quantum computing\capstone2\vehicle_fleet.csv"

with open(output_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["vehicle_id", "vehicle_type", "capacity_kg", "mileage_km_per_litre", "fixed_cost_per_trip", "start_source_id", "available_from", "available_until"])
    
    for i in range(1, NUM_VEHICLES + 1):
        v_id = f"V{i:03d}"
        
        # Pick a random model, leaning towards smaller trucks which are more common for farm-to-market
        model = random.choices(
            VEHICLE_MODELS, 
            weights=[3, 3, 2, 1, 1], # Weights favoring smaller trucks
            k=1
        )[0]
        
        # Assign a random depot/starting location
        start_source = random.choice(source_ids)
        
        # Typical availability for farm transport
        available_from = "04:00" if model["capacity_kg"] > 3000 else "05:00"
        available_until = "22:00" if model["capacity_kg"] > 3000 else "18:00"
        
        writer.writerow([
            v_id,
            model["type"],
            model["capacity_kg"],
            model["mileage_kmpl"],
            model["fixed_cost"],
            start_source,
            available_from,
            available_until
        ])

print(f"Successfully created {output_file} with {NUM_VEHICLES} realistic vehicles.")
