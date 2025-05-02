import tkinter as tk
from tkinter import ttk
import threading
from monitor import check_availability, open_browser_view, add_to_cart

def start_monitoring():
    url = url_entry.get().strip()
    if not url:
        log("⚠️ Please enter a product URL.")
        return

    log("🔍 Monitoring started...")
    # Run availability check in a separate thread to avoid GUI freezing
    threading.Thread(target=monitor_thread, args=(url,), daemon=True).start()

def monitor_thread(url):
    # Call check_availability and pass a callback for logging
    status, available = check_availability(url, log_callback=log)

    # Show status in the log
    log(status)

    # Open browser window after status
    log("🖥️ Opening browser to show current page...")
    open_browser_view(url)

    # If product is available and checkbox is selected, try adding to cart
    if available and add_to_cart_checkbox_var.get():
        log("🔒 Adding product to cart...")
        add_to_cart(url)

def log(message):
    log_output.insert(tk.END, message + "\n")
    log_output.see(tk.END)

# GUI setup
root = tk.Tk()
root.title("Product Availability Monitor")
root.geometry("600x450")

# URL Entry
ttk.Label(root, text="Product URL:").pack(pady=(10, 0))
url_entry = ttk.Entry(root, width=80)
url_entry.pack(pady=5)

# Add to Cart Checkbox
add_to_cart_checkbox_var = tk.BooleanVar()
add_to_cart_checkbox = ttk.Checkbutton(root, text="Add to Cart if Available", variable=add_to_cart_checkbox_var)
add_to_cart_checkbox.pack(pady=10)

# Start Button
start_button = ttk.Button(root, text="Start Monitoring", command=start_monitoring)
start_button.pack(pady=10)

# Log Output
log_output = tk.Text(root, height=15, wrap=tk.WORD)
log_output.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

root.mainloop()