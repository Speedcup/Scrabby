import json

# Load the data
with open('output/tracker_clips.json', 'r') as f:
    data = json.load(f)

# Check for attack/defense tags
attack_defense_count = 0
for clip in data:
    for tag in clip['tags']:
        if tag.lower() in ['attack', 'defense']:
            attack_defense_count += 1
            break

print(f'Found {attack_defense_count} clips with attack/defense tags out of {len(data)} total clips')

# Print the first 5 clips' tags
print("\nFirst 5 clips' tags:")
for i in range(min(5, len(data))):
    print(f"Clip {i+1}: {data[i]['tags']}")
