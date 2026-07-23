import os
import sys
from playwright.sync_api import sync_playwright

def run_verification(page, target_url):
    print(f"Opening {target_url}")

    # Listen for failed requests
    failed_requests = []
    page.on("requestfailed", lambda request: failed_requests.append(request.url))

    # Also listen for non-200 responses
    page.on("response", lambda response:
            failed_requests.append(response.url) if response.status >= 400 else None)

    page.goto(target_url)
    page.wait_for_timeout(1000)

    # Scroll to the bottom to trigger lazy loading
    # We'll do it in increments
    scroll_height = page.evaluate("document.body.scrollHeight")
    viewport_height = page.viewport_size["height"]

    current_scroll = 0
    while current_scroll < scroll_height:
        current_scroll += viewport_height // 2
        page.evaluate(f"window.scrollTo(0, {current_scroll})")
        page.wait_for_timeout(300)
        # Update scroll_height in case it changed
        scroll_height = page.evaluate("document.body.scrollHeight")

    # Wait a bit for final images to load
    page.wait_for_timeout(2000)

    # Check for any image tags that didn't load (onerror might have triggered)
    # The index.html has an onerror handler that hides the link and shows a placeholder.
    # We can check for visible placeholders 'ph'.
    missing_images = page.evaluate("""() => {
        const phs = Array.from(document.querySelectorAll('.ph'));
        return phs.filter(ph => !ph.hidden).map(ph => {
            const card = ph.closest('.card');
            return card ? card.querySelector('.common').innerText : 'Unknown plant';
        });
    }""")

    success = True

    if missing_images:
        print("Missing/Failed images for plants:")
        for plant in missing_images:
            print(f"  - {plant}")
        success = False
    else:
        print("All plant images loaded successfully (no placeholders visible).")

    if failed_requests:
        print("Failed requests:")
        for url in failed_requests:
            print(f"  - {url}")
        success = False
    else:
        print("No failed network requests.")

    # Take screenshot
    os.makedirs("verification/screenshots", exist_ok=True)
    screenshot_path = "verification/screenshots/verification.png"
    page.screenshot(path=screenshot_path, full_page=True)
    print(f"Screenshot saved to {screenshot_path}")

    return success

if __name__ == "__main__":
    # Default to local index.html if no URL provided
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = f"file://{os.path.abspath('index.html')}"

    os.makedirs("verification/videos", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir="verification/videos",
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()
        try:
            is_successful = run_verification(page, target)
            if not is_successful:
                sys.exit(1)
        finally:
            context.close()
            browser.close()
