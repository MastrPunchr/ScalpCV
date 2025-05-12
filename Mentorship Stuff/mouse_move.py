import cv2
import easyocr
import numpy as np
import mouse
import time
import pyautogui  # Used to get actual screen resolution

# Load screenshot
img = cv2.imread("popup_closed.png")
if img is None:
    raise FileNotFoundError("❌ Could not load 'popup_closed.png'")

# Get actual screen resolution
screen_width, screen_height = pyautogui.size()

# Get image resolution
img_height, img_width = img.shape[:2]

# OCR
reader = easyocr.Reader(['en'], gpu=True)
results = reader.readtext(img)

# Keywords with priority (lower index = higher priority)
KEYWORDS = ["add to cart", "add to order", "purchase", "buy", "order", "get", "add"]
threshold = 0.25
matches = []

# Find matches
for bbox, text, score in results:
    if score < threshold:
        continue

    cleaned = text.lower().strip().replace("\n", " ")
    cleaned = " ".join(cleaned.split())

    for priority, keyword in enumerate(KEYWORDS):
        if keyword in cleaned:
            pts = np.array(bbox)
            x_coords = pts[:, 0]
            y_coords = pts[:, 1]
            x_min, x_max = int(np.min(x_coords)), int(np.max(x_coords))
            y_min, y_max = int(np.min(y_coords)), int(np.max(y_coords))

            # Add padding
            padding_x = int((x_max - x_min) * 0.3)
            padding_y = int((y_max - y_min) * 0.6)

            x_min = max(0, x_min - padding_x)
            x_max = min(img_width, x_max + padding_x)
            y_min = max(0, y_min - padding_y)
            y_max = min(img_height, y_max + padding_y)

            center_x_img = int((x_min + x_max) / 2)
            center_y_img = int((y_min + y_max) / 2)

            # Scale to screen coordinates
            scale_x = screen_width / img_width
            scale_y = screen_height / img_height
            center_x_screen = int(center_x_img * scale_x)
            center_y_screen = int(center_y_img * scale_y)

            matches.append({
                "priority": priority,
                "coords": (center_x_screen, center_y_screen),
                "text": text,
                "score": score
            })
            break

# Sort by priority
target_coords = None
if matches:
    matches.sort(key=lambda m: m["priority"])
    best_match = matches[0]
    target_coords = best_match["coords"]
    print(f"✅ Selected '{best_match['text']}' at screen coords {target_coords} with confidence {best_match['score']:.2f}")
else:
    print("❌ No matching keyword found.")

# Move mouse in a straight line
def move_mouse_straight(x_target, y_target):
    x_start, y_start = mouse.get_position()
    steps = 100
    for i in range(steps + 1):
        t = i / steps
        x = int(x_start + (x_target - x_start) * t)
        y = int(y_start + (y_target - y_start) * t)
        mouse.move(x, y, absolute=True, duration=0.002)
    time.sleep(0.05)
    mouse.click()

# Move if target found
if target_coords:
    move_mouse_straight(*target_coords)