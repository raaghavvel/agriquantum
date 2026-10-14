import csv

# Updated to use crop IDs from crop_master.csv
# C009=Tomato, C001=Rice, C016=Banana, C010=Onion, C011=Brinjal

parameters = [
    # --- Global cost parameters ---
    {"parameter_id": "diesel_price",    "vehicle_type": "ALL", "crop_id": "ALL",  "value": 92.76, "unit": "INR_per_litre"},
    {"parameter_id": "loading_time",    "vehicle_type": "ALL", "crop_id": "ALL",  "value": 15,    "unit": "minutes_per_stop"},
    {"parameter_id": "unloading_time",  "vehicle_type": "ALL", "crop_id": "ALL",  "value": 20,    "unit": "minutes_per_stop"},

    # --- Late-delivery penalties (INR per kg per hour delay) ---
    {"parameter_id": "late_penalty",    "vehicle_type": "ALL", "crop_id": "C009", "value": 2.50,  "unit": "INR_per_kg_hour"},  # Tomato
    {"parameter_id": "late_penalty",    "vehicle_type": "ALL", "crop_id": "C011", "value": 2.00,  "unit": "INR_per_kg_hour"},  # Brinjal
    {"parameter_id": "late_penalty",    "vehicle_type": "ALL", "crop_id": "C016", "value": 1.50,  "unit": "INR_per_kg_hour"},  # Banana
    {"parameter_id": "late_penalty",    "vehicle_type": "ALL", "crop_id": "C010", "value": 0.50,  "unit": "INR_per_kg_hour"},  # Onion
    {"parameter_id": "late_penalty",    "vehicle_type": "ALL", "crop_id": "C001", "value": 0.10,  "unit": "INR_per_kg_hour"},  # Rice

    # --- Unsold / spoilage penalties (INR per kg if produce never reaches market) ---
    {"parameter_id": "unsold_penalty",  "vehicle_type": "ALL", "crop_id": "C009", "value": 15.00, "unit": "INR_per_kg"},  # Tomato
    {"parameter_id": "unsold_penalty",  "vehicle_type": "ALL", "crop_id": "C011", "value": 12.00, "unit": "INR_per_kg"},  # Brinjal
    {"parameter_id": "unsold_penalty",  "vehicle_type": "ALL", "crop_id": "C016", "value": 25.00, "unit": "INR_per_kg"},  # Banana
    {"parameter_id": "unsold_penalty",  "vehicle_type": "ALL", "crop_id": "C010", "value": 5.00,  "unit": "INR_per_kg"},  # Onion
    {"parameter_id": "unsold_penalty",  "vehicle_type": "ALL", "crop_id": "C001", "value": 2.00,  "unit": "INR_per_kg"},  # Rice
]

output_file = r"c:\III year\5th sem\quantum computing\capstone2\handling_parameters.csv"
with open(output_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["parameter_id", "vehicle_type", "crop_id", "value", "unit"])
    for p in parameters:
        writer.writerow([p["parameter_id"], p["vehicle_type"], p["crop_id"], p["value"], p["unit"]])

print(f"handling_parameters.csv updated with correct crop IDs ({len(parameters)} rows).")
