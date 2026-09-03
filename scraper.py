from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import csv
import os

ROUTES = [
    ("DEL", "BOM"),
    ("DEL", "BLR"),
    ("BOM", "BLR"),
    ("DEL", "HYD"),
    ("BOM", "CCU"),
]

DAY_WINDOWS = [1, 7, 15, 30, 45]

MAX_PRICES_PER_SEARCH = 20

OUTPUT_FILE = "fare_data.csv"


def scrape_one_route(page, origin, destination, days_ahead):
    target_date = datetime.now() + timedelta(days=days_ahead)
    date_str = target_date.strftime("%d%m%Y")

    url = (
        f"https://www.ixigo.com/search/result/flight"
        f"?from={origin}&to={destination}&date={date_str}"
        f"&adults=1&children=0&infants=0&class=e"
    )

    print(f"Visiting: {url}")
    page.goto(url)
    page.wait_for_timeout(8000)

    for _ in range(4):
        page.mouse.wheel(0, 2000)
        page.wait_for_timeout(1500)

    prices = page.locator('[data-testid="pricing"]').all_text_contents()
    prices = prices[:MAX_PRICES_PER_SEARCH]

    if not prices:
        print(f"  -> NO FLIGHTS FOUND for {origin}-{destination} on {target_date.strftime('%Y-%m-%d')} (marking as missing)")
        return [{
            "collected_on": datetime.now().strftime("%Y-%m-%d"),
            "origin": origin,
            "destination": destination,
            "travel_date": target_date.strftime("%Y-%m-%d"),
            "days_ahead": days_ahead,
            "price_raw": "MISSING",
        }]

    results = []
    for price in prices:
        results.append({
            "collected_on": datetime.now().strftime("%Y-%m-%d"),
            "origin": origin,
            "destination": destination,
            "travel_date": target_date.strftime("%Y-%m-%d"),
            "days_ahead": days_ahead,
            "price_raw": price,
        })
    return results


def main():
    all_results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for origin, destination in ROUTES:
            for days_ahead in DAY_WINDOWS:
                try:
                    rows = scrape_one_route(page, origin, destination, days_ahead)
                    all_results.extend(rows)
                    print(f"  -> Got {len(rows)} prices for {origin}-{destination}, T+{days_ahead}")
                except Exception as e:
                    print(f"  -> FAILED for {origin}-{destination}, T+{days_ahead}: {e}")

                page.wait_for_timeout(3000)

        browser.close()

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