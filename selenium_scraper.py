import time
import json
import random
import os
import re
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

class SeleniumTrackerScraper:
    def __init__(self, headless=True):
        self.base_url = "https://tracker.gg/valorant/guides/clips"
        
        # Setup Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Initialize the Chrome driver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # Set user agent
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
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
        clean_tags = []
        for tag in tags:
            # Skip if tag is a map, team, or agent
            if tag in self.map_ids or tag in ["Attack", "Defense"] or tag in self.agent_ids:
                continue
            clean_tags.append(tag)
        return clean_tags
    
    def navigate_to_page(self, page_num):
        """Navigate to a specific page of clips"""
        url = f"{self.base_url}?page={page_num}"
        try:
            self.driver.get(url)
            # Wait for the page to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.guide-tile"))
            )
            return True
        except TimeoutException:
            print(f"Timeout waiting for page {page_num} to load")
            return False
        except Exception as e:
            print(f"Error navigating to page {page_num}: {e}")
            return False
    
    def parse_clip(self, clip_element):
        """Parse a single clip element using Selenium"""
        try:
            # Extract title
            try:
                title_element = clip_element.find_element(By.CSS_SELECTOR, "h3.guide-tile__title")
                title = title_element.text.strip()
            except NoSuchElementException:
                title = ""
            
            # Extract description
            try:
                desc_element = clip_element.find_element(By.CSS_SELECTOR, "div.guide-tile__description")
                description = desc_element.text.strip()
            except NoSuchElementException:
                description = ""
            
            # Extract tags
            tags = []
            try:
                tags_element = clip_element.find_element(By.CSS_SELECTOR, "div.guide-tile__tags")
                tag_elements = tags_element.find_elements(By.CSS_SELECTOR, "div.guide-tile__tag")
                tags = [tag.text.strip() for tag in tag_elements]
            except NoSuchElementException:
                pass
            
            # Extract map ID from tags
            map_id = ""
            for tag in tags:
                if tag in self.map_ids:
                    map_id = self.get_map_id(tag)
                    break
            
            # Extract team ID from tags
            team_id = "Neutral"
            for tag in tags:
                if tag in self.team_ids:
                    team_id = self.get_team_id(tag)
                    break
            
            # Extract agent ID from tags
            agent_id = ""
            for tag in tags:
                if tag in self.agent_ids:
                    agent_id = self.get_agent_id(tag)
                    break
            
            # Clean tags (remove map, team, agent)
            clean_tags = self.clean_tags(tags)
            
            # Extract video URL
            video_url = ""
            try:
                video_element = clip_element.find_element(By.CSS_SELECTOR, "iframe, video")
                video_url = video_element.get_attribute("src") or video_element.get_attribute("data-src") or ""
            except NoSuchElementException:
                pass
            
            # Extract thumbnail URL
            thumbnail_url = ""
            try:
                thumbnail_element = clip_element.find_element(By.CSS_SELECTOR, "img")
                thumbnail_url = thumbnail_element.get_attribute("src") or thumbnail_element.get_attribute("data-src") or ""
            except NoSuchElementException:
                pass
            
            # Extract author
            author = ""
            try:
                author_element = clip_element.find_element(By.CSS_SELECTOR, "div.guide-tile__author")
                author = author_element.text.strip()
            except NoSuchElementException:
                pass
            
            # Extract source URL
            source_url = ""
            try:
                link_element = clip_element.find_element(By.CSS_SELECTOR, "a.guide-tile__link")
                href = link_element.get_attribute("href")
                if href:
                    source_url = href
            except NoSuchElementException:
                pass
            
            # Create clip data dictionary
            clip_data = {
                "title": title,
                "description": description,
                "tags": clean_tags
            }
            
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
            return None
    
    def parse_page(self):
        """Parse the current page and extract clip data"""
        try:
            # Wait for the clips to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.guide-tile"))
            )
            
            # Find all clip elements
            clip_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.guide-tile")
            print(f"Found {len(clip_elements)} clip elements on the page")
            
            page_results = []
            for clip_element in clip_elements:
                clip_data = self.parse_clip(clip_element)
                if clip_data:
                    page_results.append(clip_data)
                    
            return page_results
        
        except Exception as e:
            print(f"Error parsing page: {e}")
            return []
    
    def check_next_page_exists(self):
        """Check if there's a next page"""
        try:
            next_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Next')]")
            for button in next_buttons:
                if not button.get_attribute("disabled"):
                    return True
            return False
        except Exception as e:
            print(f"Error checking for next page: {e}")
            return False
    
    def scrape(self, start_page=1, max_pages=None):
        """Scrape clips from tracker.gg, starting from start_page"""
        try:
            current_page = start_page
            has_next_page = True
            
            while has_next_page:
                print(f"Scraping page {current_page}...")
                
                # Navigate to the page
                if not self.navigate_to_page(current_page):
                    print(f"Failed to navigate to page {current_page}, stopping")
                    break
                
                # Save the page source for debugging
                with open(f"output/page_{current_page}_selenium.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                
                # Parse the page and extract clip data
                page_results = self.parse_page()
                self.results.extend(page_results)
                
                print(f"Found {len(page_results)} clips on page {current_page}")
                
                # Check if there's a next page
                has_next_page = self.check_next_page_exists()
                
                # Stop if we've reached the maximum number of pages
                if max_pages and current_page >= start_page + max_pages - 1:
                    break
                    
                # Move to the next page
                current_page += 1
                
                # Add a delay to avoid overloading the server
                time.sleep(random.uniform(2, 5))
            
            return self.results
        
        finally:
            # Always close the driver when done
            self.driver.quit()
    
    def save_to_json(self, filename="tracker_clips_selenium.json"):
        """Save the results to a JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=4, ensure_ascii=False)
        print(f"Saved {len(self.results)} clips to {filename}")


if __name__ == "__main__":
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Create the scraper (set headless=False to see the browser in action)
    scraper = SeleniumTrackerScraper(headless=True)
    
    # Scrape the clips (optionally specify max_pages to limit the number of pages)
    # scraper.scrape(max_pages=5)  # Uncomment to limit to 5 pages
    scraper.scrape()
    
    # Save the results to a JSON file
    scraper.save_to_json("output/tracker_clips_selenium.json")
