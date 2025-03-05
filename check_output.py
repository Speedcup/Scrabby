import json

# Load the data
with open('output/tracker_clips.json', 'r') as f:
    data = json.load(f)

# Check the structure
print(f"Version: {data.get('version')}")
print(f"Data length: {len(data.get('data', []))}")
print("\nFirst clip:")
print(json.dumps(data.get('data', [])[0] if data.get('data') else {}, indent=2))
