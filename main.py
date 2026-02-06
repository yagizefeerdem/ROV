import cv2, vtk, sys
import numpy as np
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QPalette, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.uic import loadUi

import prevezeUtils

yellow = (np.array([5, 55, 95]), np.array([32, 255, 255]))
blue = (np.array([105, 123, 0]), np.array([131, 255, 255]))
karton = (np.array([4, 66, 104]), np.array([18, 165, 186]))

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
shapeDetector   = prevezeUtils.ShapeDetector(yellow)
# serialComm      = prevezeUtils.SerialComm()

class PrevezeGUI(QMainWindow):

    def __init__(self):
        super(PrevezeGUI, self).__init__()
        loadUi('ui/prevezegui2.ui', self)
        self.setupUI()
        self.setupGyroLabel()
        self.comm = ""

    def setupUI(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loop)
        self.timer.start(10)

    def updateGyroLabel(self, data):
        
        # ax, ay, az, gx, gy, gz = data
        # pitch = np.arctan2(ax, np.sqrt(ay**2 + az**2)) * 180 / np.pi
        # roll = np.arctan2(ay, np.sqrt(ax**2 + az**2)) * 180 / np.pi
        # yaw = gz  # Assuming gyro z-axis is directly yaw
        
        # self.actor.RotateX(pitch)
        # self.actor.RotateY(roll)
        # self.actor.RotateZ(yaw)
        self.actor.RotateZ(np.radians(90))



        self.vtkWidget.GetRenderWindow().Render()

    def updateThrusterLabel(self, data):
        fl, fr, bl, br, ul, ur = data
        self.FL.setText(str(fl))
        self.FR.setText(str(fr))
        self.BL.setText(str(bl))
        self.BR.setText(str(br))
        self.UL.setText(str(ul))
        self.UR.setText(str(ur))
    
    def updateImageLabel(self, img, pred):
        h, w, ch = img.shape
        bytes_per_line = ch * w
        q_img = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        self.imageLabel.setPixmap(pixmap)
        self.predLabel.setText(pred)

    def updateSerialLabel(self, data):
        self.comm += str(data) + "\n"
        self.serialText.setPlainText(self.comm)

    def updateTorpedoLabel(self, data):
        
        data = int(data)

        if data:

            if data == 2:
                self.torpedo1.setVisible(False)

            elif data == 1:
                self.torpedo1.setVisible(False)
                self.torpedo2.setVisible(False)

            elif data == 0:
                self.torpedo1.setVisible(False)
                self.torpedo2.setVisible(False)
                self.torpedo3.setVisible(False)

    def updateNemLabel(self, nem):

        if nem:
            self.humidityLabel.setText("DETECTED")
        else:
            self.humidityLabel.setText("not detected")
        return
    
    def loop(self):

        succ, img = cap.read()
        pred = ""
        # datatype, data = serialComm.read()
        mode = self.comboBox.currentText()

        datatype, data = "", ""

        if mode == "Anomaly Detection":
            img, pred, box = shapeDetector(img)
            
        # if datatype == "ui-update":
        #     self.updateThrusterLabel(data[:6])
        #     print(data[:6])
        #     self.updateGyroLabel(data[6:-1])
        #     self.updateTorpedoLabel(data[-1])
        #     # self.updateNemLabel(data[-1])

        elif datatype == "ser-update":
            self.updateSerialLabel(data)

        self.updateImageLabel(img, pred)
        self.updateGyroLabel("")

        
    def setupGyroLabel(self):
        self.vtkWidget = QVTKRenderWindowInteractor(self.gyroLabel)
        layout = QVBoxLayout()
        layout.addWidget(self.vtkWidget)
        self.gyroLabel.setLayout(layout)

        self.renderer = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.vtkWidget.GetRenderWindow().GetInteractor()

        self.loadSTLModel('ui/model1.stl')
        self.renderer.ResetCamera()
        self.interactor.Initialize()
        self.interactor.Start()

    def loadSTLModel(self, file_path):
        self.reader = vtk.vtkSTLReader()
        self.reader.SetFileName(file_path)

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.reader.GetOutputPort())

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper)

        self.renderer.AddActor(self.actor)
        self.renderer.SetBackground(29/255, 46/255, 64/255)  # Set background color to #343434
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    palette = QPalette()
    # rgb(93, 225, 175)
    # palette.setColor(QPalette.Window, QColor(53, 53, 53))
    # palette.setColor(QPalette.WindowText, Qt.white)
    # palette.setColor(QPalette.Base, QColor(25, 25, 25))
    # palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    # palette.setColor(QPalette.ToolTipBase, Qt.white)
    # palette.setColor(QPalette.ToolTipText, Qt.white)
    # palette.setColor(QPalette.Text, Qt.white)
    # palette.setColor(QPalette.Button, QColor(53, 53, 53))
    # palette.setColor(QPalette.ButtonText, Qt.white)
    # palette.setColor(QPalette.BrightText, Qt.red)
    # palette.setColor(QPalette.Link, QColor(42, 130, 218))
    # palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    # palette.setColor(QPalette.HighlightedText, Qt.black)
    palette.setColor(QPalette.Window, QColor(29, 46, 64))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(29, 46, 64))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(29, 46, 64))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    app.setStyle("Fusion")
    mainWindow = PrevezeGUI()
    mainWindow.show()
    sys.exit(app.exec_())
