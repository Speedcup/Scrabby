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

# Find all guide tile elements
guide_tiles = soup.find_all("div", class_="guide-tile")
print(f"Found {len(guide_tiles)} guide tiles")

# Analyze the first guide tile in detail
if guide_tiles:
    first_tile = guide_tiles[0]
    
    # Save the HTML structure of the first tile
    with open('output/first_guide_tile.html', 'w', encoding='utf-8') as f:
        f.write(str(first_tile.prettify()))
    
    print("Saved first guide tile HTML to output/first_guide_tile.html")
    
    # Extract key elements
    title_element = first_tile.find("h3", class_="guide-tile__title")
    title = title_element.text.strip() if title_element else "No title found"
    print(f"Title: {title}")
    
    desc_element = first_tile.find("div", class_="guide-tile__description")
    desc = desc_element.text.strip() if desc_element else "No description found"
    print(f"Description: {desc}")
    
    tags_element = first_tile.find("div", class_="guide-tile__tags")
    tags = []
    if tags_element:
        tag_elements = tags_element.find_all("div", class_="guide-tile__tag")
        tags = [tag.text.strip() for tag in tag_elements]
    print(f"Tags: {tags}")
    
    # Look for video or thumbnail elements
    video_element = first_tile.find("iframe") or first_tile.find("video")
    video_url = ""
    if video_element:
        if video_element.get("src"):
            video_url = video_element["src"]
        elif video_element.get("data-src"):
            video_url = video_element["data-src"]
    print(f"Video URL: {video_url}")
    
    # Look for thumbnail
    thumbnail_element = first_tile.find("img")
    thumbnail_url = ""
    if thumbnail_element:
        if thumbnail_element.get("src"):
            thumbnail_url = thumbnail_element["src"]
        elif thumbnail_element.get("data-src"):
            thumbnail_url = thumbnail_element["data-src"]
    print(f"Thumbnail URL: {thumbnail_url}")
    
    # Look for author
    author_element = first_tile.find("div", class_="guide-tile__author")
    author = author_element.text.strip() if author_element else "No author found"
    print(f"Author: {author}")
    
    # Look for source URL
    link_element = first_tile.find("a", class_="guide-tile__link")
    source_url = ""
    if link_element and link_element.get("href"):
        source_url = link_element["href"]
    print(f"Source URL: {source_url}")
    
    # Check for preview element which might contain the thumbnail
    preview_element = first_tile.find("div", class_="guide-tile__preview")
    if preview_element:
        print("Found preview element")
        # Check for background image style
        if preview_element.get("style"):
            print(f"Preview style: {preview_element['style']}")
        
        # Check for img inside preview
        preview_img = preview_element.find("img")
        if preview_img:
            print(f"Preview img src: {preview_img.get('src', '')}")
            print(f"Preview img data-src: {preview_img.get('data-src', '')}")
    
    # Extract all attributes and elements for debugging
    all_elements = {}
    for element in first_tile.find_all():
        if element.name and element.get("class"):
            class_name = " ".join(element.get("class"))
            all_elements[class_name] = {
                "tag": element.name,
                "text": element.text.strip() if element.text else "",
                "attributes": {k: v for k, v in element.attrs.items() if k != "class"}
            }
    
    with open('output/first_tile_elements.json', 'w', encoding='utf-8') as f:
        json.dump(all_elements, f, indent=2)
    
    print("Saved all elements from first tile to output/first_tile_elements.json")
