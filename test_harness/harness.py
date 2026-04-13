import time
import json
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import scraper

def run_test():
    request_count = 0

    # Vytvoříme falešnou odpověď (Mock object)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = lambda: None  # Simulujeme, že se nic nepokazilo

    def fake_get(*args, **kwargs):
        nonlocal request_count
        request_count += 1
        return mock_response # Vracíme objekt, ne jen True
    
    start_time = time.time()

    # Patchujeme jak klasický requests.get, tak i Session.get
    with patch('scraper.requests.get', side_effect=fake_get), \
         patch('scraper.requests.Session.get', side_effect=fake_get):
        try:
            scraper.run_scraper()
        except Exception as e:
            # Pokud scraper spadne, vypíšeme to, ale vytvoříme metrics.json,
            # aby Agent mohl analyzovat PROČ to spadlo.
            print(f"Scraper execution crashed: {e}", file=sys.stderr)

    end_time = time.time()
    execution_time = end_time - start_time
    rps = request_count / execution_time if execution_time > 0 else request_count

    contract = {
        "execution_id": "job_001",
        "test_status": "FAIL_DETERMINISTIC" if rps > 5 else "PASS",
        "metrics": {
            "requests_per_second": round(rps, 2),
            "max_allowed_rps": 5
        },
        "breached_rule_reference": "API_RATE_LIMIT" if rps > 5 else None
    }

    with open("metrics.json", "w") as f:
        json.dump(contract, f, indent=2)

    print(f"Harness finished. Executed {request_count} requests. RPS: {round(rps,2)}")

if __name__ == "__main__":
    run_test()