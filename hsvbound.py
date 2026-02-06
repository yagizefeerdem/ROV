import cv2
import numpy as np

def nothing(x):
    pass

image = cv2.imread('ralcolors.png')
image = cv2.resize(image, (750, 450))
cv2.namedWindow('Image')

cv2.createTrackbar('Lower H', 'Image', 0, 179, nothing)
cv2.createTrackbar('Lower S', 'Image', 0, 255, nothing)
cv2.createTrackbar('Lower V', 'Image', 0, 255, nothing)
cv2.createTrackbar('Upper H', 'Image', 0, 179, nothing)
cv2.createTrackbar('Upper S', 'Image', 0, 255, nothing)
cv2.createTrackbar('Upper V', 'Image', 0, 255, nothing)

cv2.setTrackbarPos('Upper H', 'Image', 179)
cv2.setTrackbarPos('Upper S', 'Image', 255)
cv2.setTrackbarPos('Upper V', 'Image', 255)

while True:
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_h = cv2.getTrackbarPos('Lower H', 'Image')
    lower_s = cv2.getTrackbarPos('Lower S', 'Image')
    lower_v = cv2.getTrackbarPos('Lower V', 'Image')
    upper_h = cv2.getTrackbarPos('Upper H', 'Image')
    upper_s = cv2.getTrackbarPos('Upper S', 'Image')
    upper_v = cv2.getTrackbarPos('Upper V', 'Image')

    lower_bound = np.array([lower_h, lower_s, lower_v])
    upper_bound = np.array([upper_h, upper_s, upper_v])

    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    mask = cv2.bitwise_and(image, image, mask=mask)

    cv2.imshow('Image', mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
