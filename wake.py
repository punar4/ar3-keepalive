from playwright.sync_api import sync_playwright

URL = "https://ar3-payments.streamlit.app"

with sync_playwright() as p:
    page = p.chromium.launch().new_page()
    page.goto(URL, timeout=60000)
    page.wait_for_timeout(8000)
    button = page.get_by_role("button", name="Yes, get this app back up")
    if button.count():
        button.first.click()
        page.wait_for_timeout(30000)
        print("App was asleep; woke it up.")
    else:
        print("App is awake.")