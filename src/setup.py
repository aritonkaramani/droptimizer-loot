import requests
import os
import json

print("=== Droptimizer Loot Setup ===\n")

# --- Prompts ---
try:
    raw_ids = input("Zone ID(s) for the raid(s) to sim (comma-separated): ").strip()
    raid_zone_ids = [int(x.strip()) for x in raw_ids.split(",") if x.strip()]
    if not raid_zone_ids:
        print("Error: At least one Zone ID must be provided.")
        exit(1)
except ValueError:
    print("Error: All Zone IDs must be integers.")
    exit(1)

try:
    catalyst_expansion = int(input("Expansion number for catalyst items (e.g. 11 for the new raid): ").strip())
except ValueError:
    print("Error: Expansion number must be an integer.")
    exit(1)

# --- Paths ---
script_dir = os.path.dirname(os.path.abspath(__file__))
static_data_dir = os.path.abspath(os.path.join(script_dir, '..', 'static_data'))

os.makedirs(static_data_dir, exist_ok=True)
os.makedirs(os.path.join(script_dir, 'heroic_data'), exist_ok=True)
os.makedirs(os.path.join(script_dir, 'mythic_data'), exist_ok=True)
os.makedirs(os.path.join(script_dir, 'normal_data'), exist_ok=True)
os.makedirs(os.path.join(script_dir, 'raidsims'), exist_ok=True)

INVENTORY_SLOT = {1: "Head", 3: "Shoulder", 5: "Chest", 7: "Legs", 10: "Hands", 20: "Chest"}
CLASS_NAME = {
    1: "Warrior", 2: "Paladin", 3: "Hunter", 4: "Rogue", 5: "Priest",
    6: "Death Knight", 7: "Shaman", 8: "Mage", 9: "Warlock",
    10: "Monk", 11: "Druid", 12: "Demon Hunter", 13: "Evoker"
}

# -------------------------------------------------------
# Step 1: Download static data
# -------------------------------------------------------
print("\n--- Step 1: Downloading static data ---")

files_to_download = {
    "https://www.raidbots.com/static/data/live/item-conversions.json": "catalyst_items.json",
    "https://www.raidbots.com/static/data/live/equippable-items.json": "encounter-items.json",
    "https://www.raidbots.com/static/data/live/instances.json": "instances.json"
}

for url, filename in files_to_download.items():
    output_file = os.path.join(static_data_dir, filename)
    try:
        response = requests.get(url, timeout=30)
    except requests.exceptions.RequestException as e:
        print(f"Network error downloading {filename}: {e}")
        exit(1)

    if response.status_code != 200:
        print(f"Failed to download {filename}. Status code: {response.status_code}")
        exit(1)

    if filename == "instances.json":
        try:
            instances = response.json()
            filtered = [inst for inst in instances if inst.get('id') in raid_zone_ids]
            if not filtered:
                print(f"No instances found with ids: {raid_zone_ids}")
                exit(1)
            with open(output_file, 'w') as f:
                json.dump(filtered, f, indent=4)
            found_ids = [inst['id'] for inst in filtered]
            print(f"Saved instances {found_ids} to instances.json")

            all_items_file = os.path.join(static_data_dir, "encounter-items.json")
            if os.path.exists(all_items_file):
                with open(all_items_file, 'r') as item_file:
                    all_items = json.load(item_file)
                filtered_items = [
                    item for item in all_items
                    if any(src.get("instanceId") in raid_zone_ids for src in item.get("sources", []))
                ]
                with open(all_items_file, 'w') as out:
                    json.dump(filtered_items, out, indent=4)
                print(f"Filtered encounter-items.json to {len(filtered_items)} items")
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            exit(1)

    elif filename == "catalyst_items.json":
        try:
            catalyst_data = response.json()
            matching_items = []
            for segment in catalyst_data.values():
                for item in segment.get("items", []):
                    if item.get("expansion") != catalyst_expansion:
                        continue
                    slot = INVENTORY_SLOT.get(item.get("inventoryType"))
                    if not slot:
                        continue
                    classes = [CLASS_NAME[c] for c in item.get("allowableClasses", []) if c in CLASS_NAME]
                    class_str = ", ".join(classes) if classes else "Unknown"
                    matching_items.append({"name": f"Tier {slot}: {class_str}", "id": item.get("id")})
            if not matching_items:
                print(f"No catalyst items found for expansion {catalyst_expansion}.")
            else:
                with open(output_file, 'w') as f:
                    json.dump({"items": matching_items}, f, indent=4)
                print(f"Saved {len(matching_items)} catalyst items to catalyst_items.json")
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            exit(1)

    else:
        with open(output_file, 'w') as f:
            f.write(response.text)
        print(f"Downloaded {filename}")

# -------------------------------------------------------
# Step 2: Build formatted_itemdata.json
# -------------------------------------------------------
print("\n--- Step 2: Building formatted_itemdata.json ---")

encounter_items_path = os.path.join(static_data_dir, "encounter-items.json")
instances_path = os.path.join(static_data_dir, "instances.json")

with open(encounter_items_path, "r") as f:
    json_data = json.load(f)

with open(instances_path, "r") as f:
    zone_data = json.load(f)

if isinstance(zone_data, dict):
    zone_data = [zone_data]

valid_encounter_ids = set()
for instance in zone_data:
    for entry in instance.get("encounters", []):
        valid_encounter_ids.add(entry["id"])

all_drops = []
for item in json_data:
    sources_data = item.get("sources", [{}])[0]
    encounter_id = sources_data.get("encounterId")
    if encounter_id in valid_encounter_ids:
        all_drops.append({"name": item.get("name"), "id": item.get("id")})

print(f"Found {len(all_drops)} boss drops")

catalyst_file_path = os.path.join(static_data_dir, "catalyst_items.json")
if os.path.exists(catalyst_file_path):
    with open(catalyst_file_path, "r") as f:
        catalyst_items = json.load(f).get("items", [])
    all_drops.extend(catalyst_items)
    print(f"Appended {len(catalyst_items)} catalyst items")

formatted_output_path = os.path.join(static_data_dir, "formatted_itemdata.json")
with open(formatted_output_path, "w") as f:
    json.dump({"drops": all_drops}, f, indent=4)

print(f"\n=== Setup complete! {len(all_drops)} total items in formatted_itemdata.json ===")
print("You can now run gatherData.py to collect player sim data.")
