from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    url = "https://www.jstor.org/stable/2480681?seq=1"

    page.goto(url)
    print(page.title())
    browser.close()