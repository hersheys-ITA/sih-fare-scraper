from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.ixigo.com/")
    page.wait_for_timeout(3000)

    try:
        page.click('button:has-text("×")', timeout=3000)
    except:
        print("No popup found, continuing...")
    page.wait_for_timeout(1000)

    # FROM
    page.click('[data-testid="originId"]')
    page.wait_for_timeout(1000)
    page.keyboard.type("Delhi")
    page.wait_for_timeout(2000)
    page.click('text=New Delhi, Delhi, India')
    page.wait_for_timeout(1500)

    # TO
    page.keyboard.type("Mumbai")
    page.wait_for_timeout(2000)
    page.click('text=Mumbai, Maharashtra, India')
    page.wait_for_timeout(1500)

    # DATE - let's do T+7 (7 days from today) as a test
    target_date = datetime.now() + timedelta(days=7)
    target_label = target_date.strftime("%B %#d, %Y")  # e.g. "September 7, 2026"
    print("Looking for date:", target_label)

    # Click the Departure box to open calendar
    page.click('text=Departure')
    page.wait_for_timeout(1500)

    # Click next month (>) up to 2 times if the date isn't visible yet
    for _ in range(2):
        try:
            page.click(f'[aria-label="{target_label}"]', timeout=2000)
            print("Date found and clicked!")
            break
        except:
            print("Not visible, clicking next month...")
            page.click('.react-calendar__navigation__next-button')
            page.wait_for_timeout(1000)

    page.wait_for_timeout(1500)
    page.screenshot(path="date_selected.png")
    browser.close()