from typing import Dict, Any
from playwright.sync_api import sync_playwright


def browser_goto(args: Dict[str, Any]) -> bool:
    url = args.get("url")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        browser.close()
    return True


def browser_fill(args: Dict[str, Any]) -> bool:
    url = args.get("url")
    selector = args.get("selector")
    text = args.get("text", "")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        page.fill(selector, text)
        browser.close()
    return True
