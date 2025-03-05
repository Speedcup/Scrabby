import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re
import os
from urllib.parse import urljoin
import cloudscraper  # Added for bypassing Cloudflare protection

class TrackerScraper:
    def __init__(self):
        self.base_url = "https://tracker.gg/valorant/guides/clips"
        # Use cloudscraper to bypass Cloudflare protection
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            },
            delay=10
        )
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Referer": "https://tracker.gg/",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }
        
        # Agent ID mapping
        self.agent_ids = {
            "Astra": "41fb69c1-4189-7b37-f117-bcaf1e96f1bf",
            "Breach": "5f8d3a7f-467b-97f3-062c-13acf203c006",
            "Brimstone": "9f0d8ba9-4140-b941-57d3-a7ad57c6b417",
            "Chamber": "22697a3d-45bf-8dd7-4fec-84a9e28c69d7",
            "Clove": "1dbf2edd-4729-0984-3115-daa5eed44993",
            "Cypher": "117ed9e3-49f3-6512-3ccf-0cada7e3823b",
            "Deadlock": "cc8b64c8-4b25-4ff9-6e7f-37b4da43d235",
            "Fade": "dade69b4-4f5a-8528-247b-219e5a1facd6",
            "Gekko": "e370fa57-4757-3604-3648-499e1f642d3f",
            "Harbor": "95b78ed7-4637-86d9-7e41-71ba8c293152",
            "Iso": "0e38b510-41a8-5780-5e8f-568b2a4f2d6c",
            "Jett": "add6443a-41bd-e414-f6ad-e58d267f4e95",
            "KAY/O": "601dbbe7-43ce-be57-2a40-4abd24953621",
            "Killjoy": "1e58de9c-4950-5125-93e9-a0aee9f98746",
            "Neon": "bb2a4828-46eb-8cd1-e765-15848195d751",
            "Omen": "8e253930-4c05-31dd-1b6c-968525494517",
            "Phoenix": "eb93336a-449b-9c1b-0a54-a891f7921d69",
            "Raze": "f94c3b30-42be-e959-889c-5aa313dba261",
            "Reyna": "a3bfb853-43b2-7238-a4f1-ad90e9e46bcc",
            "Sage": "569fdd95-4d10-43ab-ca70-79becc718b46",
            "Skye": "6f2a04ca-43e0-be17-7f36-b3908627744d",
            "Sova": "320b2a48-4d9b-a075-30f1-1f93a9b638fa",
            "Tejo": "b444168c-4e35-8076-db47-ef9bf368f384",
            "Viper": "707eab51-4836-f488-046a-cda6bf494859",
            "Vyse": "efba5359-4016-a1e5-7626-b1ae76895940",
            "Yoru": "7f94d92c-4234-0a36-9646-3a87eb8b5c89"
        }
        
        # Map ID mapping
        self.map_ids = {
            "Abyss": "Infinity",
            "Ascent": "Ascent",
            "Bind": "Duality",
            "Breeze": "Foxtrot",
            "Fracture": "Canyon",
            "Haven": "Triad",
            "Icebox": "Port",
            "Lotus": "Jam",
            "Sunset": "Juliett",
            "Split": "Bonsai",
            "Pearl": "Pitt"
        }
        
        # Team ID mapping
        self.team_ids = {
            "Attack": "Red",
            "Defense": "Blue"
        }
        
        self.results = []
        self.skipped_entries = 0
        self.total_entries = 0
        
    def get_agent_id(self, agent_name):
        """Convert agent name to agent ID"""
        return self.agent_ids.get(agent_name, "")
    
    def get_map_id(self, map_name):
        """Convert map name to map ID"""
        return self.map_ids.get(map_name, "")
    
    def get_team_id(self, team_name):
        """Convert team name to team ID"""
        return self.team_ids.get(team_name, "Neutral")
    
    def clean_tags(self, tags):
        """Remove map, team, and agent tags"""
        clean_tags = []
        
        for tag in tags:
            # Skip map tags
            if tag in self.map_ids:
                continue
            
            # Skip team tags (attack, defense)
            if tag.lower() in ["attack", "defense"]:
                continue
            
            # Skip agent tags
            if tag in self.agent_ids:
                continue
            
            # Add the tag to the clean tags list
            clean_tags.append(tag)
        
        return clean_tags
    
    def fetch_page(self, page_num):
        """Fetch a specific page of clips"""
        url = f"{self.base_url}?page={page_num}"
        try:
            # Use cloudscraper instead of requests
            response = self.scraper.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page_num}: {e}")
            # Add more detailed error information
            if hasattr(e, 'response') and e.response:
                print(f"Response status code: {e.response.status_code}")
                print(f"Response headers: {e.response.headers}")
            return None
    
    def parse_clip(self, clip_element):
        """Parse a single clip element"""
        try:
            self.total_entries += 1
            
            # Extract title - updated selector
            title_element = clip_element.find("p", class_="guide-tile__title")
            if title_element and title_element.find("a"):
                title = title_element.find("a").text.strip()
            else:
                title = ""
            
            # Extract description - leave empty if not found
            description = ""
            
            # Extract tags from badges
            badges_element = clip_element.find("div", class_="guide-tile__badges")
            tags = []
            if badges_element:
                badge_elements = badges_element.find_all("span", class_="badge")
                tags = [tag.text.strip() for tag in badge_elements]
            
            # Extract map ID from tags
            map_id = ""
            for tag in tags:
                if tag in self.map_ids:
                    map_id = self.get_map_id(tag)
                    break
            
            # Extract team ID from tags (convert "attack" or "defense" to proper case)
            team_id = "Neutral"
            for tag in tags:
                tag_lower = tag.lower()
                if tag_lower == "attack":
                    team_id = self.get_team_id("Attack")
                    break
                elif tag_lower == "defense":
                    team_id = self.get_team_id("Defense")
                    break
            
            # Extract agent ID from tags
            agent_id = ""
            for tag in tags:
                if tag in self.agent_ids:
                    agent_id = self.get_agent_id(tag)
                    break
            
            # Clean tags (remove map, team, agent)
            clean_tags = self.clean_tags(tags)
            
            # Extract source URL from the title link (needed for fetching the video URL)
            source_url = ""
            if title_element and title_element.find("a") and title_element.find("a").get("href"):
                source_url = "https://tracker.gg" + title_element.find("a")["href"]
            
            # Extract thumbnail URL from the img element in guide-tile__video
            thumbnail_url = ""
            video_div = clip_element.find("div", class_="guide-tile__video")
            if video_div:
                img_element = video_div.find("img")
                if img_element and img_element.get("src"):
                    thumbnail_url = img_element["src"]
            
            # Extract video URL - try to get the iframe URL if possible
            video_url = ""
            if source_url:
                try:
                    # Fetch the clip detail page to get the iframe
                    detail_response = self.scraper.get(source_url, headers=self.headers)
                    if detail_response.status_code == 200:
                        detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                        
                        # Look for iframe with videodelivery.net URL
                        iframe = detail_soup.find("iframe", src=lambda s: s and "videodelivery.net" in s)
                        if iframe and iframe.get("src"):
                            video_url = iframe["src"]
                        
                        # If iframe not found, look for a video element
                        if not video_url:
                            video_element = detail_soup.find("video", src=lambda s: s and "cloudflarestream" in s)
                            if video_element and video_element.get("src"):
                                video_url = video_element["src"]
                    
                    # If we still don't have a video URL, try to extract it from the thumbnail
                    if not video_url and thumbnail_url:
                        import re
                        video_id_match = re.search(r'cloudflarestream\.com/([^/]+)/', thumbnail_url)
                        if video_id_match:
                            video_id = video_id_match.group(1)
                            # Try the iframe format
                            video_url = f"https://iframe.videodelivery.net/{video_id}"
                
                except Exception as e:
                    print(f"Error fetching detail page: {e}")
            
            # If we still don't have a video URL, skip this entry
            if not video_url:
                self.skipped_entries += 1
                return None
            
            # Extract author from guide-tile__author
            author_element = clip_element.find("span", class_="guide-tile__author")
            author = ""
            if author_element:
                author_text = author_element.text.strip()
                if "By" in author_text:
                    author = author_text.replace("By", "").strip()
                    # If there's an anchor tag, use that text instead
                    author_link = author_element.find("a")
                    if author_link:
                        author = author_link.text.strip()
            
            # Create clip data dictionary
            clip_data = {
                "title": title,
                "tags": clean_tags
            }
            
            # Only add description if it's not empty
            if description:
                clip_data["description"] = description
            
            # Only add non-empty fields
            if map_id:
                clip_data["mapID"] = map_id
            if team_id != "Neutral":
                clip_data["teamID"] = team_id
            if agent_id:
                clip_data["agentID"] = agent_id
            if video_url:
                clip_data["videoURL"] = video_url
            if thumbnail_url:
                clip_data["thumbnailURL"] = thumbnail_url
            if author:
                clip_data["author"] = author
            if source_url:
                clip_data["sourceURL"] = source_url
                
            return clip_data
            
        except Exception as e:
            print(f"Error parsing clip: {e}")
            self.skipped_entries += 1
            return None
    
    def parse_page(self, html_content):
        """Parse the HTML content of a page and extract clip data"""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        # Updated class name from guide-card to guide-tile
        clip_elements = soup.find_all("div", class_="guide-tile")
        
        # Debug information
        print(f"Found {len(clip_elements)} clip elements on the page")
        
        page_results = []
        for clip_element in clip_elements:
            clip_data = self.parse_clip(clip_element)
            if clip_data:
                page_results.append(clip_data)
                
        return page_results
    
    def check_next_page_exists(self, html_content):
        """Check if there's a next page"""
        if not html_content:
            return False
        
        soup = BeautifulSoup(html_content, 'html.parser')
        next_button = soup.find("button", string=re.compile("Next"))
        
        # Check if the next button exists and is not disabled
        if next_button and not next_button.get("disabled"):
            return True
        return False
    
    def scrape(self, start_page=1, max_pages=None):
        """Scrape clips from tracker.gg"""
        page_num = start_page
        
        while True:
            print(f"Scraping page {page_num}...")
            
            # Fetch the page
            html_content = self.fetch_page(page_num)
            
            # Parse the page
            page_results = self.parse_page(html_content)
            
            # Add the results to the list
            self.results.extend(page_results)
            
            # Print the number of clips found on this page
            print(f"Found {len(page_results)} clips on page {page_num}")
            
            # If no results were found on this page, we've reached the end
            if len(page_results) == 0:
                print("No more clips found, stopping.")
                break
            
            # Check if we should stop based on max_pages
            if max_pages and page_num >= start_page + max_pages - 1:
                break
            
            # Go to the next page
            page_num += 1
            
            # Add a delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))
        
        # Print statistics
        if self.skipped_entries > 0:
            print(f"Skipped {self.skipped_entries} entries out of {self.total_entries} total entries due to missing video URLs")
        
        return self.results
    
    def save_to_json(self, filename="tracker_clips.json"):
        """Save the results to a JSON file"""
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Check if the file already exists and get the current version
        version = 1
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    if "version" in existing_data:
                        version = existing_data["version"] + 1
            except Exception as e:
                print(f"Error reading existing file: {e}")
        
        # Create the structured output with version and data
        output_data = {
            "version": version,
            "data": self.results
        }
        
        # Save the results to a JSON file
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
        
        print(f"Saved {len(self.results)} clips to {filename}")


if __name__ == "__main__":
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Create the scraper
    scraper = TrackerScraper()
    
    # Scrape the clips (optionally specify max_pages to limit the number of pages)
    # scraper.scrape(max_pages=5)  # Uncomment to limit to 5 pages
    scraper.scrape()
    
    # Save the results to a JSON file
    scraper.save_to_json("output/tracker_clips.json")
