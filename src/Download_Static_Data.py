import requests
import os
import json

# --- Prompt for raid zone ID ---
try:
    raid_zone_id = int(input("Please type in Zone ID for the raid you wish to sim items from: ").strip())
except ValueError:
    print("Error: Raid Zone ID must be an integer.")
    exit(1)

# --- Prompt for catalyst segment ID ---
try:
    catalyst_segment = input("For Catalyst items, write 8 for Nerub-ar Palace, 10 for Undermine or assumingly 11 for new raid: ").strip()
    if catalyst_segment not in ["8", "10", "11"]:
        print("Error: Catalyst segment must be 8, 10, or 11.")
        exit(1)
except Exception as e:
    print("Error processing catalyst input:", e)
    exit(1)

# --- File URLs ---
files_to_download = {
    "https://www.raidbots.com/static/data/live/item-conversions.json": "catalyst_items.json",
    "https://www.raidbots.com/static/data/live/equippable-items.json": "encounter-items.json",
    "https://www.raidbots.com/static/data/live/instances.json": "instances.json"
}

# --- Output path ---
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static_data'))
os.makedirs(output_dir, exist_ok=True)

# --- Download and process ---
for url, filename in files_to_download.items():
    output_file = os.path.join(output_dir, filename)
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to download {filename}. Status code: {response.status_code}")
        continue

    # --- Filter instances ---
    if filename == "instances.json":
        try:
            instances = response.json()
            filtered = [inst for inst in instances if inst.get('id') == raid_zone_id]
            if not filtered:
                print(f"No instance found with id: {raid_zone_id}")
                continue

            # Save the matching instance
            with open(output_file, 'w') as f:
                json.dump(filtered[0], f, indent=4)
            print(f"Filtered instance with id {raid_zone_id} saved to instances.json")

            # Filter all_items.json based on instanceId
            all_items_file = os.path.join(output_dir, "encounter-items.json")
            if os.path.exists(all_items_file):
                with open(all_items_file, 'r') as item_file:
                    all_items = json.load(item_file)

                filtered_items = []
                for item in all_items:
                    for source in item.get("sources", []):
                        if source.get("instanceId") == raid_zone_id:
                            filtered_items.append(item)
                            break

                with open(all_items_file, 'w') as out:
                    json.dump(filtered_items, out, indent=4)

                print(f"Filtered all_items.json to {len(filtered_items)} items from instance {raid_zone_id}")

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # --- Filter catalyst items ---
    elif filename == "catalyst_items.json":
        try:
            catalyst_data = response.json()
            if catalyst_segment not in catalyst_data:
                print(f"Segment '{catalyst_segment}' not found in catalyst data.")
                continue
            reduced_data = {catalyst_segment: catalyst_data[catalyst_segment]}
            with open(output_file, 'w') as f:
                json.dump(reduced_data, f, indent=4)
            print(f"Catalyst items for segment {catalyst_segment} saved to catalyst_items.json")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # --- Just save unfiltered files ---
    else:
        with open(output_file, 'w') as f:
            f.write(response.text)
        print(f"File downloaded successfully as {filename} in static_data.")
