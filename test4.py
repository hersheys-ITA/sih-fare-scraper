from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.ixigo.com/")
    page.wait_for_timeout(3000)

    # Click the "From" box using the data-testid we found earlier
    page.click('[data-testid="originId"]')
    page.wait_for_timeout(1500)

    page.screenshot(path="after_click.png")
    browser.close()