import cloudscraper
import os

# Create output directory if it doesn't exist
os.makedirs("output", exist_ok=True)

# Create a scraper
scraper = cloudscraper.create_scraper()

# Fetch the page
response = scraper.get('https://tracker.gg/valorant/guides/clips')

# Save the HTML to a file
with open('output/tracker_page.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

print('Saved HTML to output/tracker_page.html')
