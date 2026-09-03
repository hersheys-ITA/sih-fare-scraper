from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.ixigo.com/")
    page.wait_for_timeout(3000)

    # Click the "From" box using its label
    page.get_by_label("From").click()
    page.wait_for_timeout(1000)

    # Type the city name
    page.get_by_label("From").fill("Delhi")
    page.wait_for_timeout(2000)  # wait for dropdown to appear

    page.screenshot(path="from_dropdown.png")
    browser.close()