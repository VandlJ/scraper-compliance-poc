import requests
import time
from ratelimit import limits, sleep_and_retry

# Define constants based on api_terms.pdf
CALLS = 5
PERIOD = 1  # seconds

@sleep_and_retry
@limits(calls=CALLS, period=PERIOD)
def call_api(url):
    # Mandatory delay per internal_policy.pdf
    time.sleep(0.2) 
    response = requests.get(url)
    response.raise_for_status()
    return response

def run_scraper():
    # The loop now respects the rate limit and the mandatory sleep policy
    for i in range(50):
        try:
            response = call_api("https://dummy-api.cez.cz/data")
            print(f"Request {i} successful")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            # Backoff strategy to prevent further violations
            time.sleep(1)