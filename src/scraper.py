import requests
import time
import random
from ratelimit import limits, sleep_and_retry

CALLS = 3
PERIOD = 1

@sleep_and_retry
@limits(calls=CALLS, period=PERIOD)
def call_api(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response

def run_scraper():
    for i in range(50):
        try:
            response = call_api("https://dummy-api.cez.cz/data")
            print(f"Požadavek {i+1} OK")
            time.sleep(random.uniform(0.5, 1.0))

        except Exception as e:
            print(f"Chyba u požadavku {i+1}: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_scraper()