# mouse_clicker.py
import cv2
import easyocr
import numpy as np
import threading
import mouse

img = cv2.imread("popup_closed.png")

reader = easyocr.Reader(['en'], gpu=True)
results = reader.readtext(img)

KEYWORDS = ["add to cart", "add", "buy", "purchase", "order", "get", "add to order"]
threshold = 0.25
purchase_coords = None

for bbox, text, score in results:
    if score < threshold:
        continue
    cleaned = text.strip().lower()
    for keyword in KEYWORDS:
        if keyword in cleaned:
            pts = np.array(bbox)
            center_x = int(np.mean(pts[:, 0]))
            center_y = int(np.mean(pts[:, 1]))
            purchase_coords = (center_x, center_y)
            print(f"Found '{text}' at {purchase_coords}")
            break
    if purchase_coords:
        break

def move_mouse_curve(x_target, y_target):
    x_start, y_start = mouse.get_position()
    steps = 100
    ctrl_x = (x_start + x_target) / 2
    ctrl_y = min(y_start, y_target) - abs(x_target - x_start) * 0.3

    for i in range(steps + 1):
        t = i / steps
        x = int((1 - t)**2 * x_start + 2 * (1 - t) * t * ctrl_x + t**2 * x_target)
        y = int((1 - t)**2 * y_start + 2 * (1 - t) * t * ctrl_y + t**2 * y_target)
        mouse.move(x, y, absolute=True, duration=0.003)

    mouse.click()

if purchase_coords:
    offset_x, offset_y = 18, 18
    adjusted_coords = (purchase_coords[0] + offset_x, purchase_coords[1] + offset_y)
    threading.Thread(target=move_mouse_curve, args=adjusted_coords).start()
else:
    print("No purchase-related text found.")