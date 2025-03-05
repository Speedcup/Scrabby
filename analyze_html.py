from bs4 import BeautifulSoup
import os
import json

# Create output directory if it doesn't exist
os.makedirs("output", exist_ok=True)

# Load the HTML file
with open('output/tracker_page.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Find all guide elements - try different class names
guide_elements = soup.find_all("div", class_="guide-tile")
print(f"Found {len(guide_elements)} elements with class 'guide-tile'")

# Try other potential class names
guide_card_elements = soup.find_all("div", class_="guide-card")
print(f"Found {len(guide_card_elements)} elements with class 'guide-card'")

# Let's find all div elements with class containing "guide"
guide_elements_any = soup.find_all("div", class_=lambda c: c and "guide" in c)
print(f"Found {len(guide_elements_any)} elements with class containing 'guide'")

# Print the class names of these elements
if guide_elements_any:
    print("Class names found:")
    class_names = set()
    for element in guide_elements_any:
        if element.get('class'):
            class_names.add(' '.join(element.get('class')))
    
    for class_name in class_names:
        print(f"  - {class_name}")

# Try to find video elements
video_elements = soup.find_all("video")
print(f"Found {len(video_elements)} video elements")

iframe_elements = soup.find_all("iframe")
print(f"Found {len(iframe_elements)} iframe elements")

img_elements = soup.find_all("img")
print(f"Found {len(img_elements)} img elements")

# Save the first few img elements to a file for inspection
if img_elements:
    img_data = []
    for i, img in enumerate(img_elements[:20]):  # First 20 images
        img_data.append({
            "index": i,
            "src": img.get("src", ""),
            "data-src": img.get("data-src", ""),
            "alt": img.get("alt", ""),
            "class": img.get("class", ""),
            "parent_class": img.parent.get("class", "") if img.parent else ""
        })
    
    with open('output/img_elements.json', 'w', encoding='utf-8') as f:
        json.dump(img_data, f, indent=2)
    
    print("Saved first 20 img elements to output/img_elements.json")
