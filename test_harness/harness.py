import time
import json
import os
import sys
from unittest.mock import patch, MagicMock

# Oprava cesty
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import scraper

def run_test():
    request_count = 0
    mock_res = MagicMock()
    mock_res.status_code = 200
    mock_res.raise_for_status = lambda: None

    def fake_get(*args, **kwargs):
        nonlocal request_count
        request_count += 1
        return mock_res

    start_time = time.time()

    with patch('scraper.requests.get', side_effect=fake_get):
        try:
            scraper.run_scraper()
        except Exception as e:
            print(f"Crashed: {e}")

    end_time = time.time()
    duration = end_time - start_time
    rps = request_count / duration if duration > 0 else 0

    metrics = {
        "execution_id": "local_test",
        "test_status": "SUCCESS" if rps <= 5 else "FAIL",
        "metrics": {
            "requests_per_second": round(rps, 2),
            "max_allowed_rps": 5
        }
    }

    with open("metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    
    print(f"Harness done. RPS: {round(rps, 2)}. Duration: {round(duration, 2)}s")

if __name__ == "__main__":
    run_test()