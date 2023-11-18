import json
import os

# Determine the path for the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate up one level to the parent folder
parent_dir = os.path.dirname(script_dir)

# Create a new folder named "static_data" if it doesn't exist
output_folder = os.path.join(parent_dir, "static_data")
os.makedirs(output_folder, exist_ok=True)

# Determine the path for the input JSON file in the same folder as the script
input_file_path = os.path.join(parent_dir, "static_data/encounter-items.json")

# Determine the path for the zone data JSON file
zone_data_file_path = os.path.join(parent_dir, "static_data/instances.json")

# Check if the input JSON files exist
if not os.path.exists(input_file_path) or not os.path.exists(zone_data_file_path):
    print("Input file(s) do not exist.")
    exit()

# Read data from the input JSON file
with open(input_file_path, "r") as input_file:
    json_data = json.load(input_file)

# Read the zone data from the zone data JSON file
with open(zone_data_file_path, "r") as zone_data_file:
    zone_data = json.load(zone_data_file)

# Create a set of valid encounterIds from zone_data
valid_encounter_ids = set(entry["id"] for entry in zone_data["encounters"])

# Create a dictionary to map encounterId to zone names
zone_mapping = {entry["id"]: entry["name"] for entry in zone_data["encounters"]}

# Create a dictionary to group data by encounter name
encounter_data = { "drops": [] }


for item in json_data:
    sources_data = item.get("sources", [{}])[0]
    encounter_id = sources_data.get("encounterId", None)
    if encounter_id is not None and encounter_id in valid_encounter_ids:
        formatted_item = {
            "name": item.get("name", None),
            "id": item.get("id", None),
        }
        if encounter_id is not None:
            encounter_data["drops"].append(formatted_item)

# Write the grouped data to a single JSON file
output_file_path = os.path.join(output_folder, "formatted_itemdata.json")
with open(output_file_path, "w") as output_file:
    json.dump(encounter_data, output_file, indent=4)

print(f"Data written to {output_file_path}")
