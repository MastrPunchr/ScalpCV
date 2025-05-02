#midnight releases suck, AI to order thing for you
import cv2
import easyocr
import matplotlib.pyplot as plt
import numpy as np

img = cv2.imread("dkcrHD.png")

reader = easyocr.Reader(['en'], gpu=True)
result = reader.readtext(img)

threshold = 0.25

for r_, r in enumerate(result):

    bbox, text, score = r    

    top_left = tuple(map(int, bbox[0]))
    bottom_right = tuple(map(int, bbox[2]))

    print(r)
    if score > threshold:
            cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 5)
            cv2.putText(img, text, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 0, 0), 2)

plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.axis("off")
plt.show()