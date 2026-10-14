import csv
import os

locations = [
    # Coimbatore
    {"source_name": "Kinathukadavu", "district": "Coimbatore", "latitude": 10.8211, "longitude": 77.0210},
    {"source_name": "Thondamuthur", "district": "Coimbatore", "latitude": 10.9984, "longitude": 76.8277},
    {"source_name": "Annur", "district": "Coimbatore", "latitude": 11.2307, "longitude": 77.1066},
    {"source_name": "Sulur", "district": "Coimbatore", "latitude": 11.0264, "longitude": 77.1264},
    # Thanjavur
    {"source_name": "Papanasam", "district": "Thanjavur", "latitude": 10.9328, "longitude": 79.2784},
    {"source_name": "Kumbakonam", "district": "Thanjavur", "latitude": 10.9601, "longitude": 79.3845},
    {"source_name": "Orathanadu", "district": "Thanjavur", "latitude": 10.6278, "longitude": 79.2562},
    {"source_name": "Pattukkottai", "district": "Thanjavur", "latitude": 10.4285, "longitude": 79.3179},
    # Dindigul
    {"source_name": "Oddanchatram", "district": "Dindigul", "latitude": 10.4727, "longitude": 77.7554},
    {"source_name": "Palani", "district": "Dindigul", "latitude": 10.4475, "longitude": 77.5218},
    {"source_name": "Vedasandur", "district": "Dindigul", "latitude": 10.5367, "longitude": 77.9472},
    {"source_name": "Nilakottai", "district": "Dindigul", "latitude": 10.1654, "longitude": 77.8595},
    # Theni
    {"source_name": "Cumbum", "district": "Theni", "latitude": 9.7344, "longitude": 77.2807},
    {"source_name": "Bodinayakkanur", "district": "Theni", "latitude": 10.0125, "longitude": 77.3475},
    {"source_name": "Periyakulam", "district": "Theni", "latitude": 10.1209, "longitude": 77.5463},
    {"source_name": "Uthamapalayam", "district": "Theni", "latitude": 9.8153, "longitude": 77.3298},
    # Erode
    {"source_name": "Gobichettipalayam", "district": "Erode", "latitude": 11.4556, "longitude": 77.4391},
    {"source_name": "Sathyamangalam", "district": "Erode", "latitude": 11.5034, "longitude": 77.2389},
    {"source_name": "Bhavani", "district": "Erode", "latitude": 11.4428, "longitude": 77.6778},
    {"source_name": "Perundurai", "district": "Erode", "latitude": 11.2743, "longitude": 77.5815},
    # Krishnagiri
    {"source_name": "Hosur", "district": "Krishnagiri", "latitude": 12.7409, "longitude": 77.8253},
    {"source_name": "Denkanikottai", "district": "Krishnagiri", "latitude": 12.5273, "longitude": 77.7950},
    {"source_name": "Pochampalli", "district": "Krishnagiri", "latitude": 12.3392, "longitude": 78.3582},
    {"source_name": "Uthangarai", "district": "Krishnagiri", "latitude": 12.2646, "longitude": 78.5350},
    # Salem
    {"source_name": "Attur", "district": "Salem", "latitude": 11.5956, "longitude": 78.6015},
    {"source_name": "Mettur", "district": "Salem", "latitude": 11.7850, "longitude": 77.8021},
    {"source_name": "Omalur", "district": "Salem", "latitude": 11.7375, "longitude": 78.0583},
    {"source_name": "Edappadi", "district": "Salem", "latitude": 11.5833, "longitude": 77.8333},
    # Madurai
    {"source_name": "Melur", "district": "Madurai", "latitude": 10.0381, "longitude": 78.3307},
    {"source_name": "Usilampatti", "district": "Madurai", "latitude": 9.9678, "longitude": 77.7981},
    {"source_name": "Vadipatti", "district": "Madurai", "latitude": 10.0886, "longitude": 77.9626},
    {"source_name": "Thirumangalam", "district": "Madurai", "latitude": 9.8197, "longitude": 77.9897},
    # Trichy
    {"source_name": "Lalgudi", "district": "Tiruchirappalli", "latitude": 10.8710, "longitude": 78.8237},
    {"source_name": "Manapparai", "district": "Tiruchirappalli", "latitude": 10.6074, "longitude": 78.4168},
    {"source_name": "Musiri", "district": "Tiruchirappalli", "latitude": 10.9416, "longitude": 78.4503},
    {"source_name": "Thuraiyur", "district": "Tiruchirappalli", "latitude": 11.1444, "longitude": 78.5992}
]

output_file = r"c:\III year\5th sem\quantum computing\capstone2\supply_locations.csv"

with open(output_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    # Header
    writer.writerow(["source_id", "source_name", "source_type", "district", "latitude", "longitude"])
    
    # Rows
    for idx, loc in enumerate(locations, start=1):
        source_id = f"S{idx:03d}"
        source_name = loc["source_name"] + " Collection Centre"
        source_type = "collection_centre"
        writer.writerow([source_id, source_name, source_type, loc["district"], loc["latitude"], loc["longitude"]])

print(f"Successfully created {output_file} with {len(locations)} locations.")
