"""
Duffel API collection loop - mirrors the Ixigo scraper's structure
(same ROUTES, same DAY_WINDOWS, same CSV columns) so the two data
sources can be combined/compared later.

SECURITY: don't commit your real token to GitHub. For local testing
it's fine to hardcode it below, but before pushing this file to your
repo, switch to reading it from an environment variable instead:
    import os
    ACCESS_TOKEN = os.environ["DUFFEL_TOKEN"]
and set DUFFEL_TOKEN as a GitHub Actions "secret" (ask Claude to help
with this step when you get there).
"""

import requests
from datetime import datetime, timedelta
import csv
import os
import time

# --- Fill this in from your Duffel dashboard ---
ACCESS_TOKEN = "duffel_test_uorPPQK2EZbuLZvXGcyw1Vuw-IA_AAmHUTadK_KdAuF"

# ---- SETTINGS: same routes and windows as the Ixigo scraper ----
ROUTES = [
    ("DEL", "BOM"),
    ("DEL", "BLR"),
    ("BOM", "BLR"),
    ("DEL", "HYD"),
    ("BOM", "CCU"),
]

DAY_WINDOWS = [1, 7, 15, 30, 45]

MAX_OFFERS_PER_SEARCH = 20

OUTPUT_FILE = "fare_data_duffel.csv"

API_URL = "https://api.duffel.com/air/offer_requests?return_offers=true"

HEADERS = {
    "Accept-Encoding": "gzip",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Duffel-Version": "v2",
    "Authorization": f"Bearer {ACCESS_TOKEN}",
}


def fetch_offers(origin, destination, days_ahead):
    target_date = datetime.now() + timedelta(days=days_ahead)
    date_str = target_date.strftime("%Y-%m-%d")

    payload = {
        "data": {
            "slices": [
                {
                    "origin": origin,
                    "destination": destination,
                    "departure_date": date_str,
                }
            ],
            "passengers": [{"type": "adult"}],
            "cabin_class": "economy",
        }
    }

    print(f"Requesting: {origin}->{destination}, {date_str} (T+{days_ahead})")
    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)

    if response.status_code not in (200, 201):
        print(f"  -> API error {response.status_code}: {response.text[:200]}")
        return [{
            "collected_on": datetime.now().strftime("%Y-%m-%d"),
            "origin": origin,
            "destination": destination,
            "travel_date": target_date.strftime("%Y-%m-%d"),
            "days_ahead": days_ahead,
            "price_raw": "MISSING",
            "base_fare": "",
            "taxes": "",
            "currency": "",
        }]

    data = response.json()
    offers = data["data"]["offers"][:MAX_OFFERS_PER_SEARCH]

    if not offers:
        print(f"  -> NO OFFERS FOUND (marking as missing)")
        return [{
            "collected_on": datetime.now().strftime("%Y-%m-%d"),
            "origin": origin,
            "destination": destination,
            "travel_date": target_date.strftime("%Y-%m-%d"),
            "days_ahead": days_ahead,
            "price_raw": "MISSING",
            "base_fare": "",
            "taxes": "",
            "currency": "",
        }]

    results = []
    for offer in offers:
        results.append({
            "collected_on": datetime.now().strftime("%Y-%m-%d"),
            "origin": origin,
            "destination": destination,
            "travel_date": target_date.strftime("%Y-%m-%d"),
            "days_ahead": days_ahead,
            "price_raw": offer["total_amount"],
            "base_fare": offer["base_amount"],
            "taxes": offer["tax_amount"],
            "currency": offer["total_currency"],
        })
    return results


def main():
    all_results = []

    for origin, destination in ROUTES:
        for days_ahead in DAY_WINDOWS:
            try:
                rows = fetch_offers(origin, destination, days_ahead)
                all_results.extend(rows)
                print(f"  -> Got {len(rows)} offers")
            except Exception as e:
                print(f"  -> FAILED for {origin}-{destination}, T+{days_ahead}: {e}")

            time.sleep(1)  # polite pause between requests

    if all_results:
        file_exists = os.path.isfile(OUTPUT_FILE)
        with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
            if not file_exists:
                writer.writeheader()
            writer.writerows(all_results)
        print(f"\nAppended {len(all_results)} rows to {OUTPUT_FILE}")
    else:
        print("\nNo data collected.")


if __name__ == "__main__":
    main()