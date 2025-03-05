import os
import subprocess
import sys

def install_requirements():
    """Install required packages from requirements.txt"""
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def run_scraper():
    """Run the tracker scraper"""
    print("Running tracker scraper...")
    subprocess.check_call([sys.executable, "tracker_scraper.py"])

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Install requirements
    install_requirements()
    
    # Run the scraper
    run_scraper()
    
    print("\nDone! Results saved to output/tracker_clips.json")
