from playwright.sync_api import sync_playwright
from time import sleep

with sync_playwright() as playwright:
    browser=playwright.chromium.launch(headless=False,slow_mo=200)
    page=browser.new_page()
    page.goto('https://google.com')
    page.get_by_role('combobox').fill('Kochi')
    # locater=page.locator('xpath=//ul[@role="listbox"]//li')
    locater=page.get_by_role('listbox').get_by_role('option')
    print(locater.count())