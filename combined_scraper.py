import os
import sys
import json
import time
import subprocess

def install_requirements():
    """Install required packages from requirements.txt"""
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def run_tracker_scraper(start_page=1, max_pages=None):
    """Run the tracker.gg scraper"""
    try:
        print("Running tracker.gg scraper...")
        from tracker_scraper import TrackerScraper
        scraper = TrackerScraper()
        scraper.scrape(start_page, max_pages)
        
        # Check if we have any results
        if not scraper.results:
            print("No results found using tracker.gg scraper")
            return None
        
        print(f"Found {len(scraper.results)} clips using tracker.gg scraper")
        if scraper.skipped_entries > 0:
            print(f"Skipped {scraper.skipped_entries} entries out of {scraper.total_entries} total entries due to missing video URLs")
        
        return scraper.results
    except Exception as e:
        print(f"Error running tracker.gg scraper: {e}")
        return None

def run_selenium_scraper(start_page=1, max_pages=None):
    """Run the Selenium scraper"""
    try:
        print("Running Selenium scraper...")
        from selenium_scraper import SeleniumScraper
        scraper = SeleniumScraper()
        scraper.scrape(start_page, max_pages)
        
        # Check if we have any results
        if not scraper.results:
            print("No results found using Selenium scraper")
            return None
        
        print(f"Found {len(scraper.results)} clips using Selenium scraper")
        if hasattr(scraper, 'skipped_entries') and scraper.skipped_entries > 0:
            print(f"Skipped {scraper.skipped_entries} entries out of {scraper.total_entries} total entries due to missing video URLs")
        
        return scraper.results
    except Exception as e:
        print(f"Error running Selenium scraper: {e}")
        return None

def run_api_scraper(start_page=1, max_pages=None):
    """Run the API scraper"""
    try:
        print("Running API scraper...")
        from api_scraper import ApiScraper
        scraper = ApiScraper()
        scraper.scrape(start_page, max_pages)
        
        # Check if we have any results
        if not scraper.results:
            print("No results found using API scraper")
            return None
        
        print(f"Found {len(scraper.results)} clips using API scraper")
        if hasattr(scraper, 'skipped_entries') and scraper.skipped_entries > 0:
            print(f"Skipped {scraper.skipped_entries} entries out of {scraper.total_entries} total entries due to missing video URLs")
        
        return scraper.results
    except Exception as e:
        print(f"Error running API scraper: {e}")
        return None

def run_combined_scraper(start_page=1, max_pages=None, output_file="valorant_clips.json"):
    """Run all scrapers and combine the results"""
    # Try API scraper first
    api_results = run_api_scraper(start_page, max_pages)
    
    # If API scraper failed, try tracker.gg scraper
    if not api_results:
        tracker_results = run_tracker_scraper(start_page, max_pages)
        
        # If tracker.gg scraper failed, try Selenium scraper
        if not tracker_results:
            selenium_results = run_selenium_scraper(start_page, max_pages)
            
            # If all scrapers failed, return None
            if not selenium_results:
                print("All scrapers failed")
                return None
            
            # Use Selenium results
            results = selenium_results
        else:
            # Use tracker.gg results
            results = tracker_results
    else:
        # Use API results
        results = api_results
    
    # Check if the file already exists and get the current version
    version = 1
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                if "version" in existing_data:
                    version = existing_data["version"] + 1
        except Exception as e:
            print(f"Error reading existing file: {e}")
    
    # Create the structured output with version and data
    output_data = {
        "version": version,
        "data": results
    }
    
    # Save the results to a JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)
    
    print(f"Saved {len(results)} clips to {output_file} (version {version})")
    
    return results

def run_full_scraper(method, start_page=1, max_pages=None):
    """Run the full scraper with the specified method"""
    print(f"\n=== Running full scraper using {method} method ===")
    
    if method == "api":
        results = run_api_scraper(start_page, max_pages)
    elif method == "tracker":
        results = run_tracker_scraper(start_page, max_pages)
    elif method == "selenium":
        results = run_selenium_scraper(start_page, max_pages)
    else:
        print(f"Unknown method: {method}")
        return
    
    # Save the results
    output_file = f"output/tracker_clips_{method}.json"
    
    # Check if the file already exists and get the current version
    version = 1
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                if "version" in existing_data:
                    version = existing_data["version"] + 1
        except Exception as e:
            print(f"Error reading existing file: {e}")
    
    # Create the structured output with version and data
    output_data = {
        "version": version,
        "data": results
    }
    
    # Save the results to a JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)
    
    # Copy to the main output file
    main_output_file = "output/tracker_clips.json"
    
    # Check if the main output file already exists and get the current version
    main_version = 1
    if os.path.exists(main_output_file):
        try:
            with open(main_output_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                if "version" in existing_data:
                    main_version = existing_data["version"] + 1
        except Exception as e:
            print(f"Error reading existing main output file: {e}")
    
    # Create the structured output with version and data
    main_output_data = {
        "version": main_version,
        "data": results
    }
    
    # Save the results to the main output file
    with open(main_output_file, "w", encoding="utf-8") as f:
        json.dump(main_output_data, f, indent=4, ensure_ascii=False)
    
    print(f"Saved {len(results)} clips to {main_output_file} (version {main_version})")

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    if not os.path.exists("output"):
        os.makedirs("output")
    
    # Install required packages
    install_requirements()
    
    # Run the combined scraper
    run_combined_scraper(start_page=1, max_pages=None, output_file="output/tracker_clips.json")
