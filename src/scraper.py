import requests

def run_scraper():
    for i in range(50):
        requests.get("https://dummy-api.cez.cz/data")