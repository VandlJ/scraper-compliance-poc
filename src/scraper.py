import requests
import time

def run_scraper():
    # Rate limit: 5 requests per second = 0.2 seconds per request
    delay = 0.21 
    
    for i in range(50):
        try:
            response = requests.get("https://dummy-api.cez.cz/data")
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        
        # Mandatory delay to comply with internal_policy.pdf
        time.sleep(delay)