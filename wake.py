"""Wake the AR3 Streamlit demo if it has gone to sleep.

Exits with an error (so GitHub emails you) only if the app is asleep and can't be woken.
"""
import re
import sys

from playwright.sync_api import sync_playwright

URL = "https://ar3-payments.streamlit.app"
ASLEEP = re.compile(r"gone to sleep|get this app back up|zzz", re.I)
WAKE_BUTTON = re.compile(r"back up|wake|get this app", re.I)


def page_text(page) -> str:
    try:
        return page.inner_text("body", timeout=10000)
    except Exception:
        return ""


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    for attempt in range(3):                      # retry slow loads
        try:
            page.goto(URL, timeout=90000, wait_until="domcontentloaded")
            break
        except Exception as err:
            print(f"Load attempt {attempt + 1} failed: {err}")
    else:
        sys.exit("Couldn't load the app at all.")

    page.wait_for_timeout(10000)
    if not ASLEEP.search(page_text(page)):
        print("App is awake.")
        sys.exit(0)

    buttons = page.get_by_role("button", name=WAKE_BUTTON)
    if not buttons.count():
        buttons = page.locator("button").filter(has_text=WAKE_BUTTON)
    if not buttons.count():
        sys.exit("App is asleep, but no wake button was found. The page wording may have changed.")

    buttons.first.click()
    print("Clicked the wake button; waiting for the app to start...")
    for _ in range(12):                            # up to 2 minutes
        page.wait_for_timeout(10000)
        if not ASLEEP.search(page_text(page)):
            print("App was asleep; woke it up.")
            sys.exit(0)
    sys.exit("Clicked wake, but the app still looks asleep after 2 minutes.")