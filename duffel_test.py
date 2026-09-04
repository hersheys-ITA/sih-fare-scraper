"""
Step 1 of the Duffel integration: get ONE flight price working.
Fill in your ACCESS_TOKEN from duffel.com dashboard, then run:
    python duffel_test.py

Uses plain `requests` calls (Duffel's official Python library was
discontinued in 2023, so we talk to their REST API directly - this
matches their current official docs exactly).
"""

import requests
import json

# --- Fill this in from your Duffel dashboard (starts with "duffel_test_") ---
ACCESS_TOKEN = "duffel_test_uorPPQK2EZbuLZvXGcyw1Vuw-IA_AAmHUTadK_KdAuF"

url = "https://api.duffel.com/air/offer_requests?return_offers=true"

headers = {
    "Accept-Encoding": "gzip",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Duffel-Version": "v2",
    "Authorization": f"Bearer {ACCESS_TOKEN}",
}

payload = {
    "data": {
        "slices": [
            {
                "origin": "DEL",
                "destination": "BOM",
                "departure_date": "2026-09-07",
            }
        ],
        "passengers": [{"type": "adult"}],
        "cabin_class": "economy",
    }
}

response = requests.post(url, headers=headers, json=payload)

if response.status_code not in (200, 201):
    print("Error from Duffel API:", response.status_code)
    print(response.text)
else:
    data = response.json()
    offers = data["data"]["offers"]
    print(f"Got {len(offers)} offers\n")

    # Print the raw first offer so we can inspect the structure
    print(json.dumps(offers[0], indent=2)[:2000])  # trimmed for readability

    # --- Once you've looked at the structure, pull out the key fields ---
    first_offer = offers[0]

    total_amount = first_offer["total_amount"]
    total_currency = first_offer["total_currency"]
    base_amount = first_offer["base_amount"]
    tax_amount = first_offer["tax_amount"]
    airline = first_offer["owner"]["name"]

    print("\n--- Parsed summary ---")
    print(f"Airline:     {airline}")
    print(f"Currency:    {total_currency}")
    print(f"Base fare:   {base_amount}")
    print(f"Taxes:       {tax_amount}")
    print(f"Total:       {total_amount}")