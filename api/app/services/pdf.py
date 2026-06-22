"""HTML → PDF via Playwright (headless Chromium). Keeps ECharts SVG vector."""
from __future__ import annotations


def html_to_pdf(html: str) -> bytes:
    # Imported lazily so the API still boots if Playwright/Chromium isn't installed.
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        try:
            page = browser.new_page()
            page.set_content(html, wait_until="load")
            # Wait until our script signals the charts are rendered.
            page.wait_for_function("window.__READY__ === true", timeout=8000)
            page.wait_for_selector("svg", timeout=8000)
            page.wait_for_timeout(250)
            return page.pdf(
                format="A4",
                print_background=True,
                margin={"top": "14mm", "bottom": "14mm", "left": "12mm", "right": "12mm"},
            )
        finally:
            browser.close()
