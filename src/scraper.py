import requests
import time
import random

def run_scraper():
    # Target: 5 RPS = 0.2s per request. 
    # We set a safety margin (e.g., 0.25s) to account for execution time.
    MIN_DELAY = 0.25 
    
    for i in range(50):
        start_time = time.time()
        try:
            response = requests.get("https://dummy-api.cez.cz/data")
            
            # Handle explicit rate limiting from server
            if response.status_code == 429:
                time.sleep(1) # Backoff
                continue
                
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        
        # Calculate elapsed time and sleep for the remainder of the interval
        elapsed = time.time() - start_time
        sleep_time = max(0, MIN_DELAY - elapsed)
        
        # Add small jitter to prevent synchronized request patterns
        time.sleep(sleep_time + random.uniform(0, 0.05))