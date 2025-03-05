# Tracker.gg Valorant Clips Scraper

This script scrapes Valorant guide clips from tracker.gg and saves them in a structured JSON format.

## Features

- Scrapes all pages of Valorant guide clips from tracker.gg
- Automatically converts map names to map IDs
- Automatically converts agent names to agent IDs
- Automatically converts team names to team IDs
- Removes map, team, and agent tags from the tags list
- Saves the data in a structured JSON format
- Multiple scraping methods to bypass anti-scraping measures

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Quick Start (Recommended)

Run the combined scraper which will automatically try different methods:

```bash
python combined_scraper.py
```

This script will:
1. Try the API-based method first (most reliable)
2. If that fails, try the CloudScraper method
3. If that fails, try the Selenium method
4. Use the successful method to scrape all pages
5. Save the results to `output/tracker_clips.json`

### Alternative Methods

If you want to use a specific scraping method:

#### API Method (Recommended)

```bash
python api_scraper.py
```

#### CloudScraper Method

```bash
python tracker_scraper.py
```

#### Selenium Method

```bash
python selenium_scraper.py
```

## Output Format

The script outputs a JSON file with the following structure:

```json
[
    {
        "title": "Clip Title",
        "description": "Clip Description",
        "tags": ["Tag1", "Tag2"],
        "mapID": "MapID",
        "teamID": "TeamID",
        "agentID": "AgentID",
        "videoURL": "VideoURL",
        "thumbnailURL": "ThumbnailURL",
        "author": "Author",
        "sourceURL": "SourceURL"
    },
    ...
]
```

Note: Fields that are not available or empty will not be included in the output.

## Scraping Methods

### API Scraper
- Directly accesses the tracker.gg API
- Most reliable method
- Fastest performance
- Least likely to be blocked

### CloudScraper
- Uses specialized library to bypass Cloudflare protection
- Parses HTML content
- Medium reliability

### Selenium
- Uses a real browser to render the page
- Most resource-intensive
- Handles JavaScript-rendered content
- Slowest but most thorough

## Troubleshooting

If you encounter issues with the scraper:

1. Check the HTML and JSON files saved in the `output` directory to see what the scraper is actually receiving
2. Try running the Selenium scraper with `headless=False` to see the browser in action
3. Adjust the delay between requests if you're getting rate limited
4. Make sure you have the latest Chrome browser installed for Selenium
5. If all methods fail, the website structure may have changed - check for updates to this scraper

## Customization

- To limit the number of pages to scrape, modify the `scrape()` function call in the script:

```python
scraper.scrape(max_pages=5)  # Limit to 5 pages
```

- To start scraping from a specific page, modify the `scrape()` function call:

```python
scraper.scrape(start_page=3)  # Start from page 3
