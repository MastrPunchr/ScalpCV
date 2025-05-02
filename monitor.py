from playwright.sync_api import sync_playwright
import time

# Common phrases to detect stock status
IN_STOCK_KEYWORDS = ['add to cart', 'buy now', 'in stock', 'order now', 'add', 'add now', 'add item']
OUT_OF_STOCK_KEYWORDS = ['out of stock', 'sold out', 'unavailable', 'not available', 'notify me']

def log_to_file(text):
    with open("availability_status.txt", "a", encoding="utf-8") as f:
        f.write(text + "\n")

def close_popup(page):
    popup_closed = False
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

def check_availability(url, log_callback=print):
    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

    try:
        with sync_playwright() as p:
            log("🌐 Navigating to product page...")
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            time.sleep(5)

            # Take screenshot after page load
            page.screenshot(path="page_loaded.png")
            log("📸 Screenshot taken after page load.")

            if close_popup(page):
                log("🧼 Popup closed.")
            else:
                log("ℹ️ No popup found.")

            # Take screenshot after closing popup (if any)
            page.screenshot(path="popup_closed.png")
            log("📸 Screenshot taken after popup closed (if applicable).")

            # Save HTML for inspection
            with open("page_dump.html", "w", encoding="utf-8") as f:
                f.write(page.content())

            in_stock = False

            # Check all buttons for "Add to Cart" and related keywords
            buttons = page.locator("button")
            for i in range(buttons.count()):
                try:
                    btn = buttons.nth(i)
                    text = btn.text_content().strip().lower()
                    if any(keyword in text for keyword in IN_STOCK_KEYWORDS):
                        log("✅ Product appears to be IN STOCK (button).")
                        log_to_file("✅ Product appears to be IN STOCK.")
                        in_stock = True
                        break
                except:
                    continue

            # Fallback: span and a tags
            if not in_stock:
                extra_tags = page.locator("span, a")
                for i in range(extra_tags.count()):
                    try:
                        el = extra_tags.nth(i)
                        text = el.text_content().strip().lower()
                        if any(keyword in text for keyword in IN_STOCK_KEYWORDS):
                            log("✅ Product appears to be IN STOCK (fallback span/a).")
                            log_to_file("✅ Product appears to be IN STOCK.")
                            in_stock = True
                            break
                    except:
                        continue

            # Final fallback: check raw HTML for out-of-stock
            if not in_stock:
                full_text = page.content().lower()
                if any(keyword in full_text for keyword in OUT_OF_STOCK_KEYWORDS):
                    log("❌ Product is OUT OF STOCK.")
                    log_to_file("❌ Product is OUT OF STOCK.")
                else:
                    log("⚠️ Couldn't determine stock status.")
                    log_to_file("⚠️ Couldn't determine stock status.")

            time.sleep(3)
            browser.close()
            return "✅ Product is available!" if in_stock else "❌ Product is out of stock.", in_stock

    except Exception as e:
        error = f"🚫 Error: {e}"
        log(error)
        log_to_file(error)
        return error, False

def add_to_cart(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        time.sleep(5)

        close_popup(page)

        buttons = page.locator("button")
        for i in range(buttons.count()):
            try:
                button = buttons.nth(i)
                text = button.text_content().strip().lower()
                # Check for "Add To Cart" or any related keywords
                if any(keyword in text for keyword in IN_STOCK_KEYWORDS) and button.is_visible() and button.is_enabled():
                    button.click()
                    print("🛒 'Add to Cart' clicked.")
                    break
            except:
                continue

        time.sleep(5)
        browser.close()

def open_browser_view(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        time.sleep(8)
        browser.close()
