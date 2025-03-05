import requests
import json
import time
import random
import os
import re
from urllib.parse import urljoin

class ApiScraper:
    def __init__(self):
        self.base_url = "https://api.tracker.gg/api/v2/valorant/guides/clips"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://tracker.gg/valorant/guides/clips",
            "Origin": "https://tracker.gg",
            "Connection": "keep-alive"
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
        """Remove map, team, and agent from tags"""
        if not tags:
            return []
            
        clean_tags = []
        for tag in tags:
            # Skip if tag is a map, team, or agent
            if tag in self.map_ids or tag in ["Attack", "Defense"] or tag in self.agent_ids:
                continue
            clean_tags.append(tag)
        return clean_tags
    
    def fetch_page(self, page_num):
        """Fetch a specific page of clips from the API"""
        url = f"{self.base_url}?page={page_num}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Save the raw API response for debugging
            with open(f"output/api_page_{page_num}.json", "w", encoding="utf-8") as f:
                f.write(response.text)
                
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page_num}: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response status code: {e.response.status_code}")
                print(f"Response headers: {e.response.headers}")
            return None
    
    def process_clip(self, clip_data):
        """Process a single clip from the API data"""
        try:
            # Extract basic data
            title = clip_data.get('title', '')
            description = clip_data.get('description', '')
            
            # Extract tags
            tags = clip_data.get('tags', [])
            tag_names = [tag.get('name', '') for tag in tags] if tags else []
            
            # Extract map ID from tags
            map_id = ""
            for tag in tag_names:
                if tag in self.map_ids:
                    map_id = self.get_map_id(tag)
                    break
            
            # Extract team ID from tags
            team_id = "Neutral"
            for tag in tag_names:
                if tag in self.team_ids:
                    team_id = self.get_team_id(tag)
                    break
            
            # Extract agent ID from tags
            agent_id = ""
            for tag in tag_names:
                if tag in self.agent_ids:
                    agent_id = self.get_agent_id(tag)
                    break
            
            # Clean tags (remove map, team, agent)
            clean_tags = self.clean_tags(tag_names)
            
            # Extract video URL
            video_url = clip_data.get('videoUrl', '')
            
            # Extract thumbnail URL
            thumbnail_url = clip_data.get('thumbnailUrl', '')
            
            # Extract author
            author = ""
            author_data = clip_data.get('author', {})
            if author_data:
                author = author_data.get('name', '')
            
            # Extract source URL
            source_url = f"https://tracker.gg/valorant/guides/clips/{clip_data.get('id', '')}" if clip_data.get('id') else ""
            
            # Create clip data dictionary
            processed_clip = {
                "title": title,
                "description": description,
                "tags": clean_tags
            }
            
            # Only add non-empty fields
            if map_id:
                processed_clip["mapID"] = map_id
            if team_id != "Neutral":
                processed_clip["teamID"] = team_id
            if agent_id:
                processed_clip["agentID"] = agent_id
            if video_url:
                processed_clip["videoURL"] = video_url
            if thumbnail_url:
                processed_clip["thumbnailURL"] = thumbnail_url
            if author:
                processed_clip["author"] = author
            if source_url:
                processed_clip["sourceURL"] = source_url
                
            return processed_clip
            
        except Exception as e:
            print(f"Error processing clip: {e}")
            return None
    
    def process_page(self, page_data):
        """Process the API response data for a page"""
        if not page_data or 'data' not in page_data:
            return []
        
        clips_data = page_data['data'].get('items', [])
        print(f"Found {len(clips_data)} clips in the API response")
        
        page_results = []
        for clip_data in clips_data:
            processed_clip = self.process_clip(clip_data)
            if processed_clip:
                page_results.append(processed_clip)
                
        return page_results
    
    def has_next_page(self, page_data):
        """Check if there's a next page based on the API response"""
        if not page_data or 'data' not in page_data:
            return False
        
        pagination = page_data['data'].get('pagination', {})
        current_page = pagination.get('currentPage', 0)
        total_pages = pagination.get('totalPages', 0)
        
        return current_page < total_pages
    
    def scrape(self, start_page=1, max_pages=None):
        """Scrape clips from tracker.gg API, starting from start_page"""
        current_page = start_page
        has_next_page = True
        
        while has_next_page:
            print(f"Scraping page {current_page}...")
            
            # Fetch the page data from the API
            page_data = self.fetch_page(current_page)
            
            # Process the page data
            page_results = self.process_page(page_data)
            self.results.extend(page_results)
            
            print(f"Processed {len(page_results)} clips from page {current_page}")
            
            # Check if there's a next page
            has_next_page = self.has_next_page(page_data)
            
            # Stop if we've reached the maximum number of pages
            if max_pages and current_page >= start_page + max_pages - 1:
                break
                
            # Move to the next page
            current_page += 1
            
            # Add a delay to avoid overloading the server
            time.sleep(random.uniform(1, 3))
        
        return self.results
    
    def save_to_json(self, filename="tracker_clips.json"):
        """Save the results to a JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=4, ensure_ascii=False)
        print(f"Saved {len(self.results)} clips to {filename}")


if __name__ == "__main__":
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Create the scraper
    scraper = ApiScraper()
    
    # Scrape the clips (optionally specify max_pages to limit the number of pages)
    # scraper.scrape(max_pages=5)  # Uncomment to limit to 5 pages
    scraper.scrape()
    
    # Save the results to a JSON file
    scraper.save_to_json("output/tracker_clips.json")
