from playwright.sync_api import sync_playwright

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

    page.click('[data-testid="originId"]')
    page.wait_for_timeout(1000)

    page.keyboard.type("Delhi")
    page.wait_for_timeout(2000)

    # Click on "New Delhi, Delhi, India" specifically
    page.click('text=New Delhi, Delhi, India')
    page.wait_for_timeout(1500)

    page.screenshot(path="delhi_selected.png")
    browser.close()