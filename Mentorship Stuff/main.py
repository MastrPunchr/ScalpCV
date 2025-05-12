import threading
import time
from monitor import check_availability, open_browser_view, add_to_cart

ASCII_ART = r"""
+--------------------------------------------------------------+
|   _____              _          _____ __      __             |
|  / ____|            | |        / ____|\ \    / /             |
| | (___    ___  __ _ | | _ __  | |      \ \  / /              |
|  \___ \  / __|/ _` || || '_ \ | |       \ \/ /               |
|  ____) || (__| (_| || || |_) || |____    \  /                |
| |_____/  \___|\__,_||_|| .__/  \_____|    \/                 |
|                        | |                                   |
|                        |_|                                   |
+--------------------------------------------------------------+
"""

def log(message):
    print(message)

def monitor_thread(url, auto_add):
    print("🔍 Monitoring started...")

    status, available = check_availability(url, log_callback=log)
    log(status)

    print("🖥️ Opening browser to show current page...")
    open_browser_view(url)

    if available and auto_add:
        print("🔒 Adding product to cart...")
        add_to_cart(url)

def main():
    print(ASCII_ART)
    print("🛒 Product Monitor v1.0\n")

    url = input("🔗 Enter Product URL: ").strip()
    if not url:
        print("⚠️ URL cannot be empty.")
        return

    auto_add_input = input("🛒 Add to cart if available? (y/n): ").strip().lower()
    auto_add = auto_add_input == 'y'

    thread = threading.Thread(target=monitor_thread, args=(url, auto_add), daemon=True)
    thread.start()
    thread.join()

    print("\n✅ Monitoring finished.")

if __name__ == "__main__":
    main()