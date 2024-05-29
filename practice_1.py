import ctypes
import sys
import os
import webbrowser
import cv2
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtWebEngineWidgets
import SQL
import requests
import json
from threading import *
import socket
import plotly.graph_objects as go
from collections import deque
import time
import what3words

selectedUnit = ""
selectedIP = ""
selectedVictron = ""
selectedCompany = ""
selectedCCTV = ""
selectedUnitType = ""
selectedCamera = ""
selectedEfoyID = ""

userRights = ""
userCompany = ""

unitSolar = 0
unitVoltage = 0
unitLoad = 0

username = ""

CameraNumber = 1

sunstonePassword = "(10GIN$t0n3)"
wjPassword = "12Sunstone34"

mapboxAccessToken = "pk.eyJ1IjoiamFja2dhbmRlcmNvbXB0b24iLCJhIjoiY2x1bW16MmVzMTViajJqbjI0N3RuOGhhOCJ9.Kl6jwZjBEtGoM1C_5NyLJg"

geocoder = what3words.Geocoder("RMNUBSDA")

def pullVictronData(unitName):
    global unitSolar
    global unitVoltage
    global unitLoad

    data = SQL.fetchVictronData(unitName)

    for row in data:
        altered = list(row)
        unitSolar = altered[0]
        unitVoltage = altered[1]
        unitLoad = altered[2]

def axisPath(IPaddress, cameraNumber):
    Axis = f"rtsp://root:12Sunstone34@{IPaddress}:{cameraNumber}554/axis-media/media.amp"

    return Axis

def hikPath(IPaddress, cameraNumber):
    Hik = f"rtsp://admin:(10GIN$t0n3)@{IPaddress}:{cameraNumber}554/Streaming/Channels/102/?transportmode=unicast"

    return Hik

def hanwhaPath(IPaddress, cameraNumber):
    Hanwha = f"rtsp://admin:12Sunstone34@{IPaddress}:{cameraNumber}554/profile2/media.smp"

    return Hanwha


def dahuaPath(IPaddress, cameraNumber):
    Dahua = f"rtsp://admin:12Sunstone34@{IPaddress}:{cameraNumber}554/live"

    return Dahua


def resourcePath(relativePath):
    try:
        basePath = sys._MEIPASS
    except Exception:
        basePath = os.path.abspath(".")

    return os.path.join(basePath, relativePath)

def checkURL(IPAddress, Port, Timeout):
    socketOpen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketOpen.settimeout(Timeout)
    try:
        socketOpen.connect((IPAddress, Port))
    except:
        return 0
    else:
        socketOpen.close()
        return 1

class CameraWidget(QWidget):

    def __init__(self, Width, Height, streamLink=0):
        super(CameraWidget, self).__init__()

        self.Deque = deque(maxlen=1)

        self.screenWidth = Width - 16
        self.screenHeight = Height - 16

        self.cameraStreamLink = streamLink

        self.Online = False
        self.Capture = None
        self.videoFrame = QLabel()

        self.loadNetworkStream()

        self.getFrameThread = Thread(target=self.getFrame, args=())
        self.getFrameThread.daemon = True
        self.getFrameThread.start()

        self.Timer = QTimer()
        self.Timer.timeout.connect(self.setFrame)
        self.Timer.start(1)

    def loadNetworkStream(self):

        def loadNetworkStreamThread():
            if self.verifyNetworkStream(self.cameraStreamLink):
                self.Capture = cv2.VideoCapture(self.cameraStreamLink)
                self.Online = True

        self.loadStreamThread = Thread(target=loadNetworkStreamThread, args=())
        self.loadStreamThread.daemon = True
        self.loadStreamThread.start()

    def verifyNetworkStream(self, Link):
        # Attempts to get a frame from the given RTSP Stream

        Cap = cv2.VideoCapture(Link)
        if not Cap.isOpened():
            return False
        Cap.release()
        return True

    def getFrame(self):
        # Function reads the frame -> resizes and then converts the image stored to a pixmap to be used in window

        while True:
            try:
                if self.Capture.isOpened() and self.Online:
                    # Read next frame from stream and insert into deque
                    Status, Frame = self.Capture.read()
                    if Status:
                        self.Deque.append(Frame)
                    else:
                        self.Capture.release()
                        self.Online = False
                else:

                    self.loadNetworkStream()
                    self.Spin(2)
                self.Spin(.001)
            except AttributeError:
                pass

    def Spin(self, seconds):
        # Pauses stream so program stays alive

        timeEnd = time.time() + seconds
        while time.time() < timeEnd:
            QApplication.processEvents()

    def setFrame(self):
        # setting Pixmap Image to a video frame

        if not self.Online:
            self.Spin(1)
            return

        if self.Deque and self.Online:
            # Grab latest frame
            Frame = self.Deque[-1]

            self.Frame = cv2.resize(Frame, (self.screenWidth, self.screenHeight))

            # Convert to pixmap and set to video frame
            self.Image = QImage(self.Frame, self.Frame.shape[1], self.Frame.shape[0], QImage.Format_RGB888).rgbSwapped()
            self.Pixmap = QPixmap.fromImage(self.Image)
            self.videoFrame.setPixmap(self.Pixmap)

    def getVideoFrame(self):
        return self.videoFrame

class allCamerasView(QWidget):
    def __init__(self):

        cameraIcon = resourcePath("Assets/Images/CCTV.png")  # importing camera Icon

        super().__init__()

        self.setWindowTitle("View All Cameras")
        self.setGeometry(0, 0, 1280, 720)
        self.setFixedSize(1280, 720)
        self.setWindowIcon(QIcon(cameraIcon))
        self.setWindowIconText("Camera")

        layout = QGridLayout()

        if selectedCamera.lower() == "axis":

            if selectedCCTV == 4:
                cameraOneLink = axisPath(selectedIP, 1)
                cameraTwoLink = axisPath(selectedIP, 2)
                cameraThreeLink = axisPath(selectedIP, 3)
                cameraFourLink = axisPath(selectedIP, 4)

            if selectedCCTV == 3:
                cameraOneLink = axisPath(selectedIP, 1)
                cameraTwoLink = axisPath(selectedIP, 2)
                cameraThreeLink = axisPath(selectedIP, 3)

            if selectedCCTV == 2:
                cameraOneLink = axisPath(selectedIP, 1)
                cameraTwoLink = axisPath(selectedIP, 2)

        elif selectedCamera.lower() == "hik" or selectedCamera.lower() == "hikvision":

            if selectedCCTV == 4:
                cameraOneLink = hikPath(selectedIP, 1)
                cameraTwoLink = hikPath(selectedIP, 2)
                cameraThreeLink = hikPath(selectedIP, 3)
                cameraFourLink = hikPath(selectedIP, 4)

            if selectedCCTV == 3:
                cameraOneLink = hikPath(selectedIP, 1)
                cameraTwoLink = hikPath(selectedIP, 2)
                cameraThreeLink = hikPath(selectedIP, 3)

            if selectedCCTV == 2:
                cameraOneLink = hikPath(selectedIP, 1)
                cameraTwoLink = hikPath(selectedIP, 2)

        elif selectedCamera.lower() == "hanwha" or selectedCamera.lower() == "wisenet":

            if selectedCCTV == 4:
                cameraOneLink = hanwhaPath(selectedIP, 1)
                cameraTwoLink = hanwhaPath(selectedIP, 2)
                cameraThreeLink = hanwhaPath(selectedIP, 3)
                cameraFourLink = hanwhaPath(selectedIP, 4)

            if selectedCCTV == 3:
                cameraOneLink = hanwhaPath(selectedIP, 1)
                cameraTwoLink = hanwhaPath(selectedIP, 2)
                cameraThreeLink = hanwhaPath(selectedIP, 3)

            if selectedCCTV == 2:
                cameraOneLink = hanwhaPath(selectedIP, 1)
                cameraTwoLink = hanwhaPath(selectedIP, 2)

        elif selectedCamera.lower() == "dahua":

            if selectedCCTV == 4:
                cameraOneLink = dahuaPath(selectedIP, 1)
                cameraTwoLink = dahuaPath(selectedIP, 2)
                cameraThreeLink = dahuaPath(selectedIP, 3)
                cameraFourLink = dahuaPath(selectedIP, 4)

            if selectedCCTV == 3:
                cameraOneLink = dahuaPath(selectedIP, 1)
                cameraTwoLink = dahuaPath(selectedIP, 2)
                cameraThreeLink = dahuaPath(selectedIP, 3)

            if selectedCCTV == 2:
                cameraOneLink = dahuaPath(selectedIP, 1)
                cameraTwoLink = dahuaPath(selectedIP, 2)

        if selectedCCTV == 4:
            self.cameraOne = CameraWidget(640, 360, cameraOneLink)
            self.cameraTwo = CameraWidget(640, 360, cameraTwoLink)
            self.cameraThree = CameraWidget(640, 360, cameraThreeLink)
            self.cameraFour = CameraWidget(640, 360, cameraFourLink)

            layout.addWidget(self.cameraOne.getVideoFrame(), 0, 0, 1, 1)
            layout.addWidget(self.cameraTwo.getVideoFrame(), 0, 1, 1, 1)
            layout.addWidget(self.cameraThree.getVideoFrame(), 1, 0, 1, 1)
            layout.addWidget(self.cameraFour.getVideoFrame(), 1, 1, 1, 1)

        elif selectedCCTV == 3:
            self.cameraOne = CameraWidget(640, 360, cameraOneLink)
            self.cameraTwo = CameraWidget(640, 360, cameraTwoLink)
            self.cameraThree = CameraWidget(640, 360, cameraThreeLink)

            layout.addWidget(self.cameraOne.getVideoFrame(), 0, 0, 1, 1)
            layout.addWidget(self.cameraTwo.getVideoFrame(), 0, 1, 1, 1)
            layout.addWidget(self.cameraThree.getVideoFrame(), 1, 0, 1, 1)

        elif selectedCCTV == 2:
            self.cameraOne = CameraWidget(640, 360, cameraOneLink)
            self.cameraTwo = CameraWidget(640, 360, cameraTwoLink)

            layout.addWidget(self.cameraOne.getVideoFrame(), 0, 0, 1, 1)
            layout.addWidget(self.cameraTwo.getVideoFrame(), 0, 1, 1, 1)

        self.setLayout(layout)

    def closeEvent(self, event):

        if selectedCCTV == 4:
            self.cameraOne.close()
            self.cameraTwo.close()
            self.cameraThree.close()
            self.cameraFour.close()

        elif selectedCCTV == 3:
            self.cameraOne.close()
            self.cameraTwo.close()
            self.cameraThree.close()

        elif selectedCCTV == 2:
            self.cameraOne.close()
            self.cameraTwo.close()

        self.close()

        if str(selectedUnitType) == "ARC":
            pullVictronData(selectedUnit)

            self.openARCDashboard = arcDashboard()
            self.openARCDashboard.show()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openARCDashboard.frameGeometry()
            Geo.moveCenter(Center)
            self.openARCDashboard.move(Geo.topLeft())

            self.hide()
        elif str(selectedUnitType) == "IO":
            self.openIODashboard = ioDashboard()
            self.openIODashboard.show()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openIODashboard.frameGeometry()
            Geo.moveCenter(Center)
            self.openIODashboard.move(Geo.topLeft())

            self.hide()

class singleCameraView(QWidget):
    def __init__(self):

        cameraIcon = resourcePath("Assets/Images/CCTV.png")  # importing camera Icon

        super().__init__()

        self.setWindowTitle(f"Camera {CameraNumber}")
        self.setGeometry(0, 0, 1280, 720)
        self.setFixedSize(1280, 720)
        self.setWindowIcon(QIcon(cameraIcon))
        self.setWindowIconText("Camera")

        layout = QGridLayout()

        if selectedCamera.lower() == "axis":

            cameraOneLink = axisPath(selectedIP, CameraNumber)

        elif selectedCamera.lower() == "hik" or selectedCamera.lower() == "hikvision":

            cameraOneLink = hikPath(selectedIP, CameraNumber)

        elif selectedCamera.lower() == "hanwha" or selectedCamera.lower() == "wisenet":

            cameraOneLink = hanwhaPath(selectedIP, CameraNumber)

        elif selectedCamera.lower() == "dahua":

            cameraOneLink = dahuaPath(selectedIP, CameraNumber)

        self.cameraOne = CameraWidget(1280, 720, cameraOneLink)

        layout.addWidget(self.cameraOne.getVideoFrame(), 0, 0, 1, 1)

        self.setLayout(layout)

    def closeEvent(self, event):

        self.cameraOne.close()

        self.close()

        if str(selectedUnitType) == "ARC":
            pullVictronData(selectedUnit)

            self.openARCDashboard = arcDashboard()
            self.openARCDashboard.show()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openARCDashboard.frameGeometry()
            Geo.moveCenter(Center)
            self.openARCDashboard.move(Geo.topLeft())

            self.hide()
        elif str(selectedUnitType) == "IO":
            self.openIODashboard = ioDashboard()
            self.openIODashboard.show()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openIODashboard.frameGeometry()
            Geo.moveCenter(Center)
            self.openIODashboard.move(Geo.topLeft())

            self.hide()

class ioDashboard(QWidget):
    def __init__(self):

        ioBoxIcon = resourcePath("Assets/Images/IOBox.png")
        cameraPath = resourcePath("Assets/Images/CCTV.png")

        super().__init__()

        self.setWindowTitle("IO Box Dashboard")
        self.setGeometry(0, 0, 760, 200)
        self.setWindowIcon(QIcon(ioBoxIcon))
        self.setWindowIconText("IO Box")

        layout = QGridLayout()

        unitLabel = QLabel(selectedUnit)
        unitLabel.setStyleSheet("font: bold 14px;")
        unitLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pixmap = QPixmap(cameraPath)

        self.allCameras = QLabel()
        self.allCameras.setPixmap(pixmap)
        self.allCameras.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.allCamerasButton = QPushButton("All Cameras")
        self.allCamerasButton.clicked.connect(self.viewAllCameras)

        self.Camera1 = QLabel()
        self.Camera1.setPixmap(pixmap)
        self.Camera1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.camera1Button = QPushButton("Camera 1")
        self.camera1Button.clicked.connect(lambda checked=None, text=1: self.viewIndividualCamera(text))

        self.Camera2 = QLabel()
        self.Camera2.setPixmap(pixmap)
        self.Camera2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.camera2Button = QPushButton("Camera 2")
        self.camera2Button.clicked.connect(lambda checked=None, text=2: self.viewIndividualCamera(text))

        layout.addWidget(self.Camera2, 1, 2)
        layout.addWidget(self.camera2Button, 2, 2)

        self.Camera3 = QLabel()
        self.Camera3.setPixmap(pixmap)
        self.Camera3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.camera3Button = QPushButton("Camera 3")
        self.camera3Button.clicked.connect(lambda checked=None, text=3: self.viewIndividualCamera(text))

        layout.addWidget(self.Camera3, 1, 3)
        layout.addWidget(self.camera3Button, 2, 3)

        self.Camera4 = QLabel()
        self.Camera4.setPixmap(pixmap)
        self.Camera4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.camera4Button = QPushButton("Camera 4")
        self.camera4Button.clicked.connect(lambda checked=None, text=4: self.viewIndividualCamera(text))

        layout.addWidget(self.Camera4, 1, 4)
        layout.addWidget(self.camera4Button, 2, 4)

        self.routerButton = QPushButton("Router Webpage")
        self.routerButton.clicked.connect(self.openRouter)

        self.errorMessage = QLabel()
        self.errorMessage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if selectedCCTV == 1:

            self.Camera4.hide()
            self.camera4Button.hide()

            self.Camera3.hide()
            self.camera3Button.hide()

            self.Camera2.hide()
            self.camera2Button.hide()

            self.allCameras.hide()
            self.allCamerasButton.hide()

            layout.addWidget(unitLabel, 0, 0)

            layout.addWidget(self.Camera1, 1, 0)
            layout.addWidget(self.camera1Button, 2, 0)

            layout.addWidget(self.routerButton, 3, 0)

            layout.addWidget(self.errorMessage, 4, 0)

        elif selectedCCTV == 2:

            self.Camera4.hide()
            self.camera4Button.hide()

            self.Camera3.hide()
            self.camera3Button.hide()

            layout.addWidget(unitLabel, 0, 2)

            layout.addWidget(self.allCameras, 1, 0)
            layout.addWidget(self.allCamerasButton, 2, 0)

            layout.addWidget(self.Camera1, 1, 1)
            layout.addWidget(self.camera1Button, 2, 1)

            layout.addWidget(self.routerButton, 3, 1, 1, 1)

            layout.addWidget(self.errorMessage, 4, 0)


        elif selectedCCTV == 3:

            self.Camera4.hide()
            self.camera4Button.hide()

            layout.addWidget(unitLabel, 0, 0)

            layout.addWidget(self.allCameras, 1, 0)
            layout.addWidget(self.allCamerasButton, 2, 0)

            layout.addWidget(self.Camera1, 1, 1)
            layout.addWidget(self.camera1Button, 2, 1)

            layout.addWidget(self.routerButton, 3, 1, 1, 2)

            layout.addWidget(self.errorMessage, 4, 1, 1, 2)


        else:

            layout.addWidget(unitLabel, 0, 2)

            layout.addWidget(self.allCameras, 1, 0)
            layout.addWidget(self.allCamerasButton, 2, 0)

            layout.addWidget(self.Camera1, 1, 1)
            layout.addWidget(self.camera1Button, 2, 1)

            layout.addWidget(self.routerButton, 3, 1, 1, 3)

            layout.addWidget(self.errorMessage, 4, 2)

        self.checkUnitStatus()

        self.setLayout(layout)

    def viewAllCameras(self):

        self.hide()

        self.allCameras = allCamerasView()
        self.allCameras.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.allCameras.frameGeometry()
        Geo.moveCenter(Center)
        self.allCameras.move(Geo.topLeft())

    def viewIndividualCamera(self, cameraNumber):
        global CameraNumber

        CameraNumber = cameraNumber

        self.hide()

        self.singleCamera = singleCameraView()
        self.singleCamera.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.singleCamera.frameGeometry()
        Geo.moveCenter(Center)
        self.singleCamera.move(Geo.topLeft())

    def checkUnitStatus(self):
        status = checkURL(selectedIP, 64430, 1)
        if status == 0:

            cameraPath = QPixmap(resourcePath("Assets/Images/OfflineCCTV.png"))

            self.errorMessage.setText("Unit Offline")
            self.errorMessage.setStyleSheet("color: red;"
                                            "font: bold 14px;")

            self.allCamerasButton.setEnabled(False)
            self.camera1Button.setEnabled(False)
            self.camera2Button.setEnabled(False)
            self.camera3Button.setEnabled(False)
            self.camera4Button.setEnabled(False)
            self.routerButton.setEnabled(False)
            self.allCameras.setPixmap(cameraPath)
            self.Camera1.setPixmap(cameraPath)
            self.Camera2.setPixmap(cameraPath)
            self.Camera3.setPixmap(cameraPath)
            self.Camera4.setPixmap(cameraPath)

        else:
            self.errorMessage.setText("Unit Online")
            self.errorMessage.setStyleSheet("color: green;"
                                            "font: bold 14px;")

    def openRouter(self):
        webbrowser.open(f"https://{selectedIP}:64430/")

    def closeEvent(self, event):
        if userRights == "ADMIN" or userRights == "SUPERADMIN":
            self.openMonitoring = adminMonitoring()
            self.openMonitoring.show()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openMonitoring.frameGeometry()
            Geo.moveCenter(Center)
            self.openMonitoring.move(Geo.topLeft())

            self.hide()
        elif userRights == "USER":
            self.openMonitoring = userMonitoring()
            self.openMonitoring.show()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openMonitoring.frameGeometry()
            Geo.moveCenter(Center)
            self.openMonitoring.move(Geo.topLeft())

            self.hide()

class arcDashboard(QWidget):
    def __init__(self):
        global unitVoltage
        global unitLoad
        global unitSolar

        windowIcon = resourcePath("Assets/Images/ARCunit.png")
        cameraPath = resourcePath("Assets/Images/CCTV.png")

        if unitVoltage == None or unitLoad == None or unitSolar == None:
            unitVoltage = 0.0
            unitLoad = 0.0
            unitSolar = 0.0
        else:
            unitVoltage = float(unitVoltage)
            unitLoad = int(unitLoad)
            unitSolar = int(unitSolar)

        if unitVoltage >= 25.5:
            self.batteryPath = resourcePath("Assets/Images/fullBattery.png")
        elif unitVoltage >= 24 and unitVoltage < 25.5:
            self.batteryPath = resourcePath("Assets/Images/half_battery.png")
        elif unitVoltage < 24 and unitVoltage >= 23.6:
            self.batteryPath = resourcePath("Assets/Images/low_battery.png")
        elif unitVoltage < 23.6:
            self.batteryPath = resourcePath("Assets/Images/battery.png")

        if unitLoad <= 0:
            self.loadPath = resourcePath("Assets/Images/ChargingLoad.png")
        else:
            self.loadPath = resourcePath("Assets/Images/Load.png")

        if unitSolar >= 400:
            self.sunPath = resourcePath("Assets/Images/very_sunny.png")
        elif unitSolar >= 200 and unitSolar < 400:
            self.sunPath = resourcePath("Assets/Images/Sun.png")
        elif unitSolar >= 100 and unitSolar < 200:
            self.sunPath = resourcePath("Assets/Images/cloudy.png")
        elif unitSolar < 100:
            self.sunPath = resourcePath("Assets/Images/cloud.png")

        super().__init__()

        self.setWindowTitle("ARC Dashboard")
        self.setGeometry(0, 0, 600, 300)
        self.setWindowIcon(QIcon(windowIcon))
        self.setWindowIconText("ARC")

        layout = QGridLayout()

        unitLabel = QLabel(selectedUnit)
        unitLabel.setStyleSheet("font: bold 14px;")
        unitLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sunPixmap = QPixmap(self.sunPath)
        batteryPixmap = QPixmap(self.batteryPath)
        loadPixmap = QPixmap(self.loadPath)
        cameraPixmap = QPixmap(cameraPath)

        self.sunImage = QLabel()
        self.sunImage.setPixmap(sunPixmap)
        self.sunImage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.solarPower = QLabel(str(unitSolar) + " W")

        layout.addWidget(self.sunImage, 1, 0)
        layout.addWidget(self.solarPower, 1, 1)

        self.batteryImage = QLabel()
        self.batteryImage.setPixmap(batteryPixmap)
        self.batteryImage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.batteryVoltage = QLabel(str(unitVoltage) + " V")

        layout.addWidget(self.batteryImage, 2, 0)
        layout.addWidget(self.batteryVoltage, 2, 1)

        self.loadImage = QLabel()
        self.loadImage.setPixmap(loadPixmap)
        self.loadImage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.loadDraw = QLabel(str(unitLoad) + " W")

        layout.addWidget(self.loadImage, 3, 0)
        layout.addWidget(self.loadDraw, 3, 1)

        self.allCameras = QLabel()
        self.allCameras.setPixmap(cameraPixmap)
        self.allCameras.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.allCamerasButton = QPushButton("All Cameras")
        self.allCamerasButton.clicked.connect(self.viewAllCameras)

        self.Camera1 = QLabel()
        self.Camera1.setPixmap(cameraPixmap)
        self.Camera1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.camera1Button = QPushButton("Camera 1")
        self.camera1Button.clicked.connect(lambda checked=None, text=1: self.viewIndividualCamera(text))

        self.Camera2 = QLabel()
        self.Camera2.setPixmap(cameraPixmap)
        self.Camera2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.camera2Button = QPushButton("Camera 2")
        self.camera2Button.clicked.connect(lambda checked=None, text=2: self.viewIndividualCamera(text))

        layout.addWidget(self.Camera2, 4, 2)
        layout.addWidget(self.camera2Button, 5, 2)

        self.Camera3 = QLabel()
        self.Camera3.setPixmap(cameraPixmap)
        self.Camera3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.camera3Button = QPushButton("Camera 3")
        self.camera3Button.clicked.connect(lambda checked=None, text=3: self.viewIndividualCamera(text))

        layout.addWidget(self.Camera3, 4, 3)
        layout.addWidget(self.camera3Button, 5, 3)

        self.Camera4 = QLabel()
        self.Camera4.setPixmap(cameraPixmap)
        self.Camera4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.camera4Button = QPushButton("Camera 4")
        self.camera4Button.clicked.connect(lambda checked=None, text=4: self.viewIndividualCamera(text))

        layout.addWidget(self.Camera4, 4, 4)
        layout.addWidget(self.camera4Button, 5, 4)

        victronButton = QPushButton("Victron Webpage")
        victronButton.clicked.connect(self.openVictron)

        self.routerButton = QPushButton("Router Webpage")
        self.routerButton.clicked.connect(self.openRouter)

        efoyButton = QPushButton("Efoy Webpage")
        efoyButton.clicked.connect(self.openEfoy)

        self.errorMessage = QLabel()
        self.errorMessage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if selectedCCTV == 1:

            self.Camera4.hide()
            self.camera4Button.hide()

            self.Camera3.hide()
            self.camera3Button.hide()

            self.Camera2.hide()
            self.camera2Button.hide()

            self.allCameras.hide()
            self.allCamerasButton.hide()

            layout.addWidget(unitLabel, 0, 1)

            layout.addWidget(self.Camera1, 4, 0)
            layout.addWidget(self.camera1Button, 5, 0)

            layout.addWidget(victronButton, 6, 0)
            layout.addWidget(self.routerButton, 6, 1)
            layout.addWidget(efoyButton, 6, 2)

            layout.addWidget(self.errorMessage, 7, 1)

        elif selectedCCTV == 2:

            layout.addWidget(unitLabel, 0, 2)

            self.Camera4.hide()
            self.camera4Button.hide()

            self.Camera3.hide()
            self.camera3Button.hide()

            layout.addWidget(self.allCameras, 4, 0)
            layout.addWidget(self.allCamerasButton, 5, 0)

            layout.addWidget(self.Camera1, 4, 1)
            layout.addWidget(self.camera1Button, 5, 1)

            layout.addWidget(victronButton, 6, 1)
            layout.addWidget(self.routerButton, 6, 2)
            layout.addWidget(efoyButton, 6, 3)

            layout.addWidget(self.errorMessage, 7, 1)

        elif selectedCCTV == 3:

            layout.addWidget(unitLabel, 0, 2)

            self.Camera4.hide()
            self.camera4Button.hide()

            layout.addWidget(self.allCameras, 4, 0)
            layout.addWidget(self.allCamerasButton, 5, 0)

            layout.addWidget(self.Camera1, 4, 1)
            layout.addWidget(self.camera1Button, 5, 1)

            layout.addWidget(victronButton, 6, 0)
            layout.addWidget(self.routerButton, 6, 1)
            layout.addWidget(efoyButton, 6, 2)

            layout.addWidget(self.errorMessage, 7, 0)

        else:

            layout.addWidget(unitLabel, 0, 2)

            layout.addWidget(self.allCameras, 4, 0)
            layout.addWidget(self.allCamerasButton, 5, 0)

            layout.addWidget(self.Camera1, 4, 1)
            layout.addWidget(self.camera1Button, 5, 1)

            layout.addWidget(victronButton, 6, 1)
            layout.addWidget(self.routerButton, 6, 2)
            layout.addWidget(efoyButton, 6, 3)

            layout.addWidget(self.errorMessage, 7, 2)

        if selectedEfoyID == "":
            efoyButton.hide()

        self.checkUnitStatus()

        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateData)
        self.timer.start(60000)

    def viewIndividualCamera(self, cameraNumber):
        global CameraNumber

        CameraNumber = cameraNumber

        self.hide()

        self.singleCamera = singleCameraView()
        self.singleCamera.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.singleCamera.frameGeometry()
        Geo.moveCenter(Center)
        self.singleCamera.move(Geo.topLeft())

    def viewAllCameras(self):

        self.hide()

        self.allCameras = allCamerasView()
        self.allCameras.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.allCameras.frameGeometry()
        Geo.moveCenter(Center)
        self.allCameras.move(Geo.topLeft())

    def checkUnitStatus(self):
        status = checkURL(selectedIP, 64430, 1)
        if status == 0:

            cameraPath = QPixmap(resourcePath("Assets/Images/OfflineCCTV.png"))

            self.errorMessage.setText("Unit Offline")
            self.errorMessage.setStyleSheet("color: red;"
                                            "font: bold 14px;")

            self.allCamerasButton.setEnabled(False)
            self.camera1Button.setEnabled(False)
            self.camera2Button.setEnabled(False)
            self.camera3Button.setEnabled(False)
            self.camera4Button.setEnabled(False)
            self.routerButton.setEnabled(False)

            self.allCameras.setPixmap(cameraPath)
            self.Camera1.setPixmap(cameraPath)
            self.Camera2.setPixmap(cameraPath)
            self.Camera3.setPixmap(cameraPath)
            self.Camera4.setPixmap(cameraPath)

        else:
            self.errorMessage.setText("Unit Online")
            self.errorMessage.setStyleSheet("color: green;"
                                            "font: bold 14px;")

    def updateData(self):
        global unitVoltage
        global unitLoad
        global unitSolar

        pullVictronData(selectedUnit)

        if unitVoltage == None or unitLoad == None or unitSolar == None:
            unitVoltage = 0.0
            unitLoad = 0.0
            unitSolar = 0.0
        else:
            unitVoltage = float(unitVoltage)
            unitLoad = int(unitLoad)
            unitSolar = int(unitSolar)

        self.batteryVoltage.setText(str(unitVoltage) + " V")
        self.loadDraw.setText(str(unitLoad) + " W")
        self.solarPower.setText(str(unitSolar) + " W")

        if unitVoltage >= 25.5:
            self.batteryPath = resourcePath("Assets/Images/fullBattery.png")
            self.batteryImage.setPixmap(QPixmap(self.batteryPath))
        elif unitVoltage >= 24 and unitVoltage < 25.5:
            self.batteryPath = resourcePath("Assets/Images/half_battery.png")
            self.batteryImage.setPixmap(QPixmap(self.batteryPath))
        elif unitVoltage < 24 and unitVoltage >= 23.6:
            self.batteryPath = resourcePath("Assets/Images/low_battery.png")
            self.batteryImage.setPixmap(QPixmap(self.batteryPath))
        elif unitVoltage < 23.6:
            self.batteryPath = resourcePath("Assets/Images/battery.png")
            self.batteryImage.setPixmap(QPixmap(self.batteryPath))

        if unitLoad <= 0:
            self.loadPath = resourcePath("Assets/Images/ChargingLoad.png")
            self.loadImage.setPixmap(QPixmap(self.loadPath))
        else:
            self.loadPath = resourcePath("Assets/Images/Load.png")
            self.loadImage.setPixmap(QPixmap(self.loadPath))

        if unitSolar >= 400:
            self.sunPath = resourcePath("Assets/Images/very_sunny.png")
            self.sunImage.setPixmap(QPixmap(self.sunPath))
        elif unitSolar >= 200 and unitSolar < 400:
            self.sunPath = resourcePath("Assets/Images/Sun.png")
            self.sunImage.setPixmap(QPixmap(self.sunPath))
        elif unitSolar >= 100 and unitSolar < 200:
            self.sunPath = resourcePath("Assets/Images/cloudy.png")
            self.sunImage.setPixmap(QPixmap(self.sunPath))
        elif unitSolar < 100:
            self.sunPath = resourcePath("Assets/Images/cloud.png")
            self.sunImage.setPixmap(QPixmap(self.sunPath))

    def openVictron(self):
        webbrowser.open(f"https://vrm.victronenergy.com/installation/{selectedVictron}/dashboard")

    def openRouter(self):
        webbrowser.open(f"https://{selectedIP}:64430/")

    def openEfoy(self):
        webbrowser.open(f"https://www.efoy-cloud.com/devices/{selectedEfoyID}")

    def closeEvent(self, event):
        if userRights == "ADMIN" or userRights == "SUPERADMIN":
            self.openMonitoring = adminMonitoring()
            self.openMonitoring.show()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openMonitoring.frameGeometry()
            Geo.moveCenter(Center)
            self.openMonitoring.move(Geo.topLeft())

            self.hide()
        elif userRights == "USER":
            self.openMonitoring = userMonitoring()
            self.openMonitoring.show()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openMonitoring.frameGeometry()
            Geo.moveCenter(Center)
            self.openMonitoring.move(Geo.topLeft())

            self.hide()

class userManagement(QWidget):
    def __init__(self):

        sunstoneIcon = resourcePath("Assets/Images/SunstoneLogo.png")

        self.listOfUsers = []

        fetchUsers = SQL.fetchUsers()

        for item in fetchUsers:
            self.listOfUsers.append(item)

        # Current Selected User
        self.selectedUser = ""
        self.selectedPassword = ""

        # New User
        self.newUsername = ""
        self.newPassword = ""
        self.newCompany = ""

        super().__init__()

        self.setWindowTitle("User Management")
        self.setGeometry(0, 0, 350, 250)
        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setWindowIconText("Logo")

        layout = QGridLayout()

        self.userSelection = QComboBox()
        self.userSelection.addItems(self.listOfUsers)
        self.userSelection.setPlaceholderText("User Selection")
        self.userSelection.currentIndexChanged.connect(self.userChanged)

        layout.addWidget(self.userSelection, 0, 0, 1, 3)

        self.usernameLabel = QLabel("")

        layout.addWidget(self.usernameLabel, 1, 0)

        self.passwordLineEdit = QLineEdit()
        self.passwordLineEdit.setPlaceholderText("Password")
        self.passwordLineEdit.textChanged.connect(self.getPasswordChanged)
        self.passwordLineEdit.hide()

        layout.addWidget(self.passwordLineEdit, 1, 1, 1, 2)

        changeButton = QPushButton("Change Details")
        changeButton.clicked.connect(self.changeUser)

        layout.addWidget(changeButton, 2, 1)

        deleteButton = QPushButton("Delete")
        deleteButton.clicked.connect(self.deleteUser)

        layout.addWidget(deleteButton, 2, 2)

        addNewUserLabel = QLabel("--------------- Add New User ---------------")
        addNewUserLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(addNewUserLabel, 3, 0, 1, 3)

        self.usernameEdit = QLineEdit()
        self.usernameEdit.setPlaceholderText("Username")
        self.usernameEdit.textChanged.connect(self.getNewUsername)

        layout.addWidget(self.usernameEdit, 4, 0)

        self.passwordAddLineEdit = QLineEdit()
        self.passwordAddLineEdit.setPlaceholderText("Password")
        self.passwordAddLineEdit.textChanged.connect(self.getNewPassword)

        layout.addWidget(self.passwordAddLineEdit, 4, 1)

        self.companyLineEdit = QLineEdit()
        self.companyLineEdit.setPlaceholderText("Company")
        self.companyLineEdit.textChanged.connect(self.getNewCompany)

        layout.addWidget(self.companyLineEdit, 4, 2)

        addUserButton = QPushButton("Add New User")
        addUserButton.clicked.connect(self.addUser)

        layout.addWidget(addUserButton, 5, 1)

        self.errorMessage = QLabel("")
        self.errorMessage.setStyleSheet("color: red")
        self.errorMessage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.errorMessage, 6, 1)

        self.setLayout(layout)

    def getPasswordChanged(self, Password):
        self.selectedPassword = Password

    def getNewUsername(self, Username):
        self.newUsername = Username

    def getNewPassword(self, Password):
        self.newPassword = Password

    def getNewCompany(self, Company):
        self.newCompany = Company

    def userChanged(self, index):

        self.selectedUser = self.listOfUsers[index]

        self.selectedPassword = SQL.fetchPassword(self.selectedUser).strip()

        self.passwordLineEdit.show()
        self.usernameLabel.show()

        self.usernameLabel.setText(self.selectedUser)
        self.passwordLineEdit.setText(self.selectedPassword)

    def changeUser(self):
        SQL.updateUser(self.selectedPassword, self.selectedUser, "USER")
        self.errorMessage.setText("User Updated")

    def deleteUser(self):

        if username == self.selectedUser:
            self.errorMessage.setText("You cannot delete your own account")
        else:
            SQL.deleteUsers(self.selectedUser)
            self.errorMessage.setText("User Deleted")

    def addUser(self):
        checkUsername = SQL.checkUsername(self.newUsername)

        if checkUsername is None:
            if not [x for x in (self.newUsername, self.newPassword, self.newCompany) if x == ""]:
                self.errorMessage.setText("User Added")
                SQL.addUsers(self.newUsername, self.newPassword, self.newCompany, "USER")
                self.usernameEdit.setText("")
                self.passwordAddLineEdit.setText("")
                self.companyLineEdit.setText("")
            else:
                self.errorMessage.setText("One or All Field Is Empty")
        else:
            self.errorMessage.setText("Username Already Exists")

    def closeEvent(self, event):
        self.openAdminMenu = adminMenu()
        self.openAdminMenu.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.openAdminMenu.frameGeometry()
        Geo.moveCenter(Center)
        self.openAdminMenu.move(Geo.topLeft())

        self.hide()

class superUserManagement(QWidget):
    def __init__(self):

        sunstoneIcon = resourcePath("Assets/Images/SunstoneLogo.png")

        self.listOfUsers = []

        fetchUsers = SQL.fetchUsers()

        for item in fetchUsers:
            self.listOfUsers.append(item)

        # Current Selected User
        self.selectedUser = ""
        self.selectedPassword = ""
        self.selectedRights = ""

        # New User
        self.newUsername = ""
        self.newPassword = ""
        self.newCompany = ""
        self.newRights = ""

        super().__init__()

        self.setWindowTitle("Super User Management")
        self.setGeometry(0, 0, 350, 250)
        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setWindowIconText("Logo")

        layout = QGridLayout()

        self.userSelection = QComboBox()
        self.userSelection.addItems(self.listOfUsers)
        self.userSelection.setPlaceholderText("User Selection")
        self.userSelection.currentIndexChanged.connect(self.userChanged)

        layout.addWidget(self.userSelection, 0, 0, 1, 3)

        self.usernameLabel = QLabel("")

        layout.addWidget(self.usernameLabel, 1, 0)

        self.passwordLineEdit = QLineEdit()

        self.passwordLineEdit.textChanged.connect(self.getPasswordChanged)
        self.passwordLineEdit.hide()

        layout.addWidget(self.passwordLineEdit, 1, 1)

        self.rightLineEdit = QLineEdit()
        self.rightLineEdit.textChanged.connect(self.getRightsChanged)
        self.rightLineEdit.hide()

        layout.addWidget(self.rightLineEdit, 1, 2)

        changeButton = QPushButton("Change Details")
        changeButton.clicked.connect(self.changeUser)

        layout.addWidget(changeButton, 2, 1)

        deleteButton = QPushButton("Delete")
        deleteButton.clicked.connect(self.deleteUser)

        layout.addWidget(deleteButton, 2, 2)

        addNewUserLabel = QLabel("--------------- Add New User ---------------")
        addNewUserLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(addNewUserLabel, 3, 0, 1, 3)

        self.usernameEdit = QLineEdit()
        self.usernameEdit.setPlaceholderText("Username")
        self.usernameEdit.textChanged.connect(self.getNewUsername)

        layout.addWidget(self.usernameEdit, 4, 0)

        self.passwordAddLineEdit = QLineEdit()
        self.passwordAddLineEdit.setPlaceholderText("Password")
        self.passwordAddLineEdit.textChanged.connect(self.getNewPassword)

        layout.addWidget(self.passwordAddLineEdit, 4, 1)

        self.companyLineEdit = QLineEdit()
        self.companyLineEdit.setPlaceholderText("Company")
        self.companyLineEdit.textChanged.connect(self.getNewCompany)

        layout.addWidget(self.companyLineEdit, 4, 2)

        self.rightsAddLineEdit = QLineEdit()
        self.rightsAddLineEdit.setPlaceholderText("Rights")
        self.rightsAddLineEdit.textChanged.connect(self.getNewRights)

        layout.addWidget(self.rightsAddLineEdit, 5, 1)

        addUserButton = QPushButton("Add New User")
        addUserButton.clicked.connect(self.addUser)

        layout.addWidget(addUserButton, 6, 1)

        self.errorMessage = QLabel("")
        self.errorMessage.setStyleSheet("color: red")
        self.errorMessage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.errorMessage, 7, 1)

        self.setLayout(layout)

    def getPasswordChanged(self, Password):
        self.selectedPassword = Password

    def getRightsChanged(self, Rights):
        self.selectedRights = Rights

    def getNewUsername(self, Username):
        self.newUsername = Username

    def getNewPassword(self, Password):
        self.newPassword = Password

    def getNewCompany(self, Company):
        self.newCompany = Company

    def getNewRights(self, Rights):
        self.newRights = Rights

    def userChanged(self, index):

        self.selectedUser = self.listOfUsers[index]

        self.selectedPassword = SQL.fetchPassword(self.selectedUser).strip()
        self.selectedRights = SQL.fetchRights(self.selectedUser).strip()

        self.usernameLabel.show()
        self.passwordLineEdit.show()
        self.rightLineEdit.show()

        self.usernameLabel.setText(self.selectedUser)
        self.passwordLineEdit.setText(self.selectedPassword)
        self.rightLineEdit.setText(self.selectedRights)

    def changeUser(self):
        SQL.updateUser(self.selectedUser, self.selectedPassword, self.selectedRights)
        self.errorMessage.setText("User Updated")

    def deleteUser(self):

        if username == self.selectedUser:
            self.errorMessage.setText("You cannot delete your own account")
        else:
            SQL.deleteUsers(self.selectedUser)
            self.errorMessage.setText("User Deleted")

    def addUser(self):
        checkUsername = SQL.checkUsername(self.newUsername)

        if checkUsername is None:
            if not [x for x in (self.newUsername, self.newPassword, self.newCompany, self.newRights) if x == ""]:
                self.errorMessage.setText("User Added")
                SQL.addUsers(self.newUsername, self.newPassword, self.newCompany, self.newRights)
                self.usernameEdit.setText("")
                self.passwordAddLineEdit.setText("")
                self.companyLineEdit.setText("")
                self.rightsAddLineEdit.setText("")
            else:
                self.errorMessage.setText("One or All Field Is Empty")
        else:
            self.errorMessage.setText("Username Already Exists")

    def closeEvent(self, event):
        self.openAdminMenu = adminMenu()
        self.openAdminMenu.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.openAdminMenu.frameGeometry()
        Geo.moveCenter(Center)
        self.openAdminMenu.move(Geo.topLeft())

        self.hide()

class unitManagement(QWidget):
    def __init__(self):

        sunstoneIcon = resourcePath("Assets/Images/SunstoneLogo.png")

        self.listOfUnits = []

        fetchUnits = SQL.fetchUnitsSunstone()
        for item in fetchUnits:
            self.listOfUnits.append(item)

        # Current Selected Unit
        self.selectedUnit = ""
        self.selectedLocation = ""
        self.selectedCompany = ""
        self.selectedCameras = ""

        # Add new Unit
        self.newUnitName = ""
        self.newCameraType = ""
        self.newIP = ""
        self.newVictronID = ""
        self.newEfoy = ""
        self.newLocation = ""
        self.NoCCTV = ""
        self.newCompany = ""
        self.newLat = ""
        self.newLon = ""
        self.newUnitType = ""

        self.w3w = ""

        super().__init__()

        self.setWindowTitle("Unit Management")
        self.setGeometry(0, 0, 650, 300)
        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setWindowIconText("Logo")

        layout = QGridLayout()

        unitManagementDropdown = QComboBox()
        unitManagementDropdown.addItems(self.listOfUnits)
        unitManagementDropdown.setPlaceholderText("Unit Management")
        unitManagementDropdown.currentIndexChanged.connect(self.unitChanged)

        layout.addWidget(unitManagementDropdown, 0, 0, 1, 4)

        self.unitName = QLabel("")

        layout.addWidget(self.unitName, 1, 0)

        self.locationEdit = QLineEdit()
        self.locationEdit.setPlaceholderText("Location")
        self.locationEdit.textChanged.connect(self.getUpdatedLocation)
        self.locationEdit.hide()

        layout.addWidget(self.locationEdit, 1, 1)

        self.companyEdit = QLineEdit()
        self.companyEdit.setPlaceholderText("Company")
        self.companyEdit.textChanged.connect(self.getUpdatedCompany)
        self.companyEdit.hide()

        layout.addWidget(self.companyEdit, 1, 2)

        self.numCameras = QLineEdit()
        self.numCameras.textChanged.connect(self.getUpdatedNumCCTV)
        self.numCameras.hide()

        layout.addWidget(self.numCameras, 1, 3)

        changeButton = QPushButton("Change Details")
        changeButton.clicked.connect(self.changeUnit)

        layout.addWidget(changeButton, 2, 0, 1, 2)

        deleteButton = QPushButton("Delete")
        deleteButton.clicked.connect(self.deleteUnit)

        layout.addWidget(deleteButton, 2, 2, 1, 2)

        addNewUnitLabel = QLabel("--------------- Add New Unit ---------------")
        addNewUnitLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(addNewUnitLabel, 3, 0, 1, 4)

        self.unitNameAdd = QLineEdit()
        self.unitNameAdd.setPlaceholderText("Unit ID")
        self.unitNameAdd.textChanged.connect(self.getNewUnitName)

        layout.addWidget(self.unitNameAdd, 4, 0)

        self.locationAdd = QLineEdit()
        self.locationAdd.setPlaceholderText("Location")
        self.locationAdd.textChanged.connect(self.getNewLocation)

        layout.addWidget(self.locationAdd, 4, 1)

        self.companyAdd = QLineEdit()
        self.companyAdd.setPlaceholderText("Company")
        self.companyAdd.textChanged.connect(self.getNewCompany)

        layout.addWidget(self.companyAdd, 4, 2)

        self.numCamerasAdd = QSpinBox()
        self.numCamerasAdd.setMinimum(1)
        self.numCamerasAdd.setMaximum(4)
        self.numCamerasAdd.textChanged.connect(self.getNewNumCCTV)

        layout.addWidget(self.numCamerasAdd, 4, 3)

        self.cameratypeAdd = QLineEdit()
        self.cameratypeAdd.setPlaceholderText("Camera Manufacturer")
        self.cameratypeAdd.textChanged.connect(self.getCameraType)

        layout.addWidget(self.cameratypeAdd, 5, 0)

        self.IPAdd = QLineEdit()
        self.IPAdd.setPlaceholderText("IP Address")
        self.IPAdd.textChanged.connect(self.getNewIP)

        layout.addWidget(self.IPAdd, 5, 1)

        unitType = QComboBox()
        unitType.setPlaceholderText("Unit Type")
        unitType.addItems(["ARC", "IO"])
        unitType.currentIndexChanged.connect(self.getNewUnitType)

        layout.addWidget(unitType, 5, 2)

        self.victronAdd = QLineEdit()
        self.victronAdd.setPlaceholderText("Victron Site ID")
        self.victronAdd.textChanged.connect(self.getNewVictronID)

        layout.addWidget(self.victronAdd, 5, 3)

        self.efoyAdd = QLineEdit()
        self.efoyAdd.setPlaceholderText("Efoy ID")
        self.efoyAdd.textChanged.connect(self.getNewEfoy)

        layout.addWidget(self.efoyAdd, 6, 0)

        self.latAdd = QLineEdit("")
        self.latAdd.setPlaceholderText("Latitude")
        self.latAdd.textChanged.connect(self.getNewLat)

        layout.addWidget(self.latAdd, 6, 1)

        self.lonAdd = QLineEdit("")
        self.lonAdd.setPlaceholderText("Longitude")
        self.lonAdd.textChanged.connect(self.getNewLon)

        layout.addWidget(self.lonAdd, 6, 2)

        addUnit = QPushButton("Add New Unit")
        addUnit.clicked.connect(self.addNewUnit)

        layout.addWidget(addUnit, 7, 0, 1, 4)

        self.w3wLineEdit = QLineEdit()
        self.w3wLineEdit.setPlaceholderText("what3words")
        self.w3wLineEdit.textChanged.connect(self.getW3W)

        layout.addWidget(self.w3wLineEdit, 8, 0, 1, 2)

        self.w3wButton = QPushButton("Convert")
        self.w3wButton.clicked.connect(self.convertW3W)

        layout.addWidget(self.w3wButton, 8, 2, 1, 2)

        self.errorMessage = QLabel("")
        self.errorMessage.setStyleSheet("color: red")
        self.errorMessage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.errorMessage, 9, 1, 1, 2)

        self.setLayout(layout)

    def getUpdatedLocation(self, Location):
        self.selectedLocation = Location

    def getUpdatedCompany(self, Company):
        self.selectedCompany = Company

    def getUpdatedNumCCTV(self, CCTV):
        self.selectedCameras = CCTV

    def getNewUnitName(self, Name):
        self.newUnitName = Name

    def getNewLocation(self, Location):
        self.newLocation = Location

    def getNewCompany(self, Company):
        self.newCompany = Company

    def getNewNumCCTV(self, Number):
        self.NoCCTV = Number

    def getCameraType(self, Type):
        self.newCameraType = Type

    def getNewIP(self, IPADDRESS):
        self.newIP = IPADDRESS

    def getNewUnitType(self, unitIndex):
        if unitIndex == 0:
            self.newUnitType = "ARC"
            self.victronAdd.show()
            self.efoyAdd.show()
        elif unitIndex == 1:
            self.newUnitType = "IO"
            self.victronAdd.hide()
            self.efoyAdd.hide()

    def getNewVictronID(self, ID):
        self.newVictronID = ID

    def getNewEfoy(self, EFOY):
        self.newEfoy = EFOY

    def getNewLat(self, Lat):
        self.newLat = Lat

    def getNewLon(self, Lon):
        self.newLon = Lon

    def getW3W(self, W3W):
        self.w3w = W3W

    def unitChanged(self, index):

        self.selectedUnit = self.listOfUnits[index]

        data = SQL.fetchUnitDetails(self.selectedUnit)

        for row in data:
            altered = list(row)
            self.selectedLocation = altered[2]
            self.selectedCompany = altered[3]
            self.selectedCameras = str(altered[4])

        self.locationEdit.show()
        self.companyEdit.show()
        self.numCameras.show()

        self.unitName.setText(self.selectedUnit)
        self.locationEdit.setText(self.selectedLocation)
        self.companyEdit.setText(self.selectedCompany)
        self.numCameras.setText(self.selectedCameras)

    def changeUnit(self):
        if int(self.selectedCameras) >= 1 and int(self.selectedCameras) <= 4:
            SQL.updateUnit(self.selectedUnit, self.selectedLocation, self.selectedCompany, self.selectedCameras)
            self.errorMessage.setText("Unit Updated")
        else:
            self.errorMessage.setText("Number of Cameras should be between 1-4")

    def deleteUnit(self):
        SQL.deleteUnits(self.selectedUnit)
        self.errorMessage.setText("Unit Deleted")

    def addNewUnit(self):
        checkUnit = SQL.checkUnit(self.newUnitName)

        if checkUnit is not None:
            self.errorMessage.setText("Unit already in database")
        elif "ARC" not in self.newUnitName and "IO" not in self.newUnitName:
            self.errorMessage.setText("Unit Name Incorrect")
        elif any(x == "" for x in (
                self.newUnitName, self.newIP, self.newLocation, self.NoCCTV, self.newCompany, self.newLat, self.newLon,
                self.newUnitType, self.newCameraType)):
            self.errorMessage.setText("One or All Field Is Empty")
        elif len(self.newIP) < 8:
            self.errorMessage.setText("IP Address too short")
        elif "." not in self.newLat or "." not in self.newLon:
            self.errorMessage.setText("Lat and Lon do not Compute")
        elif self.newCameraType.lower() not in ["axis", "hik", "hikvision", "hanwha", "wisenet", "dahua"]:
            self.errorMessage.setText("Please speak to administrator about adding new brands")
        else:
            SQL.addUnits(self.newUnitName, self.newIP, self.newVictronID, self.newLocation, self.NoCCTV,
                         self.newCompany, self.newLat, self.newLon, self.newUnitType, self.newCameraType, self.newEfoy)
            self.errorMessage.setText("Unit Added")
            self.unitNameAdd.setText("")
            self.locationAdd.setText("")
            self.companyAdd.setText("")
            self.cameratypeAdd.setText("")
            self.IPAdd.setText("")
            self.victronAdd.setText("")
            self.efoyAdd.setText("")
            self.latAdd.setText("")
            self.lonAdd.setText("")

    def convertW3W(self):

        if self.w3w == "":
            self.errorMessage.setText("Unable to Convert")
        elif len(self.w3w) < 14:
            self.errorMessage.setText("Word is too small")
        else:
            result = geocoder.convert_to_coordinates(self.w3w)

            self.newLat = str(result['coordinates']['lat'])
            self.newLon = str(result['coordinates']['lng'])

            self.latAdd.setText(self.newLat)
            self.lonAdd.setText(self.newLon)

            self.w3wLineEdit.setText("")
            self.w3w = ""

            self.errorMessage.setText("Converted")

    def closeEvent(self, event):
        self.openAdminMenu = adminMenu()
        self.openAdminMenu.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.openAdminMenu.frameGeometry()
        Geo.moveCenter(Center)
        self.openAdminMenu.move(Geo.topLeft())

        self.hide()

class superUnitManagement(QWidget):
    def __init__(self):

        sunstoneIcon = resourcePath("Assets/Images/SunstoneLogo.png")

        self.listOfUnits = []

        fetchUnits = SQL.fetchUnitsSunstone()
        for item in fetchUnits:
            self.listOfUnits.append(item)

        # Current Selected Unit
        self.selectedUnit = ""
        self.selectedLocation = ""
        self.selectedCompany = ""
        self.selectedCameras = ""
        self.selectedIP = ""
        self.selectedCameraType = ""
        self.selectedVictronID = ""
        self.selectedEfoy = ""
        self.selectedLat = ""
        self.selectedLon = ""

        # Add new Unit
        self.newUnitName = ""
        self.newCameraType = ""
        self.newIP = ""
        self.newVictronID = ""
        self.newEfoy = ""
        self.newLocation = ""
        self.NoCCTV = ""
        self.newCompany = ""
        self.newLat = ""
        self.newLon = ""
        self.newUnitType = ""

        self.w3w = ""

        super().__init__()

        self.setWindowTitle("Super Unit Management")
        self.setGeometry(0, 0, 650, 300)
        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setWindowIconText("Logo")

        layout = QGridLayout()

        unitManagementDropdown = QComboBox()
        unitManagementDropdown.addItems(self.listOfUnits)
        unitManagementDropdown.setPlaceholderText("Unit Management")
        unitManagementDropdown.currentIndexChanged.connect(self.unitChanged)

        layout.addWidget(unitManagementDropdown, 0, 0, 1, 4)

        self.unitName = QLabel("")

        layout.addWidget(self.unitName, 1, 0)

        self.locationEdit = QLineEdit()
        self.locationEdit.textChanged.connect(self.getUpdatedLocation)
        self.locationEdit.hide()

        layout.addWidget(self.locationEdit, 1, 1)

        self.companyEdit = QLineEdit()
        self.companyEdit.textChanged.connect(self.getUpdatedCompany)
        self.companyEdit.hide()

        layout.addWidget(self.companyEdit, 1, 2)

        self.numCameras = QLineEdit()
        self.numCameras.textChanged.connect(self.getUpdatedNumCCTV)
        self.numCameras.hide()

        layout.addWidget(self.numCameras, 1, 3)

        self.cameraType = QLineEdit()
        self.cameraType.textChanged.connect(self.getUpdatedType)
        self.cameraType.hide()

        layout.addWidget(self.cameraType, 2, 0)

        self.IP = QLineEdit()
        self.IP.textChanged.connect(self.getUpdatedIP)
        self.IP.hide()

        layout.addWidget(self.IP, 2, 1)

        self.Victron = QLineEdit()
        self.Victron.textChanged.connect(self.getUpdatedVictron)
        self.Victron.hide()

        layout.addWidget(self.Victron, 2, 2)

        self.Efoy = QLineEdit()
        self.Efoy.textChanged.connect(self.getUpdatedEfoy)
        self.Efoy.hide()

        layout.addWidget(self.Efoy, 2, 3)

        self.Lat = QLineEdit()
        self.Lat.textChanged.connect(self.getUpdatedLat)
        self.Lat.hide()

        layout.addWidget(self.Lat, 3, 0)

        self.Lon = QLineEdit()
        self.Lon.textChanged.connect(self.getUpdatedLon)
        self.Lon.hide()

        layout.addWidget(self.Lon, 3, 1)

        changeButton = QPushButton("Change Details")
        changeButton.clicked.connect(self.changeUnit)

        layout.addWidget(changeButton, 4, 0, 1, 2)

        deleteButton = QPushButton("Delete")
        deleteButton.clicked.connect(self.deleteUnit)

        layout.addWidget(deleteButton, 4, 2, 1, 2)

        addNewUnitLabel = QLabel("--------------- Add New Unit ---------------")
        addNewUnitLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(addNewUnitLabel, 5, 0, 1, 4)

        self.unitNameAdd = QLineEdit()
        self.unitNameAdd.setPlaceholderText("Unit ID")
        self.unitNameAdd.textChanged.connect(self.getNewUnitName)

        layout.addWidget(self.unitNameAdd, 6, 0)

        self.locationAdd = QLineEdit()
        self.locationAdd.setPlaceholderText("Location")
        self.locationAdd.textChanged.connect(self.getNewLocation)

        layout.addWidget(self.locationAdd, 6, 1)

        self.companyAdd = QLineEdit()
        self.companyAdd.setPlaceholderText("Company")
        self.companyAdd.textChanged.connect(self.getNewCompany)

        layout.addWidget(self.companyAdd, 6, 2)

        self.numCamerasAdd = QSpinBox()
        self.numCamerasAdd.setMinimum(1)
        self.numCamerasAdd.setMaximum(4)
        self.numCamerasAdd.textChanged.connect(self.getNewNumCCTV)

        layout.addWidget(self.numCamerasAdd, 6, 3)

        self.cameratypeAdd = QLineEdit()
        self.cameratypeAdd.setPlaceholderText("Camera Manufacturer")
        self.cameratypeAdd.textChanged.connect(self.getCameraType)

        layout.addWidget(self.cameratypeAdd, 7, 0)

        self.IPAdd = QLineEdit()
        self.IPAdd.setPlaceholderText("IP Address")
        self.IPAdd.textChanged.connect(self.getNewIP)

        layout.addWidget(self.IPAdd, 7, 1)

        unitType = QComboBox()
        unitType.setPlaceholderText("Unit Type")
        unitType.addItems(["ARC", "IO"])
        unitType.currentIndexChanged.connect(self.getNewUnitType)

        layout.addWidget(unitType, 7, 2)

        self.victronAdd = QLineEdit()
        self.victronAdd.setPlaceholderText("Victron Site ID")
        self.victronAdd.textChanged.connect(self.getNewVictronID)

        layout.addWidget(self.victronAdd, 7, 3)

        self.efoyAdd = QLineEdit()
        self.efoyAdd.setPlaceholderText("Efoy ID")
        self.efoyAdd.textChanged.connect(self.getNewEfoy)

        layout.addWidget(self.efoyAdd, 8, 0)

        self.latAdd = QLineEdit("")
        self.latAdd.setPlaceholderText("Latitude")
        self.latAdd.textChanged.connect(self.getNewLat)

        layout.addWidget(self.latAdd, 8, 1)

        self.lonAdd = QLineEdit("")
        self.lonAdd.setPlaceholderText("Longitude")
        self.lonAdd.textChanged.connect(self.getNewLon)

        layout.addWidget(self.lonAdd, 8, 2)

        addUnit = QPushButton("Add New Unit")
        addUnit.clicked.connect(self.addNewUnit)

        layout.addWidget(addUnit, 9, 0, 1, 4)

        self.w3wLineEdit = QLineEdit()
        self.w3wLineEdit.setPlaceholderText("what3words")
        self.w3wLineEdit.textChanged.connect(self.getW3W)

        layout.addWidget(self.w3wLineEdit, 10, 0, 1, 2)

        self.w3wButton = QPushButton("Convert")
        self.w3wButton.clicked.connect(self.convertW3W)

        layout.addWidget(self.w3wButton, 10, 2, 1, 2)

        self.errorMessage = QLabel("")
        self.errorMessage.setStyleSheet("color: red")
        self.errorMessage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.errorMessage = QLabel("")
        self.errorMessage.setStyleSheet("color: red")
        self.errorMessage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.errorMessage, 11, 1, 1, 2)

        self.setLayout(layout)

    def getUpdatedLocation(self, Location):
        self.selectedLocation = Location

    def getUpdatedCompany(self, Company):
        self.selectedCompany = Company

    def getUpdatedNumCCTV(self, CCTV):
        self.selectedCameras = CCTV

    def getUpdatedType(self, Type):
        self.selectedCameraType = Type

    def getUpdatedIP(self, IP):
        self.selectedIP = IP

    def getUpdatedVictron(self, Victron):
        self.selectedVictronID = Victron

    def getUpdatedEfoy(self, Efoy):
        self.selectedEfoy = Efoy

    def getUpdatedLat(self, Lat):
        self.selectedLat = Lat

    def getUpdatedLon(self, Lon):
        self.selectedLon = Lon

    def getNewUnitName(self, Name):
        self.newUnitName = Name

    def getNewLocation(self, Location):
        self.newLocation = Location

    def getNewCompany(self, Company):
        self.newCompany = Company

    def getNewNumCCTV(self, Number):
        self.NoCCTV = Number

    def getCameraType(self, Type):
        self.newCameraType = Type

    def getNewIP(self, IPADDRESS):
        self.newIP = IPADDRESS

    def getNewUnitType(self, unitIndex):
        if unitIndex == 0:
            self.newUnitType = "ARC"
            self.victronAdd.show()
            self.efoyAdd.show()
        elif unitIndex == 1:
            self.newUnitType = "IO"
            self.victronAdd.hide()
            self.efoyAdd.hide()

    def getNewVictronID(self, ID):
        self.newVictronID = ID

    def getNewEfoy(self, EFOY):
        self.newEfoy = EFOY

    def getNewLat(self, Lat):
        self.newLat = Lat

    def getNewLon(self, Lon):
        self.newLon = Lon

    def getW3W(self, W3W):
        self.w3w = W3W

    def unitChanged(self, index):

        self.selectedUnit = self.listOfUnits[index]

        data = SQL.fetchUnitDetails(self.selectedUnit)

        for row in data:
            altered = list(row)
            self.selectedIP = altered[0]
            self.selectedVictronID = str(altered[1])
            self.selectedLocation = altered[2]
            self.selectedCompany = altered[3]
            self.selectedCameras = str(altered[4])
            self.selectedCameraType = altered[5]
            self.selectedEfoy = altered[6]
            self.selectedLat = str(altered[7])
            self.selectedLon = str(altered[8])

        self.locationEdit.show()
        self.companyEdit.show()
        self.numCameras.show()
        self.cameraType.show()
        self.IP.show()
        self.Victron.show()
        self.Efoy.show()
        self.Lat.show()
        self.Lon.show()

        self.unitName.setText(self.selectedUnit)
        self.locationEdit.setText(self.selectedLocation)
        self.companyEdit.setText(self.selectedCompany)
        self.numCameras.setText(self.selectedCameras)
        self.cameraType.setText(self.selectedCameraType)
        self.IP.setText(self.selectedIP)
        self.Victron.setText(self.selectedVictronID)
        self.Efoy.setText(self.selectedEfoy)
        self.Lat.setText(self.selectedLat)
        self.Lon.setText(self.selectedLon)

    def changeUnit(self):
        if int(self.selectedCameras) < 1 or int(self.selectedCameras) > 4:
            self.errorMessage.setText("Number of Cameras should be between 1-4")
        elif any(x == "" for x in (
        self.selectedIP, self.selectedLocation, self.selectedCompany, self.selectedLat, self.selectedLon,
        self.selectedCameraType)):
            self.errorMessage.setText("One or More fields empty.")
        elif len(self.selectedIP) < 8:
            self.errorMessage.setText("IP Address too short")
        elif "." not in self.selectedLat or "." not in self.selectedLon:
            self.errorMessage.setText("Lat and Lon do not Compute")
        elif self.selectedCameraType.lower() not in ["axis", "hik", "hikvision", "hanwha", "wisenet", "dahua"]:
            self.errorMessage.setText("Please speak to administrator about adding new brands")
        else:
            SQL.updateUnitSuper(self.selectedUnit, self.selectedLocation, self.selectedCompany, self.selectedCameras,
                                self.selectedCameraType, self.selectedIP, self.selectedVictronID, self.selectedEfoy,
                                self.selectedLat, self.selectedLon)
            self.errorMessage.setText("Unit Updated")

    def deleteUnit(self):
        SQL.deleteUnits(self.selectedUnit)
        self.errorMessage.setText("Unit Deleted")

    def addNewUnit(self):
        checkUnit = SQL.checkUnit(self.newUnitName)

        if checkUnit is not None:
            self.errorMessage.setText("Unit already in database")
        elif "ARC" not in self.newUnitName and "IO" not in self.newUnitName:
            self.errorMessage.setText("Unit Name Incorrect")
        elif any(x == "" for x in (
                self.newUnitName, self.newIP, self.newLocation, self.NoCCTV, self.newCompany, self.newLat, self.newLon,
                self.newUnitType, self.newCameraType)):
            self.errorMessage.setText("One or All Field Is Empty")
        elif len(self.newIP) < 8:
            self.errorMessage.setText("IP Address too short")
        elif "." not in self.newLat or "." not in self.newLon:
            self.errorMessage.setText("Lat and Lon do not Compute")
        elif self.newCameraType.lower() not in ["axis", "hik", "hikvision", "hanwha", "wisenet", "dahua"]:
            self.errorMessage.setText("Please speak to administrator about adding new brands")
        else:
            SQL.addUnits(self.newUnitName, self.newIP, self.newVictronID, self.newLocation, self.NoCCTV,
                         self.newCompany, self.newLat, self.newLon, self.newUnitType, self.newCameraType, self.newEfoy)
            self.errorMessage.setText("Unit Added")
            self.unitNameAdd.setText("")
            self.locationAdd.setText("")
            self.companyAdd.setText("")
            self.cameratypeAdd.setText("")
            self.IPAdd.setText("")
            self.victronAdd.setText("")
            self.efoyAdd.setText("")
            self.latAdd.setText("")
            self.lonAdd.setText("")

    def convertW3W(self):

        if self.w3w == "":
            self.errorMessage.setText("Unable to Convert")
        elif len(self.w3w) < 14:
            self.errorMessage.setText("Word is too small")
        else:
            result = geocoder.convert_to_coordinates(self.w3w)

            self.newLat = str(result['coordinates']['lat'])
            self.newLon = str(result['coordinates']['lng'])

            self.latAdd.setText(self.newLat)
            self.lonAdd.setText(self.newLon)

            self.w3wLineEdit.setText("")
            self.w3w = ""

            self.errorMessage.setText("Converted")

    def closeEvent(self, event):
        self.openAdminMenu = adminMenu()
        self.openAdminMenu.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.openAdminMenu.frameGeometry()
        Geo.moveCenter(Center)
        self.openAdminMenu.move(Geo.topLeft())

        self.hide()

class genManagement(QWidget):
    def __init__(self):

        sunstoneIcon = resourcePath("Assets/Images/SunstoneLogo.png")

        self.listOfGen = []

        fetchGen = SQL.fetchGeneratorSunstone()
        for item in fetchGen:
            self.listOfGen.append(item)

        self.selectedUnit = ""
        self.selectedLocation = ""
        self.selectedCompany = ""

        self.newGenName = ""
        self.newLocation = ""
        self.newCompany = ""
        self.newVictronID = ""
        self.newEfoy1 = ""
        self.newEfoy2 = ""
        self.newLat = ""
        self.newLon = ""

        super().__init__()

        self.setWindowTitle("Generator Management")
        self.setGeometry(0, 0, 650, 300)
        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setWindowIconText("Logo")

        layout = QGridLayout()

        genManagementDropdown = QComboBox()
        genManagementDropdown.addItems(self.listOfGen)
        genManagementDropdown.setPlaceholderText("Generator Management")

        layout.addWidget(genManagementDropdown, 0, 0, 1, 4)

        self.genName = QLabel("")
        layout.addWidget(self.genName, 1, 0, 1, 2)

        self.locationEdit = QLineEdit()
        self.locationEdit.textChanged.connect(self.getUpdatedLocation)
        self.locationEdit.hide()

        layout.addWidget(self.locationEdit, 1, 2)

        self.companyEdit = QLineEdit()
        self.companyEdit.textChanged.connect(self.getUpdatedCompany)
        self.companyEdit.hide()

        layout.addWidget(self.companyEdit, 1, 3)

        changeButton = QPushButton("Change Details")
        changeButton.clicked.connect(self.changeUnit)

        layout.addWidget(changeButton, 2, 0, 1, 2)

        deleteButton = QPushButton("Delete")
        deleteButton.clicked.connect(self.deleteUnit)

        layout.addWidget(deleteButton, 2, 2, 1, 2)

        addNewUnitLabel = QLabel("--------------- Add New Generator ---------------")
        addNewUnitLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(addNewUnitLabel, 3, 0, 1, 4)

        self.genNameAdd = QLineEdit()
        self.genNameAdd.setPlaceholderText("Unit ID")
        self.genNameAdd.textChanged.connect(self.genNameAdd)

        layout.addWidget(self.genNameAdd, 4, 0)

        self.locationAdd = QLineEdit()
        self.locationAdd.setPlaceholderText("Location")
        self.locationAdd.textChanged.connect(self.getNewLocation)

        layout.addWidget(self.locationAdd, 4, 1)

        self.companyAdd = QLineEdit()
        self.companyAdd.setPlaceholderText("Company")
        self.companyAdd.textChanged.connect(self.getNewCompany)

        layout.addWidget(self.companyAdd, 4, 2)

        self.victronAdd = QLineEdit()
        self.victronAdd.setPlaceholderText("Victron Site ID")
        self.victronAdd.textChanged.connect(self.getNewVictronID)

        layout.addWidget(self.victronAdd, 4, 3)

        self.efoy1Add = QLineEdit()
        self.efoy1Add.setPlaceholderText("Efoy ID")
        self.efoy1Add.textChanged.connect(self.getNewEfoy)

        layout.addWidget(self.efoy1Add, 5, 0)

        self.efoy2Add = QLineEdit()
        self.efoy2Add.setPlaceholderText("Efoy ID")
        self.efoy2Add.textChanged.connect(self.getNewEfoy)

        layout.addWidget(self.efoy2Add, 5, 1)

        self.latAdd = QLineEdit("")
        self.latAdd.setPlaceholderText("Latitude")
        self.latAdd.textChanged.connect(self.getNewLat)

        layout.addWidget(self.latAdd, 5, 2)

        self.lonAdd = QLineEdit("")
        self.lonAdd.setPlaceholderText("Longitude")
        self.lonAdd.textChanged.connect(self.getNewLon)

        layout.addWidget(self.lonAdd, 5, 3)

        addUnit = QPushButton("Add New Generator")
        addUnit.clicked.connect(self.addNewGen)

        layout.addWidget(addUnit, 6, 0, 1, 4)

        self.errorMessage = QLabel("")
        self.errorMessage.setStyleSheet("color: red")
        self.errorMessage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.errorMessage, 7, 1, 1, 2)

        self.setLayout(layout)

    def getUpdatedLocation(self, Location):
        self.selectedLocation = Location

    def getUpdatedCompany(self, Company):
        self.selectedCompany = Company
    def getNewGenName(self, Name):
        self.newGenName = Name

    def getNewLocation(self, Location):
        self.newLocation = Location

    def getNewCompany(self, Company):
        self.newCompany = Company

    def getNewVictronID(self, ID):
        self.newVictronID = ID

    def getNewEfoy1(self, Efoy):
        self.newEfoy1 = Efoy

    def getNewEfoy2(self, Efoy):
        self.newEfoy2 = Efoy

    def getNewLat(self, Lat):
        self.newLat = Lat

    def getNewLon(self, Lon):
        self.newLon = Lon

    def unitChanged(self, index):

        self.selectedGen = self.listOfGen[index]

        data = SQL.fetchGenDetails(self.selectedGen)

        for row in data:
            altered = list(row)
            self.selectedVictronID = str(altered[0])
            self.selectedLocation = altered[1]
            self.selectedCompany = altered[2]

        self.locationEdit.show()
        self.companyEdit.show()

        self.genName.setText(self.selectedGen)
        self.locationEdit.setText(self.selectedLocation)
        self.companyEdit.setText(self.selectedCompany)

    def addNewGen(self):
        checkGen = SQL.checkGen(self.newGenName)

        if checkGen is not None:
            self.errorMessage.setText("Unit already in database")
        elif any(x == "" for x in (self.newGenName, self.newVictronID, self.newEfoy1)):
            self.errorMessage.setText("One or All Field Is Empty")
        elif "." not in self.newLat or "." not in self.newLon:
            self.errorMessage.setText("Lat and Lon do not Compute")
        else:
            SQL.addGenerator(self.newGenName,self.newVictronID,self.newLocation,self.newCompany,self.newLat,self.newLon,self.newEfoy1,self.newEfoy2)
            self.errorMessage.setText("Generator Added")
            self.unitNameAdd.setText("")
            self.locationAdd.setText("")
            self.companyAdd.setText("")
            self.victronAdd.setText("")
            self.efoy1Add.setText("")
            self.efoy2Add.setText("")
            self.latAdd.setText("")
            self.lonAdd.setText("")


    def closeEvent(self, event):
        self.openAdminMenu = adminMenu()
        self.openAdminMenu.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.openAdminMenu.frameGeometry()
        Geo.moveCenter(Center)
        self.openAdminMenu.move(Geo.topLeft())

        self.hide()

class superGenManagement(QWidget):
    def __init__(self):

        sunstoneIcon = resourcePath("Assets/Images/SunstoneLogo.png")

        self.listOfGen = []

        fetchGen = SQL.fetchGeneratorSunstone()
        for item in fetchGen:
            self.listOfGen.append(item)

        self.selectedGen = ""
        self.selectedLocation = ""
        self.selectedCompany = ""
        self.selectedVictronID = ""
        self.selectedEfoy1 = ""
        self.selectedEfoy2 = ""
        self.selectedLat = ""
        self.selectedLon = ""

        self.newGenName = ""
        self.newLocation = ""
        self.newCompany = ""
        self.newVictronID = ""
        self.newEfoy1 = ""
        self.newEfoy2 = ""
        self.newLat = ""
        self.newLon = ""

        super().__init__()

        self.setWindowTitle("Super Generator Management")
        self.setGeometry(0, 0, 650, 300)
        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setWindowIconText("Logo")

        layout = QGridLayout()

        genManagementDropdown = QComboBox()
        genManagementDropdown.addItems(self.listOfGen)
        genManagementDropdown.setPlaceholderText("Generator Management")


        layout.addWidget(genManagementDropdown,0,0,1,4)

        self.genName = QLabel("")
        layout.addWidget(self.genName, 1, 0)

        self.locationEdit = QLineEdit()
        self.locationEdit.textChanged.connect(self.getUpdatedLocation)
        self.locationEdit.hide()

        layout.addWidget(self.locationEdit, 1, 1)

        self.companyEdit = QLineEdit()
        self.companyEdit.textChanged.connect(self.getUpdatedCompany)
        self.companyEdit.hide()

        layout.addWidget(self.companyEdit, 1, 2)

        self.Victron = QLineEdit()
        self.Victron.textChanged.connect(self.getUpdatedVictron)
        self.Victron.hide()

        layout.addWidget(self.Victron, 1, 3)

        self.Efoy1 = QLineEdit()
        self.Efoy1.textChanged.connect(self.getUpdatedEfoy1)
        self.Efoy1.hide()

        layout.addWidget(self.Efoy1, 2, 0)

        self.Efoy2 = QLineEdit()
        self.Efoy2.textChanged.connect(self.getUpdatedEfoy2)
        self.Efoy2.hide()

        layout.addWidget(self.Efoy2, 2, 1)

        self.Lat = QLineEdit()
        self.Lat.textChanged.connect(self.getUpdatedLat)
        self.Lat.hide()

        layout.addWidget(self.Lat, 2, 2)

        self.Lon = QLineEdit()
        self.Lon.textChanged.connect(self.getUpdatedLon)
        self.Lon.hide()

        layout.addWidget(self.Lon, 2, 3)

        changeButton = QPushButton("Change Details")
        changeButton.clicked.connect(self.changeUnit)

        layout.addWidget(changeButton, 3, 0, 1, 2)

        deleteButton = QPushButton("Delete")
        deleteButton.clicked.connect(self.deleteUnit)

        layout.addWidget(deleteButton, 3, 2, 1, 2)

        addNewUnitLabel = QLabel("--------------- Add New Generator ---------------")
        addNewUnitLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(addNewUnitLabel, 4, 0, 1, 4)

        self.genNameAdd = QLineEdit()
        self.genNameAdd.setPlaceholderText("Unit ID")
        self.genNameAdd.textChanged.connect(self.getNewGenName)

        layout.addWidget(self.genNameAdd, 5, 0)

        self.locationAdd = QLineEdit()
        self.locationAdd.setPlaceholderText("Location")
        self.locationAdd.textChanged.connect(self.getNewLocation)

        layout.addWidget(self.locationAdd, 5, 1)

        self.companyAdd = QLineEdit()
        self.companyAdd.setPlaceholderText("Company")
        self.companyAdd.textChanged.connect(self.getNewCompany)

        layout.addWidget(self.companyAdd, 5, 2)

        self.victronAdd = QLineEdit()
        self.victronAdd.setPlaceholderText("Victron Site ID")
        self.victronAdd.textChanged.connect(self.getNewVictronID)

        layout.addWidget(self.victronAdd, 5, 3)

        self.efoy1Add = QLineEdit()
        self.efoy1Add.setPlaceholderText("Efoy 1 ID")
        self.efoy1Add.textChanged.connect(self.getNewEfoy1)

        layout.addWidget(self.efoy1Add, 6, 0)

        self.efoy2Add = QLineEdit()
        self.efoy2Add.setPlaceholderText("Efoy 2 ID (Can be Null)")
        self.efoy2Add.textChanged.connect(self.getNewEfoy2)

        layout.addWidget(self.efoy2Add, 6, 1)

        self.latAdd = QLineEdit("")
        self.latAdd.setPlaceholderText("Latitude")
        self.latAdd.textChanged.connect(self.getNewLat)

        layout.addWidget(self.latAdd, 6, 2)

        self.lonAdd = QLineEdit("")
        self.lonAdd.setPlaceholderText("Longitude")
        self.lonAdd.textChanged.connect(self.getNewLon)

        layout.addWidget(self.lonAdd, 6, 3)

        addUnit = QPushButton("Add New Generator")
        addUnit.clicked.connect(self.addNewGen)

        layout.addWidget(addUnit, 7, 0, 1, 4)

        self.errorMessage = QLabel("")
        self.errorMessage.setStyleSheet("color: red")
        self.errorMessage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.errorMessage, 8, 1, 1, 2)

        self.setLayout(layout)

    def getUpdatedLocation(self, Location):
        self.selectedLocation = Location

    def getUpdatedCompany(self, Company):
        self.selectedCompany = Company

    def getUpdatedVictron(self, Victron):
        self.selectedVictronID = Victron

    def getUpdatedEfoy1(self, Efoy):
        self.selectedEfoy1 = Efoy

    def getUpdatedEfoy2(self, Efoy):
        self.selectedEfoy2 = Efoy

    def getUpdatedLat(self, Lat):
        self.selectedLat = Lat

    def getUpdatedLon(self, Lon):
        self.selectedLon = Lon

    def getNewGenName(self, Name):
        self.newGenName = Name

    def getNewLocation(self, Location):
        self.newLocation = Location

    def getNewCompany(self, Company):
        self.newCompany = Company

    def getNewVictronID(self, ID):
        self.newVictronID = ID

    def getNewEfoy1(self, Efoy):
        self.newEfoy1 = Efoy

    def getNewEfoy2(self, Efoy):
        self.newEfoy2 = Efoy

    def getNewLat(self, Lat):
        self.newLat = Lat

    def getNewLon(self, Lon):
        self.newLon = Lon


    def unitChanged(self, index):

        self.selectedGen = self.listOfGen[index]

        data = SQL.fetchGenDetails(self.selectedGen)

        for row in data:
            altered = list(row)
            self.selectedVictronID = str(altered[0])
            self.selectedLocation = altered[1]
            self.selectedCompany = altered[2]
            self.selectedEfoy1 = altered[3]
            self.selectedEfoy2 = altered[3]
            self.selectedLat = str(altered[5])
            self.selectedLon = str(altered[1])

        self.locationEdit.show()
        self.companyEdit.show()
        self.Victron.show()
        self.Efoy1.show()
        self.Efoy2.show()
        self.Lat.show()
        self.Lon.show()

        self.genName.setText(self.selectedGen)
        self.locationEdit.setText(self.selectedLocation)
        self.companyEdit.setText(self.selectedCompany)
        self.Victron.setText(self.selectedVictronID)
        self.Efoy1.setText(self.selectedEfoy)
        self.Efoy2.setText(self.selectedEfoy)
        self.Lat.setText(self.selectedLat)
        self.Lon.setText(self.selectedLon)


    def addNewGen(self):
        checkGen = SQL.checkGen(self.newGenName)

        if checkGen is not None:
            self.errorMessage.setText("Unit already in database")
        elif any(x == "" for x in (self.newGenName, self.newVictronID, self.newEfoy1)):
            self.errorMessage.setText("One or All Field Is Empty")
        elif "." not in self.newLat or "." not in self.newLon:
            self.errorMessage.setText("Lat and Lon do not Compute")
        else:
            SQL.addGenerator(self.newGenName,self.newVictronID,self.newLocation,self.newCompany,self.newLat,self.newLon,self.newEfoy1,self.newEfoy2)
            self.errorMessage.setText("Generator Added")
            self.genNameAdd.setText("")
            self.locationAdd.setText("")
            self.companyAdd.setText("")
            self.victronAdd.setText("")
            self.efoy1Add.setText("")
            self.efoy2Add.setText("")
            self.latAdd.setText("")
            self.lonAdd.setText("")

    def closeEvent(self, event):
        self.openAdminMenu = adminMenu()
        self.openAdminMenu.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.openAdminMenu.frameGeometry()
        Geo.moveCenter(Center)
        self.openAdminMenu.move(Geo.topLeft())

        self.hide()

class adminMenu(QWidget):
    def __init__(self):
        sunstoneIcon = resourcePath("Assets/Images/SunstoneLogo.png")

        super().__init__()

        self.setWindowTitle("Admin Menu")
        self.setGeometry(0, 0, 430, 180)
        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setWindowIconText("Logo")

        layout = QVBoxLayout()

        userManagementButton = QPushButton("User Management")
        userManagementButton.clicked.connect(self.openUser)

        layout.addWidget(userManagementButton)

        unitManagementButton = QPushButton("Unit Management")
        unitManagementButton.clicked.connect(self.openUnit)

        layout.addWidget(unitManagementButton)

        genManagementButton = QPushButton("Generator Management")
        genManagementButton.clicked.connect(self.openGen)

        layout.addWidget(genManagementButton)

        self.setLayout(layout)

    def openUser(self):
        if userRights == "ADMIN":
            self.openUserManagement = userManagement()
            self.openUserManagement.show()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openUserManagement.frameGeometry()
            Geo.moveCenter(Center)
            self.openUserManagement.move(Geo.topLeft())

            self.hide()
        elif userRights == "SUPERADMIN":
            self.openUserManagement = superUserManagement()
            self.openUserManagement.show()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openUserManagement.frameGeometry()
            Geo.moveCenter(Center)
            self.openUserManagement.move(Geo.topLeft())

            self.hide()

    def openUnit(self):
        if userRights == "ADMIN":

            self.openUnitManagement = unitManagement()
            self.openUnitManagement.show()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openUnitManagement.frameGeometry()
            Geo.moveCenter(Center)
            self.openUnitManagement.move(Geo.topLeft())

            self.hide()
        elif userRights == "SUPERADMIN":

            self.openUnitManagement = superUnitManagement()
            self.openUnitManagement.show()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openUnitManagement.frameGeometry()
            Geo.moveCenter(Center)
            self.openUnitManagement.move(Geo.topLeft())

            self.hide()

    def openGen(self):
        if userRights == "ADMIN":

            self.openGenManagement = genManagement()
            self.openGenManagement.show()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openGenManagement.frameGeometry()
            Geo.moveCenter(Center)
            self.openGenManagement.move(Geo.topLeft())

            self.hide()
        elif userRights == "SUPERADMIN":

            self.openGenManagement = superGenManagement()
            self.openGenManagement.show()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openGenManagement.frameGeometry()
            Geo.moveCenter(Center)
            self.openGenManagement.move(Geo.topLeft())

            self.hide()

    def closeEvent(self, event):

        self.openMonitoring = adminMonitoring()
        self.openMonitoring.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.openMonitoring.frameGeometry()
        Geo.moveCenter(Center)
        self.openMonitoring.move(Geo.topLeft())

        self.hide()

class interactiveMap(QWidget):
    def __init__(self):
        sunstoneIcon = resourcePath("Assets/Images/SunstoneLogo.png")

        super().__init__()

        self.setWindowTitle("Interactive Unit Map")
        self.setGeometry(0, 0, 700, 700)
        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setWindowIconText("Logo")

        layout = QGridLayout()

        self.mapBrowser = QtWebEngineWidgets.QWebEngineView(self)
        layout.addWidget(self.mapBrowser, 0, 0)

        self.importMap()

        self.setLayout(layout)

    def importMap(self):
        names = []

        lat = []

        lon = []

        if userCompany == "Sunstone":
            data = SQL.fetchLocationsSunstone()
        else:
            data = SQL.fetchLocations(userCompany)

        for row in data:
            altered = list(row)
            names.append(altered[0])
            lat.append(altered[1])
            lon.append(altered[2])

        config = {'displayModeBar': False}

        fig = go.Figure(go.Scattermapbox(
            lat=lat,
            lon=lon,
            mode='markers',
            marker=go.scattermapbox.Marker(size=10),
            text=names,
        ))

        fig.update_layout(
            autosize=True,
            hovermode='closest',
            mapbox=dict(
                accesstoken=mapboxAccessToken,
                bearing=0,
                center=dict(
                    lat=54.628,
                    lon=-2.150,
                ),
                pitch=0,
                zoom=4.4,
            ),
        )

        fig.update_traces()

        self.mapBrowser.setHtml(fig.to_html(include_plotlyjs='cdn', config=config))

class victronOverview(QWidget):
    def __init__(self):
        global unitVoltage
        global unitLoad
        global unitSolar

        sunstoneIcon = resourcePath("Assets/Images/SunstoneLogo.png")

        self.Filters = ["Name", "Voltage", "Solar", "Load"]
        self.listOfUnits = []
        self.listOfLocations = []
        self.listOfVoltage = []
        self.listOfSolar = []
        self.listOfLoad = []

        if userCompany == "Sunstone":
            fetchVictron = SQL.fetchVictronAllDataSunstone()

            for row in fetchVictron:
                altered = list(row)
                self.listOfUnits.append(altered[0])
                self.listOfVoltage.append(altered[1])
                self.listOfSolar.append(altered[2])
                self.listOfLoad.append(altered[3])

        else:
            fetchVictron = SQL.fetchVictronAllData(userCompany)

            for row in fetchVictron:
                altered = list(row)
                self.listOfUnits.append(altered[0])
                self.listOfVoltage.append(altered[1])
                self.listOfSolar.append(altered[2])
                self.listOfLoad.append(altered[3])

        super().__init__()

        self.setWindowTitle("Victron Data Overview")
        self.setGeometry(0, 0, 700, 700)

        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setWindowIconText("Logo")

        layout = QVBoxLayout()

        self.unitsLayout = QGridLayout()

        groupBox = QGroupBox()

        self.filterDropdown = QComboBox()
        self.filterDropdown.addItems(self.Filters)
        self.filterDropdown.currentIndexChanged.connect(self.filterChanged)

        layout.addWidget(self.filterDropdown)

        self.Header1 = QLabel("Unit Name")
        self.Header1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.Header2 = QLabel("Voltage")
        self.Header2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.Header3 = QLabel("Solar")
        self.Header3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.Header4 = QLabel("Load")
        self.Header4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.Header1.setStyleSheet("font-weight: bold;"
                                   "border-radius: 8px;"
                                   "color: white;"
                                   "border: 1px solid #46a15b;"
                                   "background-color: #358446;"
                                   "padding: 5px 15px;"
                                   "font-size: 14pt;")
        self.Header2.setStyleSheet("font-weight: bold;"
                                   "border-radius: 8px;"
                                   "color: white;"
                                   "border: 1px solid #46a15b;"
                                   "background-color: #358446;"
                                   "padding: 5px 15px;"
                                   "font-size: 14pt;")
        self.Header3.setStyleSheet("font-weight: bold;"
                                   "border-radius: 8px;"
                                   "color: white;"
                                   "border: 1px solid #46a15b;"
                                   "background-color: #358446;"
                                   "padding: 5px 15px;"
                                   "font-size: 14pt;")
        self.Header4.setStyleSheet("font-weight: bold;"
                                   "border-radius: 8px;"
                                   "color: white;"
                                   "border: 1px solid #46a15b;"
                                   "background-color: #358446;"
                                   "padding: 5px 15px;"
                                   "font-size: 14pt;")

        self.unitsLayout.addWidget(self.Header1, 0, 0)
        self.unitsLayout.addWidget(self.Header2, 0, 1)
        self.unitsLayout.addWidget(self.Header3, 0, 2)
        self.unitsLayout.addWidget(self.Header4, 0, 3)

        j = 0
        for i in self.listOfUnits:
            self.unitName = QLabel(f"{i}")
            self.unitName.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.unitName.setStyleSheet("border-radius: 8px;"
                                   "color: black;"
                                   "border: 1px solid #46a15b;"
                                   "background-color: #c8eacf;"
                                   "padding: 5px 15px;"
                                   "font-size: 14pt;")

            self.unitsLayout.addWidget(self.unitName, j+1, 0)

            unitVoltage = self.listOfVoltage[j]
            unitLoad = self.listOfLoad[j]
            unitSolar = self.listOfSolar[j]

            self.batteryVoltage = QLabel(str(unitVoltage) + " V")
            self.batteryVoltage.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.batteryVoltage.setStyleSheet("border-radius: 8px;"
                                   "color: black;"
                                   "border: 1px solid #46a15b;"
                                   "background-color: #c8eacf;"
                                   "padding: 5px 15px;"
                                   "font-size: 14pt;")

            self.unitsLayout.addWidget(self.batteryVoltage, j+1, 1)

            self.solarPower = QLabel(str(unitSolar) + " W")
            self.solarPower.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.solarPower.setStyleSheet("border-radius: 8px;"
                                   "color: black;"
                                   "border: 1px solid #46a15b;"
                                   "background-color: #c8eacf;"
                                   "padding: 5px 15px;"
                                   "font-size: 14pt;")

            self.unitsLayout.addWidget(self.solarPower, j+1, 2)

            self.loadDraw = QLabel(str(unitLoad) + " W")
            self.loadDraw.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.loadDraw.setStyleSheet("border-radius: 8px;"
                                   "color: black;"
                                   "border: 1px solid #46a15b;"
                                   "background-color: #c8eacf;"
                                   "padding: 5px 15px;"
                                   "font-size: 14pt;")

            self.unitsLayout.addWidget(self.loadDraw, j+1, 3)

            j = j + 1

        groupBox.setLayout(self.unitsLayout)

        scrollArea = QScrollArea()
        scrollArea.setWidget(groupBox)
        scrollArea.setWidgetResizable(True)

        layout.addWidget(scrollArea)

        self.setLayout(layout)

    def filterChanged(self, index):

        selectedFilter = self.Filters[index]

        for i in reversed(range(self.unitsLayout.count())):
            widgetToRemove = self.unitsLayout.itemAt(i).widget()
            self.unitsLayout.removeWidget(widgetToRemove)
            widgetToRemove.deleteLater()

        self.Header1 = QLabel("Unit Name")
        self.Header1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.Header2 = QLabel("Voltage")
        self.Header2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.Header3 = QLabel("Solar")
        self.Header3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.Header4 = QLabel("Load")
        self.Header4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.Header1.setStyleSheet("font-weight: bold;"
                                   "border-radius: 8px;"
                                   "color: white;"
                                   "border: 1px solid #46a15b;"
                                   "background-color: #358446;"
                                   "padding: 5px 15px;"
                                   "font-size: 14pt;")
        self.Header2.setStyleSheet("font-weight: bold;"
                                   "border-radius: 8px;"
                                   "color: white;"
                                   "border: 1px solid #46a15b;"
                                   "background-color: #358446;"
                                   "padding: 5px 15px;"
                                   "font-size: 14pt;")
        self.Header3.setStyleSheet("font-weight: bold;"
                                   "border-radius: 8px;"
                                   "color: white;"
                                   "border: 1px solid #46a15b;"
                                   "background-color: #358446;"
                                   "padding: 5px 15px;"
                                   "font-size: 14pt;")
        self.Header4.setStyleSheet("font-weight: bold;"
                                   "border-radius: 8px;"
                                   "color: white;"
                                   "border: 1px solid #46a15b;"
                                   "background-color: #358446;"
                                   "padding: 5px 15px;"
                                   "font-size: 14pt;")

        self.unitsLayout.addWidget(self.Header1, 0, 0)
        self.unitsLayout.addWidget(self.Header2, 0, 1)
        self.unitsLayout.addWidget(self.Header3, 0, 2)
        self.unitsLayout.addWidget(self.Header4, 0, 3)

        self.listOfUnits = []
        self.listOfLocations = []
        self.listOfVoltage = []
        self.listOfSolar = []
        self.listOfLoad = []

        if userCompany == "Sunstone":
            if selectedFilter == "Name":
                fetchVictron = SQL.fetchVictronAllDataSunstone()
            else:
                fetchVictron = SQL.fetchFilteredVictronSunstone(selectedFilter)

            for row in fetchVictron:
                altered = list(row)
                self.listOfUnits.append(altered[0])
                self.listOfVoltage.append(altered[1])
                self.listOfSolar.append(altered[2])
                self.listOfLoad.append(altered[3])

        else:
            if selectedFilter == "Name":
                fetchVictron = SQL.fetchVictronAllData(userCompany)
            else:
                fetchVictron = SQL.fetchFilteredVictron(userCompany, selectedFilter)

            for row in fetchVictron:
                altered = list(row)
                self.listOfUnits.append(altered[0])
                self.listOfVoltage.append(altered[1])
                self.listOfSolar.append(altered[2])
                self.listOfLoad.append(altered[3])

        j = 0
        for i in self.listOfUnits:
            self.unitName = QLabel(f"{i}")
            self.unitName.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.unitName.setStyleSheet("border-radius: 8px;"
                                        "color: black;"
                                        "border: 1px solid #46a15b;"
                                        "background-color: #c8eacf;"
                                        "padding: 5px 15px;"
                                        "font-size: 14pt;")

            self.unitsLayout.addWidget(self.unitName, j + 1, 0)

            unitVoltage = self.listOfVoltage[j]
            unitLoad = self.listOfLoad[j]
            unitSolar = self.listOfSolar[j]

            self.batteryVoltage = QLabel(str(unitVoltage) + " V")
            self.batteryVoltage.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.batteryVoltage.setStyleSheet("border-radius: 8px;"
                                              "color: black;"
                                              "border: 1px solid #46a15b;"
                                              "background-color: #c8eacf;"
                                              "padding: 5px 15px;"
                                              "font-size: 14pt;")

            self.unitsLayout.addWidget(self.batteryVoltage, j + 1, 1)

            self.solarPower = QLabel(str(unitSolar) + " W")
            self.solarPower.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.solarPower.setStyleSheet("border-radius: 8px;"
                                          "color: black;"
                                          "border: 1px solid #46a15b;"
                                          "background-color: #c8eacf;"
                                          "padding: 5px 15px;"
                                          "font-size: 14pt;")

            self.unitsLayout.addWidget(self.solarPower, j + 1, 2)

            self.loadDraw = QLabel(str(unitLoad) + " W")
            self.loadDraw.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.loadDraw.setStyleSheet("border-radius: 8px;"
                                        "color: black;"
                                        "border: 1px solid #46a15b;"
                                        "background-color: #c8eacf;"
                                        "padding: 5px 15px;"
                                        "font-size: 14pt;")

            self.unitsLayout.addWidget(self.loadDraw, j + 1, 3)

            j = j + 1

class adminMonitoring(QWidget):
    def __init__(self):

        sunstoneIcon = resourcePath("Assets/Images/SunstoneLogo.png")

        self.listOfUnits = []
        self.listOfLocations = []

        fetchUnits = SQL.fetchUnitsSunstone()

        for item in fetchUnits:
            self.listOfUnits.append(item)

        if userCompany == "Sunstone":
            fetchSites = SQL.fetchSitesSunstone()

            for i in fetchSites:
                self.listOfLocations.append(i)

        else:
            fetchSites = SQL.fetchSites(userCompany)

            for i in fetchSites:
                self.listOfLocations.append(i)
                print(self.listOfLocations)

        super().__init__()

        self.setWindowTitle("Admin Dashboard")
        self.setGeometry(0, 0, 255, 600)
        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setWindowIconText("Logo")

        mainLayout = QVBoxLayout()

        unitsLayout = QVBoxLayout()

        groupBox = QGroupBox()

        j = 0

        for i in self.listOfUnits:

            self.testButton = QPushButton(str(f"{i} {self.listOfLocations[j]}"))

            buttonText = (self.testButton.text()).split()

            buttonText = buttonText[0]

            self.testButton.clicked.connect(lambda checked=None, text=buttonText: self.openUnitDashboard(text))

            unitsLayout.addWidget(self.testButton)

            j = j + 1

        groupBox.setLayout(unitsLayout)

        scrollArea = QScrollArea()
        scrollArea.setWidget(groupBox)
        scrollArea.setWidgetResizable(True)

        mainLayout.addWidget(scrollArea)

        mapButton = QPushButton("Interactive Map")
        mapButton.clicked.connect(self.openMap)

        mainLayout.addWidget(mapButton)

        victronButton = QPushButton("Victron Overview")
        victronButton.clicked.connect(self.openVictron)

        mainLayout.addWidget(victronButton)

        adminButton = QPushButton("Admin Menu")
        adminButton.clicked.connect(self.openAdmin)

        mainLayout.addWidget(adminButton)

        self.setLayout(mainLayout)

    def openUnitDashboard(self, unitName):
        global selectedUnit
        global selectedUnitType
        global selectedIP
        global selectedVictron
        global selectedCCTV
        global selectedEfoyID
        global selectedCamera
        global selectedCompany

        unitType = SQL.fetchUnitType(unitName).strip()
        data = SQL.fetchUnitDetails(unitName)
        selectedUnit = unitName
        selectedUnitType = unitType

        for row in data:
            altered = list(row)
            selectedIP = altered[0]
            selectedVictron = altered[1]
            selectedCompany = altered[3]
            selectedCCTV = altered[4]
            selectedCamera = altered[5]
            selectedEfoyID = altered[6]

        if str(unitType) == "ARC":
            pullVictronData(selectedUnit)

            self.openARCDashboard = arcDashboard()
            self.openARCDashboard.show()

            self.hide()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openARCDashboard.frameGeometry()
            Geo.moveCenter(Center)
            self.openARCDashboard.move(Geo.topLeft())

        elif str(unitType) == "IO":
            self.openIODashboard = ioDashboard()
            self.openIODashboard.show()

            self.hide()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openIODashboard.frameGeometry()
            Geo.moveCenter(Center)
            self.openIODashboard.move(Geo.topLeft())

    def openMap(self):
        self.openMapPage = interactiveMap()
        self.openMapPage.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.openMapPage.frameGeometry()
        Geo.moveCenter(Center)
        self.openMapPage.move(Geo.topLeft())

    def openVictron(self):
        self.openVictronPage = victronOverview()
        self.openVictronPage.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.openVictronPage.frameGeometry()
        Geo.moveCenter(Center)
        self.openVictronPage.move(Geo.topLeft())

    def openAdmin(self):
        self.openAdminMenu = adminMenu()
        self.openAdminMenu.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.openAdminMenu.frameGeometry()
        Geo.moveCenter(Center)
        self.openAdminMenu.move(Geo.topLeft())

        self.hide()

    def closeEvent(self, event):
        self.login = loginUI()
        self.login.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.login.frameGeometry()
        Geo.moveCenter(Center)
        self.login.move(Geo.topLeft())

        self.openMapPage = interactiveMap()
        self.openMapPage.hide()

        self.hide()

class userMonitoring(QWidget):
    def __init__(self):

        sunstoneIcon = resourcePath("Assets/Images/SunstoneLogo.png")

        self.listOfUnits = []
        self.listOfLocations = []

        if userCompany == "Sunstone":
            fetchUnits = SQL.fetchUnitsSunstone()
        else:
            fetchUnits = SQL.fetchUnits(userCompany)

        for item in fetchUnits:
            self.listOfUnits.append(item)

        if userCompany == "Sunstone":
            fetchSites = SQL.fetchSitesSunstone()

            for i in fetchSites:
                self.listOfLocations.append(i)

        else:
            fetchSites = SQL.fetchSites(userCompany)

            for i in fetchSites:
                self.listOfLocations.append(i)

        super().__init__()

        self.setWindowTitle("User Dashboard")
        self.setGeometry(0, 0, 255, 600)
        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setWindowIconText("Logo")

        mainLayout = QVBoxLayout()

        unitsLayout = QVBoxLayout()

        groupBox = QGroupBox()

        j = 0

        for i in self.listOfUnits:

            self.testButton = QPushButton(str(f"{i} {self.listOfLocations[j]}"))

            buttonText = (self.testButton.text()).split()

            buttonText = buttonText[0]

            self.testButton.clicked.connect(lambda checked=None, text=buttonText: self.openUnitDashboard(text))

            unitsLayout.addWidget(self.testButton)

            j = j + 1

        groupBox.setLayout(unitsLayout)

        scrollArea = QScrollArea()
        scrollArea.setWidget(groupBox)
        scrollArea.setWidgetResizable(True)

        mainLayout.addWidget(scrollArea)

        mapButton = QPushButton("Interactive Map")
        mapButton.clicked.connect(self.openMap)

        mainLayout.addWidget(mapButton)

        victronButton = QPushButton("Victron Overview")
        victronButton.clicked.connect(self.openVictron)

        mainLayout.addWidget(victronButton)

        self.setLayout(mainLayout)

    def openUnitDashboard(self, unitName):
        global selectedUnit
        global selectedUnitType
        global selectedIP
        global selectedVictron
        global selectedCompany
        global selectedCCTV
        global selectedEfoyID
        global selectedCamera

        unitType = SQL.fetchUnitType(unitName).strip()
        data = SQL.fetchUnitDetails(unitName)
        selectedUnit = unitName
        selectedUnitType = unitType

        for row in data:
            altered = list(row)
            selectedIP = altered[0]
            selectedVictron = altered[1]
            selectedCompany = altered[3]
            selectedCCTV = altered[4]
            selectedCamera = altered[5]
            selectedEfoyID = altered[6]

        if str(unitType) == "ARC":
            pullVictronData(selectedUnit)

            self.openARCDashboard = arcDashboard()
            self.openARCDashboard.show()

            self.hide()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openARCDashboard.frameGeometry()
            Geo.moveCenter(Center)
            self.openARCDashboard.move(Geo.topLeft())

        elif str(unitType) == "IO":
            self.openIODashboard = ioDashboard()
            self.openIODashboard.show()

            self.hide()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openIODashboard.frameGeometry()
            Geo.moveCenter(Center)
            self.openIODashboard.move(Geo.topLeft())

    def openMap(self):
        self.openMapPage = interactiveMap()
        self.openMapPage.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.openMapPage.frameGeometry()
        Geo.moveCenter(Center)
        self.openMapPage.move(Geo.topLeft())

    def openVictron(self):
        self.openVictronPage = victronOverview()
        self.openVictronPage.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.openVictronPage.frameGeometry()
        Geo.moveCenter(Center)
        self.openVictronPage.move(Geo.topLeft())

    def closeEvent(self, event):
        self.login = loginUI()
        self.login.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.login.frameGeometry()
        Geo.moveCenter(Center)
        self.login.move(Geo.topLeft())

        self.openMapPage = interactiveMap()
        self.openMapPage.hide()

        self.hide()

class loginUI(QMainWindow):
    def __init__(self):

        sunstoneIcon = resourcePath("Assets/Images/SunstoneLogo.png")
        logoPath = resourcePath("Assets/Images/sunstone.png")

        self.username = ""
        self.password = ""
        self.rights = ""

        super().__init__()

        self.setWindowTitle("Dashboard Login")
        self.setGeometry(0, 0, 380, 320)
        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setWindowIconText("Logo")

        layout = QGridLayout()

        self.Logo = QLabel()
        pixmap = QPixmap(logoPath)
        self.Logo.setPixmap(pixmap)
        self.Logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.Logo, 0, 0)

        usernameEntry = QLineEdit()
        usernameEntry.setPlaceholderText("Username")
        usernameEntry.textChanged.connect(self.getUser)

        layout.addWidget(usernameEntry, 4, 0)

        passwordEntry = QLineEdit()
        passwordEntry.setPlaceholderText("Password")
        passwordEntry.textChanged.connect(self.getPassword)
        passwordEntry.returnPressed.connect(self.openMonitoring)
        passwordEntry.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addWidget(passwordEntry, 5, 0)

        loginButton = QPushButton("Login")
        loginButton.clicked.connect(self.openMonitoring)
        layout.addWidget(loginButton, 6, 0)

        self.errorMessage = QLabel("WRONG USERNAME OR PASSWORD")
        self.errorMessage.setStyleSheet("color: red")
        self.errorMessage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.errorMessage, 7, 0)

        self.errorMessage.hide()

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def getUser(self, Username):
        global username
        username = Username
        self.username = Username
        self.errorMessage.hide()

    def getPassword(self, Password):
        global password
        self.password = Password
        self.errorMessage.hide()

    def openMonitoring(self):

        global userRights
        global userCompany

        checkUsername = SQL.checkUsername(self.username)

        if checkUsername is None:
            self.errorMessage.show()

        else:
            checkPassword = SQL.fetchPassword(self.username)

            loggedIn = self.password == checkPassword.strip()

            if loggedIn:
                userRights = SQL.fetchRights(self.username)
                userCompany = SQL.fetchCompany(self.username)
                if "ADMIN" == userRights or "SUPERADMIN" == userRights:
                    self.adminMonitoring = adminMonitoring()
                    self.adminMonitoring.show()

                    Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
                    Geo = self.adminMonitoring.frameGeometry()
                    Geo.moveCenter(Center)
                    self.adminMonitoring.move(Geo.topLeft())

                    self.hide()
                elif "USER" == userRights:
                    self.userMonitoring = userMonitoring()
                    self.userMonitoring.show()

                    Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
                    Geo = self.userMonitoring.frameGeometry()
                    Geo.moveCenter(Center)
                    self.userMonitoring.move(Geo.topLeft())

                    self.hide()
            else:
                self.errorMessage.show()

class errorMessage(QMainWindow):

    def __init__(self):
        sunstoneIcon = resourcePath("Assets/Images/SunstoneLogo.png")

        super().__init__()

        self.setWindowTitle("Connection Error")
        self.setGeometry(0, 0, 300, 300)

        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setWindowIconText("Logo")

        layout = QVBoxLayout()

        errorLabel = QLabel("You are not connected to the Internet")
        errorLabel.setStyleSheet("color: red;"
                                 "font: bold 14px;")
        errorLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(errorLabel)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

app = QApplication([])

if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

app.setStyleSheet("""

    QLineEdit {
        border-radius: 10px;
        border: 1px solid #e0e4e7;
        background-color: #c8eacf;
        color: #0e2515;
        padding: 5px 15px; 
    }
    QComboBox {
        border: 1px solid #000000;
        padding: 5px 15px;
    }
    QPushButton {
        border-radius: 8px;
        color: white;
        border: 1px solid #46a15b;
        background-color: #358446;
        padding: 5px 15px; 

    }
    QPushButton:hover {
        background-color: #358446;
        border: 1px solid #2d683a;
    }
    QSpinBox {
        border: 1px solid #e0e4e7;
        background-color: #c8eacf;
        color: #0e2515;
        padding: 5px 15px; 

    }

""")

app.setStyle('Fusion')

socketOpen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socketOpen.settimeout(2)

try:
    socketOpen.connect(("google.com", 80))

except:
    window = errorMessage()

    window.show()

else:
    window = loginUI()
    window.show()
    socketOpen.close()

center = QScreen.availableGeometry(QApplication.primaryScreen()).center()

geo = window.frameGeometry()
geo.moveCenter(center)
window.move(geo.topLeft())

sys.exit(app.exec())