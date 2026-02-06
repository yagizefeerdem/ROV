import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

# Pi Camera'yı başlat
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

# Kameranın başlaması için kısa bir süre bekle
time.sleep(0.1)

# Pi Camera'dan görüntüleri yakala
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array

    # Görüntüyü göster
    cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF

    # `q` tuşuna basıldığında döngüyü sonlandır
    if key == ord("q"):
        break

    # RawCapture'ı temizle
    rawCapture.truncate(0)

# Tüm pencereleri kapat
cv2.destroyAllWindows()
