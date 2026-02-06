import cv2
import numpy as np
import serial

class ShapeDetector:
    def __init__(self, colorbound):
        self.lower_color = colorbound[0]
        self.upper_color = colorbound[1]

    def evaluate_shape(self, contour):
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        corners = len(approx)

        contour_area = cv2.contourArea(contour)
        rect = cv2.minAreaRect(contour)
        rect_area = rect[1][0] * rect[1][1]
        (x, y), radius = cv2.minEnclosingCircle(contour)
        circle_area = radius ** 2 * 3.14

        shape = ""

        if corners == 3:
            shape = "Ucgen"
        elif corners == 4:
            if contour_area / rect_area < 0.9:
                shape = "Trombus"
            else:
                width, height = rect[1]
                aspect_ratio = width / height

                if 0.9 <= aspect_ratio <= 1.1:
                    shape = "Kare"
                else:
                    shape = "Dortgen"
        elif corners == 5:
            shape = "Besgen"
        elif corners == 6:
            shape = "Altigen"
        elif corners == 8:
            width, height = rect[1]
            aspect_ratio = width / height

            if 0.9 <= aspect_ratio <= 1.1:
                if contour_area / circle_area > 0.87:
                    shape = "Daire"
                else:
                    shape = "Yonca"
            else:
                shape = "Elips"
        elif corners == 10:
            shape = "Yildiz"
        else:
            shape = "No Shape"

        return shape, corners

    def __call__(self, image):
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv = cv2.blur(hsv, (3, 3))
        mask = cv2.inRange(hsv, self.lower_color, self.upper_color)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        maxAreaIndex = 0
        maxArea = 0
        text = ""
        box = 0

        for i in range (len(contours)):
            area = cv2.contourArea(contours[i])
            if area > maxArea:
                maxAreaIndex = i
                maxArea = area

        if contours:
            if maxArea > 100:
                contour = contours[maxAreaIndex]
                cv2.drawContours(rgb, contour, -1, (255,0,255), 7)

                text, corners = self.evaluate_shape(contour)
                font = cv2.FONT_HERSHEY_PLAIN
                cv2.putText(rgb, text, (50, 100), font, 2, (255, 0, 255), 3, cv2.LINE_AA)
                cv2.putText(rgb, str(corners), (50, 400), font, 2, (255, 0, 255), 3, cv2.LINE_AA)

                rect = cv2.minAreaRect(contour)
                box = cv2.boxPoints(rect)
                box = np.int0(box)

                mx = (box[0][0] + box[1][0] + box[2][0] + box[3][0])//4
                my = (box[0][1] + box[1][1] + box[2][1] + box[3][1])//4

                mid = (mx,my)

                if not corners == 8:
                    cv2.drawContours(rgb,[box],0,(0,0,255),2)
                    cv2.circle(rgb, mid, 5, (0, 0, 255), -1)

                else:
                    (x,y),radius = cv2.minEnclosingCircle(contour)
                    center = (int(x),int(y))
                    radius = int(radius)
                    cv2.circle(rgb,center,radius,(0,255,0),2)
                    cv2.circle(rgb, mid, 5, (0, 0, 255), -1)

        return rgb, text, box

class SerialComm:

    def __init__(self, port='COM14', baudrate=115200):
        self.ser = serial.Serial(port, baudrate)

    def read(self):
        if self.ser.in_waiting:
            data = self.ser.readline()
            data = data.decode("utf-8")
            datatype = ""
            if data[0] == "*" and len(data) > 1:
                data = data[1:].split(",")
                data = [float(d) for d in data]
                datatype = "ui-update"
            elif data[0] == "!":
                datatype = "ser-update"
                data = data[1:]
            else:
                datatype = ""
            return datatype, data
        else:
            return "", ""

    def write(self, data):
        self.ser.write(str(data).encode("utf-8"))

class AutoPilot:

    def __init__(self, detector:ShapeDetector, ser:SerialComm):

        self.detector = detector
        self.ser = ser
        self.tolerance = 10
    
    def __call__(self, img):

        img, _, box = self.detector(img)
        ux, uy, uz, yaw = 0, 0, 0, 0

        if box is None: 
            yaw = 1

        else:
            img_height, img_width = img.shape[:2]
            mx = sum(point[0] for point in box) // 4
            my = sum(point[1] for point in box) // 4

            error_x = mx - (img_width // 2)
            error_y = my - (img_height // 2)

            if abs(error_x) < self.tolerance and abs(error_y) < self.tolerance:
                ux = 1
            else:
                uz  = -0.1 * error_y
                yaw = -0.1 * error_x

        
        self.ser.write(f"{ux},{uy},{uz},{yaw}")
        return box, ux, uy, uz, yaw





