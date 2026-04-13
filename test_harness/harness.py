import time
import json
import sys
import os
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import scraper

def run_test():
    request_count = 0

    def fake_get(*args, **kwargs):
        nonlocal request_count
        request_count += 1
        return True
    
    start_time = time.time()

    with patch('scraper.requests.get', side_effect=fake_get):
        try:
            scraper.run_scraper()
        except Exception as e:
            print(f"Execution crashed: {e}")
            sys.exit(1)

    end_time = time.time()
    execution_time = end_time - start_time

    rps = request_count / execution_time if execution_time > 0 else request_count

    contract = {
        "execution_id": "job_001",
        "test_status": "FAIL_DETERMINISTIC" if rps > 5 else "PASS",
        "metrics": {
            "requests_per_second": round(rps,2),
            "max_allowed_rps": 5
        },
        "breached_rule_reference": "API_RATE_LIMIT" if rps > 5 else None
    }

    with open("metrics.json", "w") as f:
        json.dump(contract, f, indent=2)

    print(f"Harness finished. Executed {request_count} requests. Metrics saved.")

if __name__ == "__main__":
    run_test()
