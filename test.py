from playwright.sync_api import sync_playwright
from time import sleep

VM_IP = "192.168.1.5"  # VM IP address from your screenshot
REMOTE_PORT = 9222     # Port used for remote debugging

with sync_playwright() as p:
    # Connect to the browser running in the VM
    browser = p.chromium.connect_over_cdp("http://192.168.1.5:9222")
    page = browser.new_page()
    page.goto("https://google.com")
    sleep(2)
    browser.close()
