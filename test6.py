from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.ixigo.com/")
    page.wait_for_timeout(3000)

    # Try to close any popup, if one appears
    try:
        page.click('button:has-text("×")', timeout=3000)
    except:
        print("No popup found, continuing...")

    page.wait_for_timeout(1000)

    # Click the "From" box
    page.click('[data-testid="originId"]')
    page.wait_for_timeout(1000)

    # Type "Delhi"
    page.keyboard.type("Delhi")
    page.wait_for_timeout(2000)

    page.screenshot(path="delhi_typed2.png")
    browser.close()