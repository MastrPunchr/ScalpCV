from playwright.sync_api import sync_playwright
import time
import pyautogui
from datetime import datetime

def take_fullscreen_screenshot(filepath):
    image = pyautogui.screenshot()
    image.save(filepath)
    print(f"🖼️ Fullscreen screenshot saved as {filepath}")

# common phrases to detect stock status
IN_STOCK_KEYWORDS = ['add to cart', 'buy now', 'in stock', 'order now', 'add', 'add now', 'add item']
OUT_OF_STOCK_KEYWORDS = ['out of stock', 'sold out', 'unavailable', 'not available', 'notify me']

# function to log the status to a file
def log_to_file(text):
    with open("availability_status.txt", "a", encoding="utf-8") as f:
        f.write(text + "\n")

# function to close any popups on the page
def close_popup(page):
    popup_closed = False
    # selectors to match various types of popups (buttons, links, etc.)
    selectors = [
        'button[aria-label*="close" i]',
        'button[title*="close" i]',
        'button:has-text("×")',
        'button:has-text("x")',
        'a[aria-label*="close" i]',
        'div[aria-label*="close" i]',
        'button:has-text("Close")',
        'button:has-text("No Thanks")',
        '.popup-close',
        '.close-button',
    ]
    # attempt to close the popup by looking for matching selectors
    for selector in selectors:
        try:
            close_btns = page.locator(selector)
            for i in range(close_btns.count()):
                btn = close_btns.nth(i)
                if btn.is_visible():
                    btn.click()
                    popup_closed = True
                    break
            if popup_closed:
                break
        except:
            continue
    return popup_closed

# function to check the availability of the product
def check_availability(url, log_callback=print):
    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

    try:
        with sync_playwright() as p:
            log("🌐 navigating to product page...")
            browser = p.chromium.launch(headless=False)  # open browser in non-headless mode
            page = browser.new_page()
            page.goto(url, timeout=60000)  # go to the product page with a 1-minute timeout
            time.sleep(5)  # wait for the page to load

            # take screenshot after page load
            take_fullscreen_screenshot("page_loaded.png")
            log("📸 screenshot taken after page load.")

            # close any popup if found
            if close_popup(page):
                log("🧼 popup closed.")
            else:
                log("ℹ️ no popup found.")

            # take screenshot after closing popup (if any)
            take_fullscreen_screenshot("popup_closed.png")
            log("📸 screenshot taken after popup closed (if applicable).")

            # save the page's HTML content for inspection later
            with open("page_dump.html", "w", encoding="utf-8") as f:
                f.write(page.content())

            in_stock = False

            # check all buttons for "add to cart" and related keywords
            buttons = page.locator("button")
            for i in range(buttons.count()):
                try:
                    btn = buttons.nth(i)
                    text = btn.text_content().strip().lower()  # get the button's text and normalize it
                    if any(keyword in text for keyword in IN_STOCK_KEYWORDS):  # check for any stock-related keyword
                        log("✅ product appears to be in stock (button).")
                        log_to_file("✅ product appears to be in stock.")


                        in_stock = True
                        break
                except:
                    continue

            # fallback: check span and a tags for the stock keywords
            if not in_stock:
                extra_tags = page.locator("span, a")
                for i in range(extra_tags.count()):
                    try:
                        el = extra_tags.nth(i)
                        text = el.text_content().strip().lower()
                        if any(keyword in text for keyword in IN_STOCK_KEYWORDS):
                            log("✅ product appears to be in stock (fallback span/a).")
                            log_to_file("✅ product appears to be in stock.")
                            in_stock = True
                            break
                    except:
                        continue

            # final fallback: check raw HTML content for out-of-stock keywords
            if not in_stock:
                full_text = page.content().lower()
                if any(keyword in full_text for keyword in OUT_OF_STOCK_KEYWORDS):
                    log("❌ product is out of stock.")
                    log_to_file("❌ product is out of stock.")
                else:
                    log("⚠️ couldn't determine stock status.")
                    log_to_file("⚠️ couldn't determine stock status.")

            time.sleep(3)  # wait for a while before closing the browser
            browser.close()  # close the browser
            return "✅ product is available!" if in_stock else "❌ product is out of stock.", in_stock

    except Exception as e:
        error = f"🚫 error: {e}"
        log(error)
        log_to_file(error)
        return error, False

# function to add product to cart (if available)
def add_to_cart(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        time.sleep(5)

        close_popup(page)  # attempt to close any popup that may appear

        buttons = page.locator("button")
        for i in range(buttons.count()):
            try:
                button = buttons.nth(i)
                text = button.text_content().strip().lower()
                # check if the button text matches "add to cart" or related keywords
                if any(keyword in text for keyword in IN_STOCK_KEYWORDS) and button.is_visible() and button.is_enabled():
                    print("🛒 'add to cart' clicked.")

                    import subprocess
                    subprocess.run(["python", "mouse_move.py"])  # 🧠 move + click via OCR after click

                    break

            except:
                continue

        time.sleep(5)
        browser.close()

# function to open the browser in view mode without headless operation
def open_browser_view(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # open browser in non-headless mode
        page = browser.new_page()
        page.goto(url)
        time.sleep(8)  # wait for a while to see the page
        browser.close()  # close the browser