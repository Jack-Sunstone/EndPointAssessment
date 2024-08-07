# importing all used libaries
import sys
import os
import webbrowser
import cv2
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtWebEngineWidgets
import SQL
from threading import *
import socket
import plotly.graph_objects as go
from collections import deque
import time
import what3words
import requests
from datetime import datetime
import Relays

# These will be used to store the data from SQL of the open unit dashboard
selectedUnit = ""
selectedIP = ""
selectedVictron = ""
selectedCompany = ""
selectedCCTV = ""
selectedUnitType = ""
selectedCamera = ""
selectedEfoyID = ""
selectedEfoyID2 = ""
selectedTextDevice = ""
selectedUnitSize = ""

# Storing the logged in users details
userRights = ""
userCompany = ""

# If the unit has no victron data then the 0 will be displayed
unitSolar = 0
unitVoltage = 0
unitLoad = 0

# Stores the user name of the logged in user
username = ""

# Default camera 1 when viewing
CameraNumber = 1

# Passwords for cameras
sunstonePassword = "(10GIN$t0n3)"
wjPassword = "12Sunstone34"

# Token for the interactive map
mapboxAccessToken = "pk.eyJ1IjoiamFja2dhbmRlcmNvbXB0b24iLCJhIjoiY2x1bW16MmVzMTViajJqbjI0N3RuOGhhOCJ9.Kl6jwZjBEtGoM1C_5NyLJg"

# Token to login to W3W API
geocoder = what3words.Geocoder("RMNUBSDA")

baseSheet = """
            QLineEdit {
                    border-radius: 10px;
                    border: 1px solid #e0e4e7;
                    background-color: #c8eacf;
                    color: white;
                    padding: 5px 15px; 
                }
            QWidget {
                background-color: #358446;
            }
            QComboBox {
                background-color: #358446;
                border: 1px solid white;
                color: #FFFFFF;
                padding: 5px 15px;
                combobox-popup: 0;
            }
            QPushButton {
                border-radius: 8px;
                color: white;
                border: 1px solid white;
                background-color: #358446;
                padding: 5px 15px; 

            }
            QPushButton:hover {
                background-color: #358446;
                border: 1px solid #2d683a;
            }
            QSpinBox {
                border: 1px solid #e0e4e7;
                color: white;
                padding: 5px 15px; 
            }
            QLabel {
                font: bold;
                color: white;
            }

            QRadioButton {
                font: bold;
                color: white;
            }


        """

graidentSheet = """
                    QWidget {
                        background-color: qlineargradient(x1: 0, x2: 1, stop: 0 #358446, stop: 1 #6FFF63);
                    }
                    QComboBox {
                        background-color: #358446;
                        border: 1px solid #46a15b;;
                        color: #FFFFFF;
                        padding: 5px 15px;
                        combobox-popup: 0;
                    }
                    QPushButton {
                        border-radius: 8px;
                        color: white;
                        border: 1px solid #46a15b;
                        background-color: #358446;
                        padding: 5px 15px; 
                        margin: 5px;
                    }
                    QPushButton:hover {
                        background-color: #358446;
                        border: 1px solid #2d683a;
                    }

                """


def binToDec(n):

    return int(n,2)

# This function gets the data stored in the SQL database and stores it within the program in the variables above
def pullVictronData(unitName):
    global unitSolar
    global unitVoltage
    global unitLoad

    data = SQL.fetchVictronData(unitName)  # Calling Function in the SQL document using the selected units name

    # Storing data
    for row in data:
        altered = list(row)
        unitSolar = altered[0]
        unitVoltage = altered[1]
        unitLoad = altered[2]


# Returns the RTSP link for viewing specific Axis Cameras
def axisPath(IPaddress, cameraNumber):
    Axis = f"rtsp://root:12Sunstone34@{IPaddress}:{cameraNumber}554/axis-media/media.amp"

    return Axis


# Returns the RTSP link for viewing specific Hikvision Cameras
def hikPath(IPaddress, cameraNumber):
    Hik = f"rtsp://admin:(10GIN$t0n3)@{IPaddress}:{cameraNumber}554/Streaming/Channels/102/?transportmode=unicast"

    return Hik


# Returns the RTSP link for viewing specific Hanwha Cameras
def hanwhaPath(IPaddress, cameraNumber):
    Hanwha = f"rtsp://admin:12Sunstone34@{IPaddress}:{cameraNumber}554/profile2/media.smp"

    return Hanwha


# Returns the RTSP link for viewing specific Dahua Cameras
def dahuaPath(IPaddress, cameraNumber):
    Dahua = f"rtsp://admin:12Sunstone34@{IPaddress}:{cameraNumber}554/live"

    return Dahua


# Returns the absolute path of any document called within the program i.e Images
def resourcePath(relativePath):
    try:
        basePath = sys._MEIPASS
    except Exception:
        basePath = os.path.abspath(".")

    return os.path.join(basePath, relativePath)


# Checking whether a unit is online or not and returning True or False
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
        self.loop = 1
        self.stream = 1
        super(CameraWidget, self).__init__()

        self.Deque = deque(maxlen=1)

        self.screenWidth = Width
        self.screenHeight = Height

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
            else:
                self.videoFrame.setText("Camera Offline")
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

        while self.loop == 1:
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

            #Convert to pixmap and set to video frame
            self.Image = QImage(self.Frame, self.Frame.shape[1], self.Frame.shape[0], QImage.Format_RGB888).rgbSwapped()
            self.Pixmap = QPixmap.fromImage(self.Image)
            self.videoFrame.setPixmap(self.Pixmap)
    def getVideoFrame(self):
        return self.videoFrame

    def closeEvent(self, a0):
        self.loop = 0
        self.close()
        self.Timer.stop()


class allCamerasView(QWidget):
    def __init__(self):

        cameraIcon = resourcePath("Assets/Images/CCTV.png")  # importing camera Icon

        super().__init__()

        self.setWindowTitle("View All Cameras")
        self.setGeometry(0, 0, 1310, 800)
        self.setFixedSize(1310, 800)
        self.setWindowIcon(QIcon(cameraIcon))
        self.setWindowIconText("Camera")

        layout = QGridLayout()

        if selectedUnitType == "ARC":

            batteryVoltage = QLabel(f"Battery Voltage: {unitVoltage}V")
            Solar = QLabel(f"Solar: {unitSolar}W")

            layout.addWidget(batteryVoltage, 0, 0, 1, 1)
            layout.addWidget(Solar, 0, 1, 1, 1)

            batteryVoltage.setAttribute(Qt.WA_TranslucentBackground)
            Solar.setAttribute(Qt.WA_TranslucentBackground)

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

            self.cameraOne.setAttribute(Qt.WA_TranslucentBackground)
            self.cameraTwo.setAttribute(Qt.WA_TranslucentBackground)
            self.cameraThree.setAttribute(Qt.WA_TranslucentBackground)
            self.cameraFour.setAttribute(Qt.WA_TranslucentBackground)

            layout.addWidget(self.cameraOne.getVideoFrame(), 1, 0, 1, 1)
            layout.addWidget(self.cameraTwo.getVideoFrame(), 1, 1, 1, 1)
            layout.addWidget(self.cameraThree.getVideoFrame(), 2, 0, 1, 1)
            layout.addWidget(self.cameraFour.getVideoFrame(), 2, 1, 1, 1)

        elif selectedCCTV == 3:
            self.cameraOne = CameraWidget(640, 360, cameraOneLink)
            self.cameraTwo = CameraWidget(640, 360, cameraTwoLink)
            self.cameraThree = CameraWidget(640, 360, cameraThreeLink)

            self.cameraOne.setAttribute(Qt.WA_TranslucentBackground)
            self.cameraTwo.setAttribute(Qt.WA_TranslucentBackground)
            self.cameraThree.setAttribute(Qt.WA_TranslucentBackground)

            layout.addWidget(self.cameraOne.getVideoFrame(), 1, 0, 1, 1)
            layout.addWidget(self.cameraTwo.getVideoFrame(), 1, 1, 1, 1)
            layout.addWidget(self.cameraThree.getVideoFrame(), 2, 0, 1, 1)

        elif selectedCCTV == 2:
            self.cameraOne = CameraWidget(640, 360, cameraOneLink)
            self.cameraTwo = CameraWidget(640, 360, cameraTwoLink)

            self.cameraOne.setAttribute(Qt.WA_TranslucentBackground)
            self.cameraTwo.setAttribute(Qt.WA_TranslucentBackground)

            layout.addWidget(self.cameraOne.getVideoFrame(), 1, 0, 1, 1)
            layout.addWidget(self.cameraTwo.getVideoFrame(), 1, 1, 1, 1)

        self.setLayout(layout)
        self.setStyleSheet(baseSheet)

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

            self.close()
        elif str(selectedUnitType) == "IO":
            self.openIODashboard = ioDashboard()
            self.openIODashboard.show()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openIODashboard.frameGeometry()
            Geo.moveCenter(Center)
            self.openIODashboard.move(Geo.topLeft())

            self.close()

class singleCameraView(QWidget):
    def __init__(self):

        cameraIcon = resourcePath("Assets/Images/CCTV.png")  # importing camera Icon

        super().__init__()

        self.setWindowTitle(f"Camera {CameraNumber}")
        self.setGeometry(0, 0, 1310, 800)
        self.setFixedSize(1310, 800)
        self.setWindowIcon(QIcon(cameraIcon))
        self.setWindowIconText("Camera")

        layout = QGridLayout()

        if selectedUnitType == "ARC":
            batteryVoltage = QLabel(f"Battery Voltage: {unitVoltage}V")
            Solar = QLabel(f"Solar: {unitSolar}W")

            layout.addWidget(batteryVoltage, 0, 0, 1, 1)
            layout.addWidget(Solar, 0, 1, 1, 1)

            batteryVoltage.setAttribute(Qt.WA_TranslucentBackground)
            Solar.setAttribute(Qt.WA_TranslucentBackground)

        if selectedCamera.lower() == "axis":

            cameraOneLink = axisPath(selectedIP, CameraNumber)

        elif selectedCamera.lower() == "hik" or selectedCamera.lower() == "hikvision":

            cameraOneLink = hikPath(selectedIP, CameraNumber)

        elif selectedCamera.lower() == "hanwha" or selectedCamera.lower() == "wisenet":

            cameraOneLink = hanwhaPath(selectedIP, CameraNumber)

        elif selectedCamera.lower() == "dahua":

            cameraOneLink = dahuaPath(selectedIP, CameraNumber)

        self.cameraOne = CameraWidget(1280, 720, cameraOneLink)

        layout.addWidget(self.cameraOne.getVideoFrame(), 1, 0, 1, 2)

        self.cameraOne.setAttribute(Qt.WA_TranslucentBackground)

        self.setLayout(layout)

        self.setStyleSheet(baseSheet)

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


class relays(QWidget):
    def __init__(self):
        sunstoneIcon = resourcePath("Assets/Images/SunstoneLogo.png")
        response = requests.get(f"http://81.179.155.109:78/{selectedUnit}/lastSeen.php")
        lastSeen = response.text

        datalst = lastSeen.split()

        datetimeFormat = datetime(int(datalst[6]), int(datalst[5]), int(datalst[4]), int(datalst[7]), int(datalst[8]),
                                  int(datalst[9]))

        datetimeNow = datetime.now()

        difference = datetimeNow - datetimeFormat

        differenceSeconds = difference.total_seconds()
        differenceMinutes = divmod(differenceSeconds, 60)[0]

        self.Relay1 = ""
        self.Relay2 = ""
        self.Relay3 = ""
        self.Relay4 = ""

        data = SQL.fetchRelayState(selectedUnit)

        for row in data:
            altered = list(row)
            self.Relay1 = altered[0]
            self.Relay2 = altered[1]
            self.Relay3 = altered[2]
            self.Relay4 = altered[3]

        intList = [self.Relay4, self.Relay3, self.Relay2, self.Relay1]

        strList = [str(i) for i in intList]

        Binary = "".join(strList)

        Decimal = binToDec(Binary)

        relayImage = resourcePath(f"Assets/Images/TextDevice/{Decimal}.png")

        super().__init__()

        self.setWindowTitle(selectedUnit)
        self.setGeometry(0, 0, 760, 200)
        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setStyleSheet(baseSheet)

        layout = QGridLayout()

        self.lastSeenLabel = QLabel(lastSeen)
        self.lastSeenLabel.setStyleSheet("font: bold 14px;"
                                    "color: white;")
        self.lastSeenLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.lastSeenLabel, 0, 1, 1, 2)

        self.relayImage = QLabel()
        self.relayImage.setPixmap(QPixmap(relayImage))
        self.relayImage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.relayImage.setAttribute(Qt.WA_TranslucentBackground)

        layout.addWidget(self.relayImage, 1,0,1,4)

        self.relay1Button = QPushButton("Relay 1")
        self.relay1Button.clicked.connect(self.Relay1Clicked)

        self.relay1Label = QLabel()
        self.relay1Label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if self.Relay1 == 0:
            self.relay1Label.setText("Relay OFF")
            self.relay1Label.setStyleSheet("color: red")
            self.relay1Button.setStyleSheet("QPushButton { border: 2px solid red;"
                                            "background: red; }"
                                            "QPushButton:hover { border: 2px solid #1eff00; }")
        else:
            self.relay1Label.setText("Relay ON")
            self.relay1Label.setStyleSheet("color: #1eff00")
            self.relay1Button.setStyleSheet("QPushButton { border: 2px solid #1eff00;"
                                            "background: #1eff00; }"
                                            "QPushButton:hover { border: 2px solid red; }")

        layout.addWidget(self.relay1Label, 2, 0)
        layout.addWidget(self.relay1Button, 3, 0)

        self.relay2Button = QPushButton("Relay 2")
        self.relay2Button.clicked.connect(self.Relay2Clicked)

        self.relay2Label = QLabel()
        self.relay2Label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if self.Relay2 == 0:
            self.relay2Label.setText("Relay OFF")
            self.relay2Label.setStyleSheet("color: red")
            self.relay2Button.setStyleSheet("QPushButton { border: 2px solid red;"
                                            "background: red; }"
                                            "QPushButton:hover { border: 2px solid #1eff00; }")
        else:
            self.relay2Label.setText("Relay ON")
            self.relay2Label.setStyleSheet("color: #1eff00")
            self.relay2Button.setStyleSheet("QPushButton { border: 2px solid #1eff00;"
                                            "background: #1eff00; }"
                                            "QPushButton:hover { border: 2px solid red; }")

        layout.addWidget(self.relay2Label, 2, 1)
        layout.addWidget(self.relay2Button, 3, 1)

        self.relay3Button = QPushButton("Relay 3")
        self.relay3Button.clicked.connect(self.Relay3Clicked)

        self.relay3Label = QLabel()
        self.relay3Label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if self.Relay3 == 0:
            self.relay3Label.setText("Relay OFF")
            self.relay3Label.setStyleSheet("color: red")
            self.relay3Button.setStyleSheet("QPushButton { border: 2px solid red;"
                                            "background: red; }"
                                            "QPushButton:hover { border: 2px solid #1eff00; }")
        else:
            self.relay3Label.setText("Relay ON")
            self.relay3Label.setStyleSheet("color: #1eff00")
            self.relay3Button.setStyleSheet("QPushButton { border: 2px solid #1eff00;"
                                            "background: #1eff00; }"
                                            "QPushButton:hover { border: 2px solid red; }")

        layout.addWidget(self.relay3Label, 2, 2)
        layout.addWidget(self.relay3Button, 3, 2)

        self.relay4Button = QPushButton("Relay 4")
        self.relay4Button.clicked.connect(self.Relay4Clicked)

        self.relay4Label = QLabel()
        self.relay4Label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if self.Relay4 == 0:
            self.relay4Label.setText("Relay OFF")
            self.relay4Label.setStyleSheet("color: red")
            self.relay4Button.setStyleSheet("QPushButton { border: 2px solid red;"
                                            "background: red; }"
                                            "QPushButton:hover { border: 2px solid #1eff00; }")
        else:
            self.relay4Label.setText("Relay ON")
            self.relay4Label.setStyleSheet("color: #1eff00")
            self.relay4Button.setStyleSheet("QPushButton { border: 2px solid #1eff00;"
                                            "background: #1eff00; }"
                                            "QPushButton:hover { border: 2px solid red; }")

        layout.addWidget(self.relay4Label, 2, 3)
        layout.addWidget(self.relay4Button, 3, 3)

        warningMessage = QLabel(
            "Disclaimer: Please allow 60 Seconds for Text Device to update when changing Relay State.")
        warningMessage.setStyleSheet("color: white;")
        warningMessage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(warningMessage, 4, 0, 1, 4)

        if differenceMinutes > 6:
            self.relay1Button.setEnabled(False)
            self.relay2Button.setEnabled(False)
            self.relay3Button.setEnabled(False)
            self.relay4Button.setEnabled(False)

            self.relay1Button.setStyleSheet("background-color: red;")
            self.relay2Button.setStyleSheet("background-color: red;")
            self.relay3Button.setStyleSheet("background-color: red;")
            self.relay4Button.setStyleSheet("background-color: red;")
            self.lastSeenLabel.setStyleSheet("font: bold 14px;"
                                        "color: red;")

        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.relayCheck)
        self.timer.start(2000)

    def relayCheck(self):

        response = requests.get(f"http://81.179.155.109:78/{selectedUnit}/lastSeen.php")
        lastSeen = response.text

        datalst = lastSeen.split()

        datetimeFormat = datetime(int(datalst[6]), int(datalst[5]), int(datalst[4]), int(datalst[7]), int(datalst[8]),
                                  int(datalst[9]))

        datetimeNow = datetime.now()

        difference = datetimeNow - datetimeFormat

        differenceSeconds = difference.total_seconds()
        differenceMinutes = divmod(differenceSeconds, 60)[0]

        self.lastSeenLabel.setText(lastSeen)

        data = SQL.fetchRelayState(selectedUnit)

        for row in data:
            altered = list(row)
            self.Relay1 = altered[0]
            self.Relay2 = altered[1]
            self.Relay3 = altered[2]
            self.Relay4 = altered[3]

        intList = [self.Relay4, self.Relay3, self.Relay2, self.Relay1]

        strList = [str(i) for i in intList]

        Binary = "".join(strList)

        Decimal = binToDec(Binary)

        relayImage = resourcePath(f"Assets/Images/TextDevice/{Decimal}.png")

        self.relayImage.setPixmap(QPixmap(relayImage))


        if self.Relay1 == 0:
            self.relay1Label.setText("Relay OFF")
            self.relay1Label.setStyleSheet("color: red")
            self.relay1Button.setStyleSheet("QPushButton { border: 2px solid red;"
                                            "background: red; }"
                                            "QPushButton:hover { border: 2px solid #1eff00; }")
        else:
            self.relay1Label.setText("Relay ON")
            self.relay1Label.setStyleSheet("color: #1eff00")
            self.relay1Button.setStyleSheet("QPushButton { border: 2px solid #1eff00;"
                                            "background: #1eff00; }"
                                            "QPushButton:hover { border: 2px solid red; }")

        if self.Relay2 == 0:
            self.relay2Label.setText("Relay OFF")
            self.relay2Label.setStyleSheet("color: red")
            self.relay2Button.setStyleSheet("QPushButton { border: 2px solid red;"
                                            "background: red; }"
                                            "QPushButton:hover { border: 2px solid #1eff00; }")
        else:
            self.relay2Label.setText("Relay ON")
            self.relay2Label.setStyleSheet("color: #1eff00")
            self.relay2Button.setStyleSheet("QPushButton { border: 2px solid #1eff00;"
                                            "background: #1eff00; }"
                                            "QPushButton:hover { border: 2px solid red; }")

        if self.Relay3 == 0:
            self.relay3Label.setText("Relay OFF")
            self.relay3Label.setStyleSheet("color: red")
            self.relay3Button.setStyleSheet("QPushButton { border: 2px solid red;"
                                            "background: red; }"
                                            "QPushButton:hover { border: 2px solid #1eff00; }")
        else:
            self.relay3Label.setText("Relay ON")
            self.relay3Label.setStyleSheet("color: #1eff00")
            self.relay3Button.setStyleSheet("QPushButton { border: 2px solid #1eff00;"
                                            "background: #1eff00; }"
                                            "QPushButton:hover { border: 2px solid red; }")

        if self.Relay4 == 0:
            self.relay4Label.setText("Relay OFF")
            self.relay4Label.setStyleSheet("color: red")
            self.relay4Button.setStyleSheet("QPushButton { border: 2px solid red;"
                                            "background: red; }"
                                            "QPushButton:hover { border: 2px solid #1eff00; }")
        else:
            self.relay4Label.setText("Relay ON")
            self.relay4Label.setStyleSheet("color: #1eff00")
            self.relay4Button.setStyleSheet("QPushButton { border: 2px solid #1eff00;"
                                            "background: #1eff00; }"
                                            "QPushButton:hover { border: 2px solid red; }")

        if differenceMinutes > 6:
            self.relay1Button.setEnabled(False)
            self.relay2Button.setEnabled(False)
            self.relay3Button.setEnabled(False)
            self.relay4Button.setEnabled(False)

            self.relay1Button.setStyleSheet("background-color: red;")
            self.relay2Button.setStyleSheet("background-color: red;")
            self.relay3Button.setStyleSheet("background-color: red;")
            self.relay4Button.setStyleSheet("background-color: red;")
            self.lastSeenLabel.setStyleSheet("font: bold 14px;"
                                        "color: red;")
        else:
            self.relay1Button.setEnabled(True)
            self.relay2Button.setEnabled(True)
            self.relay3Button.setEnabled(True)
            self.relay4Button.setEnabled(True)
            self.lastSeenLabel.setStyleSheet("font: bold 14px;"
                                             "color: white;")
    def setRelayImage(self):

        intList = [self.Relay4, self.Relay3, self.Relay2, self.Relay1]

        strList = [str(i) for i in intList]

        Binary = "".join(strList)

        Decimal = binToDec(Binary)

        relayImage = resourcePath(f"Assets/Images/TextDevice/{Decimal}.png")

        self.relayImage.setPixmap(QPixmap(relayImage))

    def Relay1Clicked(self):
        Relays.Relay1(selectedUnit)
        if self.Relay1 == 0:
            SQL.setRelayState(selectedUnit, "Relay1", 1)
            self.Relay1 = 1
            self.relay1Label.setText("Relay ON")
            self.relay1Label.setStyleSheet("color: #1eff00")
            self.relay1Button.setStyleSheet("QPushButton { border: 2px solid #1eff00;"
                                            "background: #1eff00; }"
                                            "QPushButton:hover { border: 2px solid red; }")

        elif self.Relay1 == 1:
            SQL.setRelayState(selectedUnit, "Relay1", 0)
            self.Relay1 = 0
            self.relay1Label.setText("Relay OFF")
            self.relay1Label.setStyleSheet("color: red")
            self.relay1Button.setStyleSheet("QPushButton { border: 2px solid red;"
                                            "background: red; }"
                                            "QPushButton:hover { border: 2px solid #1eff00; }")

        self.setRelayImage()


    def Relay2Clicked(self):
        Relays.Relay2(selectedUnit)
        if self.Relay2 == 0:
            SQL.setRelayState(selectedUnit, "Relay2", 1)
            self.Relay2 = 1

            self.relay2Label.setText("Relay ON")
            self.relay2Label.setStyleSheet("color: #1eff00")
            self.relay2Button.setStyleSheet("QPushButton { border: 2px solid #1eff00;"
                                            "background: #1eff00; }"
                                            "QPushButton:hover { border: 2px solid red; }")

        elif self.Relay2 == 1:
            SQL.setRelayState(selectedUnit, "Relay2", 0)
            self.Relay2 = 0
            self.relay2Label.setText("Relay OFF")
            self.relay2Label.setStyleSheet("color: red")
            self.relay2Button.setStyleSheet("QPushButton { border: 2px solid red;"
                                            "background: red; }"
                                            "QPushButton:hover { border: 2px solid #1eff00; }")

        self.setRelayImage()

    def Relay3Clicked(self):
        Relays.Relay3(selectedUnit)
        if self.Relay3 == 0:
            SQL.setRelayState(selectedUnit, "Relay3", 1)
            self.Relay3 = 1
            self.relay3Label.setText("Relay ON")
            self.relay3Label.setStyleSheet("color: #1eff00")
            self.relay3Button.setStyleSheet("QPushButton { border: 2px solid #1eff00;"
                                            "background: #1eff00; }"
                                            "QPushButton:hover { border: 2px solid red; }")

        elif self.Relay3 == 1:
            SQL.setRelayState(selectedUnit, "Relay3", 0)
            self.Relay3 = 0
            self.relay3Label.setText("Relay OFF")
            self.relay3Label.setStyleSheet("color: red")
            self.relay3Button.setStyleSheet("QPushButton { border: 2px solid red;"
                                            "background: red; }"
                                            "QPushButton:hover { border: 2px solid #1eff00; }")

        self.setRelayImage()

    def Relay4Clicked(self):
        Relays.Relay4(selectedUnit)
        if self.Relay4 == 0:
            SQL.setRelayState(selectedUnit, "Relay4", 1)
            self.Relay4 = 1
            self.relay4Label.setText("Relay ON")
            self.relay4Label.setStyleSheet("color: #1eff00")
            self.relay4Button.setStyleSheet("QPushButton { border: 2px solid #1eff00;"
                                            "background: #1eff00; }"
                                            "QPushButton:hover { border: 2px solid red; }")

        elif self.Relay4 == 1:
            SQL.setRelayState(selectedUnit, "Relay4", 0)
            self.Relay4 = 0
            self.relay4Label.setText("Relay OFF")
            self.relay4Label.setStyleSheet("color: red")
            self.relay4Button.setStyleSheet("QPushButton { border: 2px solid red;"
                                            "background: red; }"
                                            "QPushButton:hover { border: 2px solid #1eff00; }")

        self.setRelayImage()

    def closeEvent(self, a0):
        self.timer.stop()
        self.close()

class ioDashboard(QWidget):
    def __init__(self):

        ioBoxIcon = resourcePath("Assets/Images/IOBox.png")
        cameraPath = resourcePath("Assets/Images/CCTV.png")
        ioBox = resourcePath("Assets/Images/IOBoxLeft.png")

        super().__init__()

        self.setWindowTitle(selectedUnit)
        self.setGeometry(0, 0, 760, 200)
        self.setWindowIcon(QIcon(ioBoxIcon))
        self.setWindowIconText("IO Box")
        self.setWindowFlags(Qt.FramelessWindowHint)

        layout = QGridLayout()

        unitLabel = QLabel(selectedIP)
        unitLabel.setStyleSheet("font: bold 14px;"
                                "color: white;")
        unitLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        unitLabel.setAttribute(Qt.WA_TranslucentBackground)

        pixmap = QPixmap(cameraPath)
        ioBoxPixmap = QPixmap(ioBox)

        self.allCameras = QLabel()
        self.allCameras.setPixmap(pixmap)
        self.allCameras.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.allCameras.setAttribute(Qt.WA_TranslucentBackground)

        self.allCamerasButton = QPushButton("All Cameras")
        self.allCamerasButton.clicked.connect(self.viewAllCameras)

        self.Camera1 = QLabel()
        self.Camera1.setPixmap(pixmap)
        self.Camera1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.Camera1.setAttribute(Qt.WA_TranslucentBackground)

        self.camera1Button = QPushButton("Camera 1")
        self.camera1Button.clicked.connect(lambda checked=None, text=1: self.viewIndividualCamera(text))

        self.Camera2 = QLabel()
        self.Camera2.setPixmap(pixmap)
        self.Camera2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.Camera2.setAttribute(Qt.WA_TranslucentBackground)

        self.camera2Button = QPushButton("Camera 2")
        self.camera2Button.clicked.connect(lambda checked=None, text=2: self.viewIndividualCamera(text))

        layout.addWidget(self.Camera2, 1, 2)
        layout.addWidget(self.camera2Button, 2, 2)

        self.Camera3 = QLabel()
        self.Camera3.setPixmap(pixmap)
        self.Camera3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.Camera3.setAttribute(Qt.WA_TranslucentBackground)

        self.camera3Button = QPushButton("Camera 3")
        self.camera3Button.clicked.connect(lambda checked=None, text=3: self.viewIndividualCamera(text))

        layout.addWidget(self.Camera3, 1, 3)
        layout.addWidget(self.camera3Button, 2, 3)

        self.Camera4 = QLabel()
        self.Camera4.setPixmap(pixmap)
        self.Camera4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.Camera4.setAttribute(Qt.WA_TranslucentBackground)

        self.camera4Button = QPushButton("Camera 4")
        self.camera4Button.clicked.connect(lambda checked=None, text=4: self.viewIndividualCamera(text))

        layout.addWidget(self.Camera4, 1, 4)
        layout.addWidget(self.camera4Button, 2, 4)

        ioBoxImage = QLabel()
        ioBoxImage.setPixmap(ioBoxPixmap)
        ioBoxImage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ioBoxImage.setAttribute(Qt.WA_TranslucentBackground)

        self.routerButton = QPushButton("Router Webpage")
        self.routerButton.clicked.connect(self.openRouter)

        self.backButton = QPushButton("Back")
        self.backButton.clicked.connect(self.closeEvent)
        self.backButton.setStyleSheet("""border-radius: 8px;
                color: white;
                border: 1px solid #202E23;
                background-color: #295231;
                padding: 5px 15px;""")

        self.relaysButton = QPushButton("Relays")
        self.relaysButton.clicked.connect(self.openRelays)

        if selectedTextDevice == None:
            self.relaysButton.hide()
        elif selectedTextDevice.strip() == "NULL":
            self.relaysButton.hide()

        self.errorMessage = QLabel()
        self.errorMessage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.errorMessage.setAttribute(Qt.WA_TranslucentBackground)

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

            layout.addWidget(ioBoxImage, 3, 0, 2, 1)

            layout.addWidget(self.routerButton, 5, 0)

            layout.addWidget(self.relaysButton, 6, 0)

            layout.addWidget(self.backButton, 7, 0)

            layout.addWidget(self.errorMessage, 8, 0)

        elif selectedCCTV == 2:

            self.Camera4.hide()
            self.camera4Button.hide()

            self.Camera3.hide()
            self.camera3Button.hide()

            layout.addWidget(unitLabel, 0, 1)

            layout.addWidget(self.allCameras, 1, 0)
            layout.addWidget(self.allCamerasButton, 2, 0)

            layout.addWidget(self.Camera1, 1, 1)
            layout.addWidget(self.camera1Button, 2, 1)

            layout.addWidget(ioBoxImage, 3, 1, 2, 1)

            layout.addWidget(self.routerButton, 5, 1, 1, 1)

            layout.addWidget(self.relaysButton, 6, 1, 1, 1)

            layout.addWidget(self.backButton, 7, 1, 1, 1)

            layout.addWidget(self.errorMessage, 8, 1)


        elif selectedCCTV == 3:

            self.Camera4.hide()
            self.camera4Button.hide()

            layout.addWidget(unitLabel, 0, 1, 1, 2)

            layout.addWidget(self.allCameras, 1, 0)
            layout.addWidget(self.allCamerasButton, 2, 0)

            layout.addWidget(self.Camera1, 1, 1)
            layout.addWidget(self.camera1Button, 2, 1)

            layout.addWidget(ioBoxImage, 3, 0, 2, 4)

            layout.addWidget(self.routerButton, 5, 1, 1, 2)

            layout.addWidget(self.relaysButton, 6, 1, 1, 2)

            layout.addWidget(self.backButton, 7, 1, 1, 2)

            layout.addWidget(self.errorMessage, 8, 1, 1, 2)


        else:

            layout.addWidget(unitLabel, 0, 2)

            layout.addWidget(self.allCameras, 1, 0)
            layout.addWidget(self.allCamerasButton, 2, 0)

            layout.addWidget(self.Camera1, 1, 1)
            layout.addWidget(self.camera1Button, 2, 1)

            layout.addWidget(ioBoxImage, 3, 0, 2, 5)

            layout.addWidget(self.routerButton, 5, 1, 1, 3)

            layout.addWidget(self.relaysButton, 6, 1, 1, 3)

            layout.addWidget(self.backButton, 7, 1, 1, 3)

            layout.addWidget(self.errorMessage, 8, 2)

        self.checkUnitStatus()

        self.setLayout(layout)

        self.setStyleSheet(graidentSheet)

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
        unitStatus = checkURL(selectedIP, 64430, 5)
        apacheStatus = checkURL("81.179.155.109", 78, 1)
        if unitStatus == 0:

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
            self.errorMessage.setStyleSheet("color: #1eff00;"
                                            "font: bold 14px;")
        if apacheStatus == 0:
            self.relaysButton.setEnabled(False)
            self.relaysButton.setStyleSheet("background-color: red;")

    def openRouter(self):
        webbrowser.open(f"https://{selectedIP}:64430/")

    def openRelays(self):
        self.openRelaysPage = relays()
        self.openRelaysPage.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.openRelaysPage.frameGeometry()
        Geo.moveCenter(Center)
        self.openRelaysPage.move(Geo.topLeft())

    def closeEvent(self):
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

        self.closed6M = resourcePath("Assets/Images/SolarClosedLeft6M.png")
        self.open6M = resourcePath("Assets/Images/SolarOpenLeft6M.png")
        self.closed4M = resourcePath("Assets/Images/SolarClosedLeft.png")
        self.open4M = resourcePath("Assets/Images/SolarOpenLeft.png")

        if selectedUnitSize.strip() == "6M":
            self.closedSolarPanels = self.closed6M
            self.openSolarPanels = self.open6M
        else:
            self.closedSolarPanels = self.closed4M
            self.openSolarPanels = self.open4M

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

        if selectedTextDevice != None:
            if selectedTextDevice.strip() != "NULL":
                self.solarStatus = SQL.fetchSolarState(selectedUnit)
                self.solarStatus = int(self.solarStatus[0])
            else:
                self.solarStatus = "N/A"

        else:
            self.solarStatus = "N/A"

        super().__init__()

        self.setWindowTitle(selectedUnit)
        self.setGeometry(0, 0, 600, 600)
        self.setWindowIcon(QIcon(windowIcon))
        self.setWindowIconText("ARC")
        self.setWindowFlags(Qt.FramelessWindowHint)

        layout = QGridLayout()

        unitLabel = QLabel(selectedIP)
        unitLabel.setStyleSheet("font: bold 14px;"
                                "color: white;")
        unitLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        unitLabel.setAttribute(Qt.WA_TranslucentBackground)

        sunPixmap = QPixmap(self.sunPath)
        batteryPixmap = QPixmap(self.batteryPath)
        loadPixmap = QPixmap(self.loadPath)
        cameraPixmap = QPixmap(cameraPath)

        self.sunImage = QLabel()
        self.sunImage.setPixmap(sunPixmap)
        self.sunImage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sunImage.setAttribute(Qt.WA_TranslucentBackground)

        self.solarPower = QLabel(str(unitSolar) + " W")
        self.solarPower.setStyleSheet("font: bold 14px;"
                                      "color: white;")
        self.solarPower.setAttribute(Qt.WA_TranslucentBackground)
        self.solarPower.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.sunImage, 3, 4)
        layout.addWidget(self.solarPower, 4, 4)

        self.batteryImage = QLabel()
        self.batteryImage.setPixmap(batteryPixmap)
        self.batteryImage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.batteryImage.setAttribute(Qt.WA_TranslucentBackground)

        self.batteryVoltage = QLabel(str(unitVoltage) + " V")
        self.batteryVoltage.setAttribute(Qt.WA_TranslucentBackground)
        self.batteryVoltage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if unitVoltage >= 25.5:
            self.batteryVoltage.setStyleSheet("font: bold 14px;"
                                              "color: #1eff00;")
        elif unitVoltage >= 24 and unitVoltage < 25.5:
            self.batteryVoltage.setStyleSheet("font: bold 14px;"
                                              "color: yellow;")
        elif unitVoltage < 24 and unitVoltage >= 23.6:
            self.batteryVoltage.setStyleSheet("font: bold 14px;"
                                              "color: red;")
        elif unitVoltage < 23.6:
            self.batteryVoltage.setStyleSheet("font: bold 14px;"
                                              "color: red;")

        layout.addWidget(self.batteryImage, 7, 2)
        layout.addWidget(self.batteryVoltage, 8, 2)

        self.loadImage = QLabel()
        self.loadImage.setPixmap(loadPixmap)
        self.loadImage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loadImage.setAttribute(Qt.WA_TranslucentBackground)

        self.loadDraw = QLabel(str(unitLoad) + " W")
        self.loadDraw.setAttribute(Qt.WA_TranslucentBackground)
        self.loadDraw.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if unitLoad <= 0:
            self.loadDraw.setStyleSheet("font: bold 14px;"
                                        "color: #1eff00;")

        else:
            self.loadDraw.setStyleSheet("font: bold 14px;"
                                        "color: red;")

        layout.addWidget(self.loadImage, 3, 0)
        layout.addWidget(self.loadDraw, 4, 0)

        self.solarPanelsImage = QLabel()
        self.solarPanelsImage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.solarPanelsImage.setAttribute(Qt.WA_TranslucentBackground)

        if self.solarStatus == 1:
            solarPanelsPixmap = QPixmap(self.openSolarPanels)
        elif self.solarStatus == "N/A":
            solarPanelsPixmap = QPixmap(self.openSolarPanels)
        elif self.solarStatus == 0:
            solarPanelsPixmap = QPixmap(self.closedSolarPanels)

        self.solarPanelsImage.setPixmap(solarPanelsPixmap)

        layout.addWidget(self.solarPanelsImage, 2, 1, 5, 3)

        self.allCameras = QLabel()
        self.allCameras.setPixmap(cameraPixmap)
        self.allCameras.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.allCameras.setAttribute(Qt.WA_TranslucentBackground)


        self.allCamerasButton = QPushButton("All Cameras")
        self.allCamerasButton.clicked.connect(self.viewAllCameras)

        self.Camera1 = QLabel()
        self.Camera1.setPixmap(cameraPixmap)
        self.Camera1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.Camera1.setAttribute(Qt.WA_TranslucentBackground)

        self.camera1Button = QPushButton("Camera 1")
        self.camera1Button.clicked.connect(lambda checked=None, text=1: self.viewIndividualCamera(text))

        self.Camera2 = QLabel()
        self.Camera2.setPixmap(cameraPixmap)
        self.Camera2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.Camera2.setAttribute(Qt.WA_TranslucentBackground)

        self.camera2Button = QPushButton("Camera 2")
        self.camera2Button.clicked.connect(lambda checked=None, text=2: self.viewIndividualCamera(text))

        layout.addWidget(self.Camera2, 0, 2)
        layout.addWidget(self.camera2Button, 1, 2)

        self.Camera3 = QLabel()
        self.Camera3.setPixmap(cameraPixmap)
        self.Camera3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.Camera3.setAttribute(Qt.WA_TranslucentBackground)

        self.camera3Button = QPushButton("Camera 3")
        self.camera3Button.clicked.connect(lambda checked=None, text=3: self.viewIndividualCamera(text))

        layout.addWidget(self.Camera3, 0, 3)
        layout.addWidget(self.camera3Button, 1, 3)

        self.Camera4 = QLabel()
        self.Camera4.setPixmap(cameraPixmap)
        self.Camera4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.Camera4.setAttribute(Qt.WA_TranslucentBackground)

        self.camera4Button = QPushButton("Camera 4")
        self.camera4Button.clicked.connect(lambda checked=None, text=4: self.viewIndividualCamera(text))

        layout.addWidget(self.Camera4, 0, 4)
        layout.addWidget(self.camera4Button, 1, 4)

        victronButton = QPushButton("Victron Webpage")
        victronButton.clicked.connect(self.openVictron)

        self.routerButton = QPushButton("Router Webpage")
        self.routerButton.clicked.connect(self.openRouter)

        efoyButton = QPushButton("Efoy Webpage")
        efoyButton.clicked.connect(self.openEfoy)

        layout.addWidget(victronButton, 9, 1)
        layout.addWidget(self.routerButton, 9, 2)
        layout.addWidget(efoyButton, 9, 3)

        self.backButton = QPushButton("Back")
        self.backButton.clicked.connect(self.closeEvent)
        self.backButton.setStyleSheet("""border-radius: 8px;
        color: white;
        border: 1px solid #202E23;
        background-color: #295231;
        padding: 5px 15px;""")

        layout.addWidget(self.backButton, 11, 2)

        self.relaysButton = QPushButton("Relays")
        self.relaysButton.clicked.connect(self.openRelays)

        layout.addWidget(self.relaysButton, 10, 2)

        if selectedTextDevice == None:
            self.relaysButton.hide()
        elif selectedTextDevice.strip() == "NULL":
            self.relaysButton.hide()

        self.errorMessage = QLabel()
        self.errorMessage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.errorMessage.setAttribute(Qt.WA_TranslucentBackground)

        layout.addWidget(self.errorMessage, 12, 2)

        if selectedCCTV == 1:

            self.Camera4.hide()
            self.camera4Button.hide()

            self.Camera3.hide()
            self.camera3Button.hide()

            self.Camera2.hide()
            self.camera2Button.hide()

            self.allCameras.hide()
            self.allCamerasButton.hide()

            layout.addWidget(self.Camera1, 0, 0)
            layout.addWidget(self.camera1Button, 1, 0)


        elif selectedCCTV == 2:

            self.Camera4.hide()
            self.camera4Button.hide()

            self.Camera3.hide()
            self.camera3Button.hide()

            layout.addWidget(self.allCameras, 0, 0)
            layout.addWidget(self.allCamerasButton, 1, 0)

            layout.addWidget(self.Camera1, 0, 1)
            layout.addWidget(self.camera1Button, 1, 1)


        elif selectedCCTV == 3:

            self.Camera4.hide()
            self.camera4Button.hide()

            layout.addWidget(self.allCameras, 0, 0)
            layout.addWidget(self.allCamerasButton, 1, 0)

            layout.addWidget(self.Camera1, 0, 1)
            layout.addWidget(self.camera1Button, 1, 1)

        else:

            layout.addWidget(self.allCameras, 0, 0)
            layout.addWidget(self.allCamerasButton, 1, 0)

            layout.addWidget(self.Camera1, 0, 1)
            layout.addWidget(self.camera1Button, 1, 1)

        if selectedEfoyID == "":
            efoyButton.hide()

        self.checkUnitStatus()

        self.setLayout(layout)

        self.setStyleSheet(graidentSheet)

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
        unitStatus = checkURL(selectedIP, 64430, 5)
        apacheStatus = checkURL("81.179.155.109", 78,1)
        if unitStatus == 0:

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
            self.errorMessage.setStyleSheet("color: #1eff00;"
                                            "font: bold 14px;")
        if apacheStatus == 0:
            self.relaysButton.setEnabled(False)
            self.relaysButton.setStyleSheet("background-color: red;")
    def updateData(self):
        global unitVoltage
        global unitLoad
        global unitSolar

        pullVictronData(selectedUnit)

        if selectedTextDevice != None:
            if selectedTextDevice.strip() != "NULL":
                self.solarStatus = SQL.fetchSolarState(selectedUnit)
                self.solarStatus = int(self.solarStatus[0])
            else:
                self.solarStatus = "N/A"

        else:
            self.solarStatus = "N/A"

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

        if self.solarStatus == 1:
            solarPanelsPixmap = QPixmap(self.openSolarPanels)
            self.solarPanelsImage.setPixmap(solarPanelsPixmap)
        elif self.solarStatus == 0:
            solarPanelsPixmap = QPixmap(self.closedSolarPanels)
            self.solarPanelsImage.setPixmap(solarPanelsPixmap)
        elif self.solarStatus == "N/A":
            solarPanelsPixmap = QPixmap(self.openSolarPanels)
            self.solarPanelsImage.setPixmap(solarPanelsPixmap)

    def openVictron(self):
        webbrowser.open(f"https://vrm.victronenergy.com/installation/{selectedVictron}/dashboard")

    def openRouter(self):
        webbrowser.open(f"https://{selectedIP}:64430/")

    def openEfoy(self):
        webbrowser.open(f"https://www.efoy-cloud.com/devices/{selectedEfoyID}")

    def openRelays(self):
        self.openRelaysPage = relays()
        self.openRelaysPage.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.openRelaysPage.frameGeometry()
        Geo.moveCenter(Center)
        self.openRelaysPage.move(Geo.topLeft())

    def closeEvent(self):
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


class generatorDashboard(QWidget):
    def __init__(self):
        global unitVoltage
        global unitLoad
        global unitSolar

        windowIcon = resourcePath("Assets/Images/ARCGen.png")
        generatorImage = resourcePath("Assets/Images/ARCGenLeft.PNG")
        solarPanelsPixmap = QPixmap(generatorImage)

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

        self.setWindowTitle("Generator Dashboard")
        self.setGeometry(0, 0, 500, 500)
        self.setWindowIcon(QIcon(windowIcon))
        self.setWindowIconText("Generator")
        self.setWindowFlags(Qt.FramelessWindowHint)

        layout = QGridLayout()

        genLabel = QLabel(selectedUnit)
        genLabel.setStyleSheet("font: bold 14px;"
                               "color: white;")
        genLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        genLabel.setAttribute(Qt.WA_TranslucentBackground)

        layout.addWidget(genLabel, 0, 1)

        sunPixmap = QPixmap(self.sunPath)
        batteryPixmap = QPixmap(self.batteryPath)
        loadPixmap = QPixmap(self.loadPath)

        self.sunImage = QLabel()
        self.sunImage.setPixmap(sunPixmap)
        self.sunImage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sunImage.setAttribute(Qt.WA_TranslucentBackground)

        self.solarPower = QLabel(str(unitSolar) + " W")
        self.solarPower.setStyleSheet("font: bold 14px;"
                                      "color: white;")
        self.solarPower.setAttribute(Qt.WA_TranslucentBackground)
        self.solarPower.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.sunImage, 1, 2)
        layout.addWidget(self.solarPower, 2, 2)

        self.batteryImage = QLabel()
        self.batteryImage.setPixmap(batteryPixmap)
        self.batteryImage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.batteryImage.setAttribute(Qt.WA_TranslucentBackground)

        self.batteryVoltage = QLabel(str(unitVoltage) + " V")
        self.batteryVoltage.setAttribute(Qt.WA_TranslucentBackground)
        self.batteryVoltage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if unitVoltage >= 25.5:
            self.batteryVoltage.setStyleSheet("font: bold 14px;"
                                              "color: #1eff00;")
        elif unitVoltage >= 24 and unitVoltage < 25.5:
            self.batteryVoltage.setStyleSheet("font: bold 14px;"
                                              "color: yellow;")
        elif unitVoltage < 24 and unitVoltage >= 23.6:
            self.batteryVoltage.setStyleSheet("font: bold 14px;"
                                              "color: red;")
        elif unitVoltage < 23.6:
            self.batteryVoltage.setStyleSheet("font: bold 14px;"
                                              "color: red;")

        layout.addWidget(self.batteryImage, 4, 1)
        layout.addWidget(self.batteryVoltage, 5, 1)

        self.loadImage = QLabel()
        self.loadImage.setPixmap(loadPixmap)
        self.loadImage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loadImage.setAttribute(Qt.WA_TranslucentBackground)

        self.loadDraw = QLabel(str(unitLoad) + " W")
        self.loadDraw.setAttribute(Qt.WA_TranslucentBackground)
        self.loadDraw.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if unitLoad <= 0:
            self.loadDraw.setStyleSheet("font: bold 14px;"
                                        "color: #1eff00;")
        else:
            self.loadDraw.setStyleSheet("font: bold 14px;"
                                        "color: red;")

        layout.addWidget(self.loadImage, 1, 0)
        layout.addWidget(self.loadDraw, 2, 0)

        self.solarPanelsImage = QLabel()
        self.solarPanelsImage.setPixmap(solarPanelsPixmap)
        self.solarPanelsImage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #self.solarPanelsImage.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.solarPanelsImage.setAttribute(Qt.WA_TranslucentBackground)

        layout.addWidget(self.solarPanelsImage, 1,1,3,1)

        victronButton = QPushButton("Victron Webpage")
        victronButton.clicked.connect(self.openVictron)

        layout.addWidget(victronButton, 6, 0)

        efoy1Button = QPushButton("Efoy No.1")
        efoy1Button.clicked.connect(self.openEfoy1)

        layout.addWidget(efoy1Button, 6, 1)

        efoy2Button = QPushButton("Efoy No.2")
        efoy2Button.clicked.connect(self.openEfoy2)

        layout.addWidget(efoy2Button, 6, 2)

        if selectedEfoyID2 == "":
            efoy2Button.hide()

        self.backButton = QPushButton("Back")
        self.backButton.clicked.connect(self.closeEvent)
        self.backButton.setStyleSheet("""border-radius: 8px;
                color: white;
                border: 1px solid #202E23;
                background-color: #295231;
                padding: 5px 15px;""")

        layout.addWidget(self.backButton, 7, 1)

        self.setLayout(layout)

        self.setStyleSheet(graidentSheet)

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateData)
        self.timer.start(60000)

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

    def openEfoy1(self):
        webbrowser.open(f"https://www.efoy-cloud.com/devices/{selectedEfoyID}")

    def openEfoy2(self):
        webbrowser.open(f"https://www.efoy-cloud.com/devices/{selectedEfoyID2}")

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
        self.setWindowFlags(Qt.FramelessWindowHint)

        layout = QGridLayout()

        self.userSelection = QComboBox()
        self.userSelection.addItems(self.listOfUsers)
        self.userSelection.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
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

        self.backButton = QPushButton("Back")
        self.backButton.clicked.connect(self.closeEvent)
        self.backButton.setStyleSheet("""border-radius: 8px;
                        color: white;
                        border: 1px solid #202E23;
                        background-color: #295231;
                        padding: 5px 15px;""")

        layout.addWidget(self.backButton, 6, 1)

        self.errorMessage = QLabel("")
        self.errorMessage.setStyleSheet("color: red")
        self.errorMessage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.errorMessage, 7, 1)

        self.setLayout(layout)

        self.setStyleSheet(baseSheet)

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

    def closeEvent(self):
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
        self.setWindowFlags(Qt.FramelessWindowHint)

        layout = QGridLayout()

        self.userSelection = QComboBox()
        self.userSelection.addItems(self.listOfUsers)
        self.userSelection.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
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

        self.backButton = QPushButton("Back")
        self.backButton.clicked.connect(self.closeEvent)
        self.backButton.setStyleSheet("""border-radius: 8px;
                        color: white;
                        border: 1px solid #202E23;
                        background-color: #295231;
                        padding: 5px 15px;""")

        layout.addWidget(self.backButton, 7, 1)

        self.errorMessage = QLabel("")
        self.errorMessage.setStyleSheet("color: red")
        self.errorMessage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.errorMessage, 8, 1)

        self.setLayout(layout)

        self.setStyleSheet(baseSheet)

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
        if self.selectedRights == "SUPERADMIN":
            self.errorMessage.setText("Only one Super Admin Account Allowed")
        else:
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

    def closeEvent(self):
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

        fetchUnits = SQL.fetchUnitsManagement()
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
        self.newTextDevice = "NULL"
        self.newUnitSize = "4M"

        self.w3w = ""

        super().__init__()

        self.setWindowTitle("Unit Management")
        self.setGeometry(0, 0, 700, 300)
        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setWindowIconText("Logo")
        self.setWindowFlags(Qt.FramelessWindowHint)

        layout = QGridLayout()

        unitManagementDropdown = QComboBox()
        unitManagementDropdown.addItems(self.listOfUnits)
        unitManagementDropdown.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        unitManagementDropdown.setPlaceholderText("Unit Management")
        unitManagementDropdown.currentIndexChanged.connect(self.unitChanged)

        layout.addWidget(unitManagementDropdown, 0, 0, 1, 4)

        self.unitName = QLabel("")

        layout.addWidget(self.unitName, 2, 0)

        self.locationLabel = QLabel("Location")
        self.locationLabel.hide()
        self.locationEdit = QLineEdit()
        self.locationEdit.textChanged.connect(self.getUpdatedLocation)
        self.locationEdit.hide()


        layout.addWidget(self.locationEdit, 2, 1)
        layout.addWidget(self.locationLabel, 1, 1)

        self.companyLabel = QLabel("Company")
        self.companyLabel.hide()
        self.companyEdit = QLineEdit()
        self.companyEdit.textChanged.connect(self.getUpdatedCompany)
        self.companyEdit.hide()

        layout.addWidget(self.companyLabel, 1, 2)
        layout.addWidget(self.companyEdit, 2, 2)


        self.numCamerasLabel = QLabel("Number of Cameras")
        self.numCamerasLabel.hide()
        self.numCameras = QLineEdit()
        self.numCameras.textChanged.connect(self.getUpdatedNumCCTV)
        self.numCameras.hide()

        layout.addWidget(self.numCamerasLabel, 1, 3)
        layout.addWidget(self.numCameras, 2, 3)

        changeButton = QPushButton("Change Details")
        changeButton.clicked.connect(self.changeUnit)

        layout.addWidget(changeButton, 3, 0, 1, 2)

        deleteButton = QPushButton("Delete")
        deleteButton.clicked.connect(self.deleteUnit)

        layout.addWidget(deleteButton, 3, 2, 1, 2)

        addNewUnitLabel = QLabel("--------------- Add New Unit ---------------")
        addNewUnitLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(addNewUnitLabel, 4, 0, 1, 4)

        self.unitNameAdd = QLineEdit()
        self.unitNameAdd.setPlaceholderText("Unit ID")
        self.unitNameAdd.textChanged.connect(self.getNewUnitName)

        layout.addWidget(self.unitNameAdd, 5, 0)

        self.locationAdd = QLineEdit()
        self.locationAdd.setPlaceholderText("Location")
        self.locationAdd.textChanged.connect(self.getNewLocation)

        layout.addWidget(self.locationAdd, 5, 1)

        self.companyAdd = QLineEdit()
        self.companyAdd.setPlaceholderText("Company")
        self.companyAdd.textChanged.connect(self.getNewCompany)

        layout.addWidget(self.companyAdd, 5, 2)

        self.numCamerasAdd = QSpinBox()
        self.numCamerasAdd.setMinimum(1)
        self.numCamerasAdd.setMaximum(4)
        self.numCamerasAdd.textChanged.connect(self.getNewNumCCTV)

        layout.addWidget(self.numCamerasAdd, 5, 3)

        self.cameratypeAdd = QLineEdit()
        self.cameratypeAdd.setPlaceholderText("Camera Manufacturer")
        self.cameratypeAdd.textChanged.connect(self.getCameraType)

        layout.addWidget(self.cameratypeAdd, 6, 0)

        self.IPAdd = QLineEdit()
        self.IPAdd.setPlaceholderText("IP Address")
        self.IPAdd.textChanged.connect(self.getNewIP)

        layout.addWidget(self.IPAdd, 6, 1)

        self.textDevice = QRadioButton("Text Device")
        self.textDevice.toggled.connect(self.textDeviceState)

        layout.addWidget(self.textDevice, 6, 2)

        unitType = QComboBox()
        unitType.setPlaceholderText("Unit Type")
        unitType.addItems(["ARC", "IO"])
        unitType.currentIndexChanged.connect(self.getNewUnitType)

        layout.addWidget(unitType, 7, 0)

        self.unitSize = QComboBox()
        self.unitSize.addItems(["4M", "6M"])
        self.unitSize.currentIndexChanged.connect(self.getNewUnitSize)

        layout.addWidget(self.unitSize, 7, 1)

        self.victronAdd = QLineEdit()
        self.victronAdd.setPlaceholderText("Victron Site ID")
        self.victronAdd.textChanged.connect(self.getNewVictronID)

        layout.addWidget(self.victronAdd, 7, 2)

        self.efoyAdd = QLineEdit()
        self.efoyAdd.setPlaceholderText("Efoy ID")
        self.efoyAdd.textChanged.connect(self.getNewEfoy)

        layout.addWidget(self.efoyAdd, 7, 3)

        self.latAdd = QLineEdit("")
        self.latAdd.setPlaceholderText("Latitude")
        self.latAdd.textChanged.connect(self.getNewLat)

        layout.addWidget(self.latAdd, 8, 0,1,2)

        self.lonAdd = QLineEdit("")
        self.lonAdd.setPlaceholderText("Longitude")
        self.lonAdd.textChanged.connect(self.getNewLon)

        layout.addWidget(self.lonAdd, 8, 2,1,2)


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

        self.backButton = QPushButton("Back")
        self.backButton.clicked.connect(self.closeEvent)
        self.backButton.setStyleSheet("""border-radius: 8px;
                        color: white;
                        border: 1px solid #202E23;
                        background-color: #295231;
                        padding: 5px 15px;""")

        layout.addWidget(self.backButton, 11, 1, 1, 2)

        self.errorMessage = QLabel("")
        self.errorMessage.setStyleSheet("color: red")
        self.errorMessage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.errorMessage, 12, 1, 1, 2)

        self.setLayout(layout)

        self.setStyleSheet(baseSheet)

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
            self.unitSize.show()
        elif unitIndex == 1:
            self.newUnitType = "IO"
            self.victronAdd.hide()
            self.efoyAdd.hide()
            self.unitSize.hide()

    def getNewVictronID(self, ID):
        self.newVictronID = ID

    def getNewEfoy(self, EFOY):
        self.newEfoy = EFOY

    def getNewLat(self, Lat):
        self.newLat = Lat

    def getNewLon(self, Lon):
        self.newLon = Lon

    def textDeviceState(self):
        if self.newTextDevice == "NULL":
            self.newTextDevice = "Yes"
        else:
            self.newTextDevice = "NULL"

    def getNewUnitSize(self, unitIndex):
        if unitIndex == 1:
            self.newUnitSize = "4M"
        else:
            self.newUnitSize = "6M"

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
        self.locationLabel.show()
        self.companyLabel.show()
        self.numCamerasLabel.show()

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
        SQL.deleteUnits(self.selectedUnit, selectedTextDevice)
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
                         self.newCompany, self.newLat, self.newLon, self.newUnitType, self.newCameraType, self.newEfoy,
                         self.newTextDevice, self.newUnitSize)
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

    def closeEvent(self):
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

        fetchUnits = SQL.fetchUnitsManagement()
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
        self.newTextDevice = "NULL"
        self.newUnitSize = "4M"

        self.w3w = ""

        super().__init__()

        self.setWindowTitle("Super Unit Management")
        self.setGeometry(0, 0, 700, 300)
        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setWindowIconText("Logo")
        self.setWindowFlags(Qt.FramelessWindowHint)

        layout = QGridLayout()

        unitManagementDropdown = QComboBox()
        unitManagementDropdown.addItems(self.listOfUnits)
        unitManagementDropdown.setPlaceholderText("Unit Management")
        unitManagementDropdown.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        unitManagementDropdown.currentIndexChanged.connect(self.unitChanged)

        layout.addWidget(unitManagementDropdown, 0, 0, 1, 4)

        self.unitName = QLabel("")

        layout.addWidget(self.unitName, 2, 0)

        self.locationLabel = QLabel("Location")
        self.locationLabel.hide()
        self.locationEdit = QLineEdit()
        self.locationEdit.textChanged.connect(self.getUpdatedLocation)
        self.locationEdit.hide()

        layout.addWidget(self.locationLabel,1,1)
        layout.addWidget(self.locationEdit, 2, 1)

        self.companyLabel = QLabel("Company")
        self.companyLabel.hide()
        self.companyEdit = QLineEdit()
        self.companyEdit.textChanged.connect(self.getUpdatedCompany)
        self.companyEdit.hide()

        layout.addWidget(self.companyLabel,1,2)
        layout.addWidget(self.companyEdit, 2, 2)

        self.numCamerasLabel = QLabel("Number of Cameras")
        self.numCamerasLabel.hide()
        self.numCameras = QLineEdit()
        self.numCameras.textChanged.connect(self.getUpdatedNumCCTV)
        self.numCameras.hide()

        layout.addWidget(self.numCamerasLabel,1,3)
        layout.addWidget(self.numCameras, 2, 3)

        self.cameraLabel = QLabel("Camera Manufacture")
        self.cameraLabel.hide()
        self.cameraType = QLineEdit()
        self.cameraType.textChanged.connect(self.getUpdatedType)
        self.cameraType.hide()

        layout.addWidget(self.cameraLabel,3,0)
        layout.addWidget(self.cameraType, 4, 0)

        self.IPLabel = QLabel("IP Address")
        self.IPLabel.hide()
        self.IP = QLineEdit()
        self.IP.textChanged.connect(self.getUpdatedIP)
        self.IP.hide()

        layout.addWidget(self.IPLabel, 3, 1)
        layout.addWidget(self.IP, 4, 1)

        self.victronLabel = QLabel("Victron Site ID")
        self.victronLabel.hide()
        self.Victron = QLineEdit()
        self.Victron.textChanged.connect(self.getUpdatedVictron)
        self.Victron.hide()

        layout.addWidget(self.victronLabel, 3, 2)
        layout.addWidget(self.Victron, 4, 2)

        self.efoyLabel = QLabel("Efoy ID")
        self.efoyLabel.hide()
        self.Efoy = QLineEdit()
        self.Efoy.textChanged.connect(self.getUpdatedEfoy)
        self.Efoy.hide()

        layout.addWidget(self.efoyLabel,3,3)
        layout.addWidget(self.Efoy, 4, 3)

        self.latLabel = QLabel("Latitude")
        self.latLabel.hide()
        self.Lat = QLineEdit()
        self.Lat.textChanged.connect(self.getUpdatedLat)
        self.Lat.hide()

        layout.addWidget(self.latLabel,5, 0)
        layout.addWidget(self.Lat, 6, 0)

        self.lonLabel = QLabel("Longitude")
        self.lonLabel.hide()
        self.Lon = QLineEdit()
        self.Lon.textChanged.connect(self.getUpdatedLon)
        self.Lon.hide()

        layout.addWidget(self.lonLabel,5,1)
        layout.addWidget(self.Lon, 6, 1)

        changeButton = QPushButton("Change Details")
        changeButton.clicked.connect(self.changeUnit)

        layout.addWidget(changeButton, 7, 0, 1, 2)

        deleteButton = QPushButton("Delete")
        deleteButton.clicked.connect(self.deleteUnit)

        layout.addWidget(deleteButton, 7, 2, 1, 2)

        addNewUnitLabel = QLabel("--------------- Add New Unit ---------------")
        addNewUnitLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(addNewUnitLabel, 8, 0, 1, 4)

        self.unitNameAdd = QLineEdit()
        self.unitNameAdd.setPlaceholderText("Unit ID")
        self.unitNameAdd.textChanged.connect(self.getNewUnitName)

        layout.addWidget(self.unitNameAdd, 9, 0)

        self.locationAdd = QLineEdit()
        self.locationAdd.setPlaceholderText("Location")
        self.locationAdd.textChanged.connect(self.getNewLocation)

        layout.addWidget(self.locationAdd, 9, 1)

        self.companyAdd = QLineEdit()
        self.companyAdd.setPlaceholderText("Company")
        self.companyAdd.textChanged.connect(self.getNewCompany)

        layout.addWidget(self.companyAdd, 9, 2)

        self.numCamerasAdd = QSpinBox()
        self.numCamerasAdd.setMinimum(1)
        self.numCamerasAdd.setMaximum(4)
        self.numCamerasAdd.textChanged.connect(self.getNewNumCCTV)

        layout.addWidget(self.numCamerasAdd, 9, 3)

        self.cameratypeAdd = QLineEdit()
        self.cameratypeAdd.setPlaceholderText("Camera Manufacturer")
        self.cameratypeAdd.textChanged.connect(self.getCameraType)

        layout.addWidget(self.cameratypeAdd, 10, 0)

        self.IPAdd = QLineEdit()
        self.IPAdd.setPlaceholderText("IP Address")
        self.IPAdd.textChanged.connect(self.getNewIP)

        layout.addWidget(self.IPAdd, 10, 1)

        self.textDevice = QRadioButton("Text Device")
        self.textDevice.toggled.connect(self.textDeviceState)

        layout.addWidget(self.textDevice, 10, 2)

        unitType = QComboBox()
        unitType.addItems(["ARC", "IO"])
        unitType.currentIndexChanged.connect(self.getNewUnitType)

        layout.addWidget(unitType, 11, 0)

        self.victronAdd = QLineEdit()
        self.victronAdd.setPlaceholderText("Victron Site ID")
        self.victronAdd.textChanged.connect(self.getNewVictronID)

        layout.addWidget(self.victronAdd, 11, 2)

        self.efoyAdd = QLineEdit()
        self.efoyAdd.setPlaceholderText("Efoy ID")
        self.efoyAdd.textChanged.connect(self.getNewEfoy)

        layout.addWidget(self.efoyAdd, 11, 3)

        self.unitSize = QComboBox()
        self.unitSize.addItems(["4M","6M"])
        self.unitSize.currentIndexChanged.connect(self.getNewUnitSize)

        layout.addWidget(self.unitSize,11,1)

        self.latAdd = QLineEdit("")
        self.latAdd.setPlaceholderText("Latitude")
        self.latAdd.textChanged.connect(self.getNewLat)

        layout.addWidget(self.latAdd, 12, 0,1,2)

        self.lonAdd = QLineEdit("")
        self.lonAdd.setPlaceholderText("Longitude")
        self.lonAdd.textChanged.connect(self.getNewLon)

        layout.addWidget(self.lonAdd, 12, 2,1,2)

        addUnit = QPushButton("Add New Unit")
        addUnit.clicked.connect(self.addNewUnit)

        layout.addWidget(addUnit, 13, 0, 1, 4)

        self.w3wLineEdit = QLineEdit()
        self.w3wLineEdit.setPlaceholderText("what3words")
        self.w3wLineEdit.textChanged.connect(self.getW3W)

        layout.addWidget(self.w3wLineEdit, 14, 0, 1, 2)

        self.w3wButton = QPushButton("Convert")
        self.w3wButton.clicked.connect(self.convertW3W)

        layout.addWidget(self.w3wButton, 14, 2, 1, 2)

        self.backButton = QPushButton("Back")
        self.backButton.clicked.connect(self.closeEvent)
        self.backButton.setStyleSheet("""border-radius: 8px;
                        color: white;
                        border: 1px solid #202E23;
                        background-color: #295231;
                        padding: 5px 15px;""")

        layout.addWidget(self.backButton, 15, 1, 1, 2)

        self.errorMessage = QLabel("")
        self.errorMessage.setStyleSheet("color: red")
        self.errorMessage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.errorMessage, 16, 1, 1, 2)

        self.setLayout(layout)

        self.setStyleSheet(baseSheet)

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
            self.unitSize.show()
        elif unitIndex == 1:
            self.newUnitType = "IO"
            self.victronAdd.hide()
            self.efoyAdd.hide()
            self.unitSize.hide()

    def getNewVictronID(self, ID):
        self.newVictronID = ID

    def getNewEfoy(self, EFOY):
        self.newEfoy = EFOY

    def getNewLat(self, Lat):
        self.newLat = Lat

    def getNewLon(self, Lon):
        self.newLon = Lon

    def textDeviceState(self):
        if self.newTextDevice == "NULL":
            self.newTextDevice = "Yes"
        else:
            self.newTextDevice = "NULL"

    def getNewUnitSize(self, unitIndex):
        if unitIndex == 1:
            self.newUnitSize = "4M"
        else:
            self.newUnitSize = "6M"
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
        self.locationLabel.show()
        self.companyLabel.show()
        self.numCamerasLabel.show()
        self.cameraLabel.show()
        self.IPLabel.show()
        self.victronLabel.show()
        self.efoyLabel.show()
        self.latLabel.show()
        self.lonLabel.show()

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
                         self.newCompany, self.newLat, self.newLon, self.newUnitType, self.newCameraType, self.newEfoy, self.newUnitSize)
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

    def closeEvent(self):
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
        self.setWindowFlags(Qt.FramelessWindowHint)

        layout = QGridLayout()

        genManagementDropdown = QComboBox()
        genManagementDropdown.addItems(self.listOfGen)
        genManagementDropdown.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        genManagementDropdown.setPlaceholderText("Generator Management")
        genManagementDropdown.currentIndexChanged.connect(self.genChanged)

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
        changeButton.clicked.connect(self.changeGen)

        layout.addWidget(changeButton, 2, 0, 1, 2)

        deleteButton = QPushButton("Delete")
        # deleteButton.clicked.connect(self.deleteGen)

        layout.addWidget(deleteButton, 2, 2, 1, 2)

        addNewUnitLabel = QLabel("--------------- Add New Generator ---------------")
        addNewUnitLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(addNewUnitLabel, 3, 0, 1, 4)

        self.genNameAdd = QLineEdit()
        self.genNameAdd.setPlaceholderText("Unit ID")
        self.genNameAdd.textChanged.connect(self.getNewGenName)

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
        self.efoy1Add.setPlaceholderText("Efoy 1 ID")
        self.efoy1Add.textChanged.connect(self.getNewEfoy1)

        layout.addWidget(self.efoy1Add, 5, 0)

        self.efoy2Add = QLineEdit()
        self.efoy2Add.setPlaceholderText("Efoy 2 ID (Can be Null)")
        self.efoy2Add.textChanged.connect(self.getNewEfoy2)

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

        self.backButton = QPushButton("Back")
        self.backButton.clicked.connect(self.closeEvent)
        self.backButton.setStyleSheet("""border-radius: 8px;
                        color: white;
                        border: 1px solid #202E23;
                        background-color: #295231;
                        padding: 5px 15px;""")

        layout.addWidget(self.backButton, 7, 0, 1, 4)

        self.errorMessage = QLabel("")
        self.errorMessage.setStyleSheet("color: red")
        self.errorMessage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.errorMessage, 8, 1, 1, 2)

        self.setLayout(layout)

        self.setStyleSheet(baseSheet)

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

    def genChanged(self, index):

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

    def changeGen(self):

        SQL.updateGenSuper(self.selectedGen, self.selectedLocation, self.selectedCompany)

        self.errorMessage.setText("Generator Updated")

    def addNewGen(self):
        checkGen = SQL.checkGen(self.newGenName)

        if checkGen is not None:
            self.errorMessage.setText("Unit already in database")
        elif any(x == "" for x in (self.newGenName, self.newVictronID, self.newEfoy1)):
            self.errorMessage.setText("One or All Field Is Empty")
        elif "." not in self.newLat or "." not in self.newLon:
            self.errorMessage.setText("Lat and Lon do not Compute")
        else:
            SQL.addGenerator(self.newGenName, self.newVictronID, self.newLocation, self.newCompany, self.newLat,
                             self.newLon, self.newEfoy1, self.newEfoy2)
            self.errorMessage.setText("Generator Added")
            self.genNameAdd.setText("")
            self.locationAdd.setText("")
            self.companyAdd.setText("")
            self.victronAdd.setText("")
            self.efoy1Add.setText("")
            self.efoy2Add.setText("")
            self.latAdd.setText("")
            self.lonAdd.setText("")

    def closeEvent(self):
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
        self.setWindowFlags(Qt.FramelessWindowHint)

        layout = QGridLayout()

        genManagementDropdown = QComboBox()
        genManagementDropdown.addItems(self.listOfGen)
        genManagementDropdown.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        genManagementDropdown.setPlaceholderText("Generator Management")
        genManagementDropdown.currentIndexChanged.connect(self.genChanged)

        layout.addWidget(genManagementDropdown, 0, 0, 1, 4)

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
        changeButton.clicked.connect(self.changeGen)

        layout.addWidget(changeButton, 3, 0, 1, 2)

        deleteButton = QPushButton("Delete")
        # deleteButton.clicked.connect(self.deleteGen)

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

        self.backButton = QPushButton("Back")
        self.backButton.clicked.connect(self.closeEvent)
        self.backButton.setStyleSheet("""border-radius: 8px;
                        color: white;
                        border: 1px solid #202E23;
                        background-color: #295231;
                        padding: 5px 15px;""")

        layout.addWidget(self.backButton, 8, 1, 1, 2)

        self.errorMessage = QLabel("")
        self.errorMessage.setStyleSheet("color: red")
        self.errorMessage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.errorMessage, 9, 1, 1, 2)

        self.setLayout(layout)

        self.setStyleSheet(baseSheet)

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

    def genChanged(self, index):

        self.selectedGen = self.listOfGen[index]

        data = SQL.fetchGenDetails(self.selectedGen)

        for row in data:
            altered = list(row)
            self.selectedVictronID = str(altered[0])
            self.selectedLocation = altered[1]
            self.selectedCompany = altered[2]
            self.selectedEfoy1 = altered[3]
            self.selectedEfoy2 = altered[4]
            self.selectedLat = str(altered[5])
            self.selectedLon = str(altered[6])

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
        self.Efoy1.setText(self.selectedEfoy1)
        self.Efoy2.setText(self.selectedEfoy2)
        self.Lat.setText(self.selectedLat)
        self.Lon.setText(self.selectedLon)

    def changeGen(self):

        if any(x == "" for x in (self.selectedVictronID, self.selectedEfoy1)):
            self.errorMessage.setText("One or All Field Is Empty")
        elif "." not in self.selectedLat or "." not in self.selectedLon:
            self.errorMessage.setText("Lat and Lon do not Compute")
        else:
            SQL.updateGenSuper(self.selectedGen, self.selectedLocation, self.selectedCompany, self.selectedVictronID,
                               self.selectedEfoy1, self.selectedEfoy2, self.selectedLat, self.selectedLon)

            self.errorMessage.setText("Generator Updated")

    def addNewGen(self):
        checkGen = SQL.checkGen(self.newGenName)

        if checkGen is not None:
            self.errorMessage.setText("Unit already in database")
        elif any(x == "" for x in (self.newGenName, self.newVictronID, self.newEfoy1)):
            self.errorMessage.setText("One or All Field Is Empty")
        elif "." not in self.newLat or "." not in self.newLon:
            self.errorMessage.setText("Lat and Lon do not Compute")
        else:
            SQL.addGenerator(self.newGenName, self.newVictronID, self.newLocation, self.newCompany, self.newLat,
                             self.newLon, self.newEfoy1, self.newEfoy2)
            self.errorMessage.setText("Generator Added")
            self.genNameAdd.setText("")
            self.locationAdd.setText("")
            self.companyAdd.setText("")
            self.victronAdd.setText("")
            self.efoy1Add.setText("")
            self.efoy2Add.setText("")
            self.latAdd.setText("")
            self.lonAdd.setText("")

    def closeEvent(self):
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
        self.setWindowFlags(Qt.FramelessWindowHint)

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

        self.backButton = QPushButton("Back")
        self.backButton.clicked.connect(self.closeEvent)
        self.backButton.setStyleSheet("""border-radius: 8px;
                        color: white;
                        border: 1px solid #202E23;
                        background-color: #295231;
                        padding: 5px 15px;""")

        layout.addWidget(self.backButton)

        self.setLayout(layout)

        self.setStyleSheet(baseSheet)

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

    def closeEvent(self):

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

        self.setStyleSheet(baseSheet)

    def importMap(self):
        names = []

        lat = []

        lon = []

        if userCompany == "Sunstone":
            data = SQL.fetchLocationsSunstone()

            for row in data:
                altered = list(row)
                names.append(altered[0])
                lat.append(altered[1])
                lon.append(altered[2])

            data = SQL.fetchGeneratorLocationSunstone()

            for row in data:
                altered = list(row)
                names.append(altered[0])
                lat.append(altered[1])
                lon.append(altered[2])

        else:
            data = SQL.fetchLocations(userCompany)

            for row in data:
                altered = list(row)
                names.append(altered[0])
                lat.append(altered[1])
                lon.append(altered[2])

            data = SQL.fetchGeneratorLocation(userCompany)

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

        self.mainHeader = ("font-weight: bold;"
                      "border-radius: 8px;"
                      "color: white;"
                      "border: 1px solid #46a15b;"
                      "background-color: #295231;"
                      "padding: 5px 15px;"
                      "font-size: 14pt;")

        self.values = ("border-radius: 8px;"
                  "color: black;"
                  "border: 1px solid #46a15b;"
                  "background-color: #c8eacf;"
                  "padding: 5px 15px;"
                  "font-size: 14pt;")

        super().__init__()

        self.setWindowTitle("Victron Data Overview")
        self.setGeometry(0, 0, 700, 700)
        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setWindowIconText("Logo")
        self.setWindowFlags(Qt.FramelessWindowHint)

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

        self.Header1.setStyleSheet(self.mainHeader)
        self.Header2.setStyleSheet(self.mainHeader)
        self.Header3.setStyleSheet(self.mainHeader)
        self.Header4.setStyleSheet(self.mainHeader)

        self.unitsLayout.addWidget(self.Header1, 0, 0)
        self.unitsLayout.addWidget(self.Header2, 0, 1)
        self.unitsLayout.addWidget(self.Header3, 0, 2)
        self.unitsLayout.addWidget(self.Header4, 0, 3)

        j = 0
        for i in self.listOfUnits:
            self.unitName = QLabel(f"{i}")
            self.unitName.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.unitName.setStyleSheet(self.mainHeader)

            self.unitsLayout.addWidget(self.unitName, j + 1, 0)

            unitVoltage = self.listOfVoltage[j]
            unitLoad = self.listOfLoad[j]
            unitSolar = self.listOfSolar[j]

            self.batteryVoltage = QLabel(str(unitVoltage) + " V")
            self.batteryVoltage.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.batteryVoltage.setStyleSheet(self.values)

            self.unitsLayout.addWidget(self.batteryVoltage, j + 1, 1)

            self.solarPower = QLabel(str(unitSolar) + " W")
            self.solarPower.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.solarPower.setStyleSheet(self.values)

            self.unitsLayout.addWidget(self.solarPower, j + 1, 2)

            self.loadDraw = QLabel(str(unitLoad) + " W")
            self.loadDraw.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.loadDraw.setStyleSheet(self.values)

            self.unitsLayout.addWidget(self.loadDraw, j + 1, 3)

            j = j + 1

        groupBox.setLayout(self.unitsLayout)

        scrollArea = QScrollArea()
        scrollArea.setWidget(groupBox)
        scrollArea.setWidgetResizable(True)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        layout.addWidget(scrollArea)

        backButton = QPushButton("Back")
        backButton.clicked.connect(self.closeEvent)
        backButton.setStyleSheet("""border-radius: 8px;
                color: white;
                border: 1px solid #202E23;
                background-color: #295231;
                padding: 5px 15px;""")

        layout.addWidget(backButton)

        self.setLayout(layout)
        self.setStyleSheet(baseSheet)

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

        self.Header1.setStyleSheet(self.mainHeader)
        self.Header2.setStyleSheet(self.mainHeader)
        self.Header3.setStyleSheet(self.mainHeader)
        self.Header4.setStyleSheet(self.mainHeader)

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

            self.unitsLayout.addWidget(self.unitName, j + 1, 0)

            unitVoltage = self.listOfVoltage[j]
            unitLoad = self.listOfLoad[j]
            unitSolar = self.listOfSolar[j]

            self.batteryVoltage = QLabel(str(unitVoltage) + " V")
            self.batteryVoltage.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.unitsLayout.addWidget(self.batteryVoltage, j + 1, 1)

            self.solarPower = QLabel(str(unitSolar) + " W")
            self.solarPower.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.unitsLayout.addWidget(self.solarPower, j + 1, 2)

            self.loadDraw = QLabel(str(unitLoad) + " W")
            self.loadDraw.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.unitsLayout.addWidget(self.loadDraw, j + 1, 3)

            if selectedFilter == "Name":
                self.unitName.setStyleSheet(self.mainHeader)
                self.batteryVoltage.setStyleSheet(self.values)
                self.solarPower.setStyleSheet(self.values)
                self.loadDraw.setStyleSheet(self.values)
            elif selectedFilter == "Voltage":
                self.unitName.setStyleSheet(self.values)
                self.batteryVoltage.setStyleSheet(self.mainHeader)
                self.solarPower.setStyleSheet(self.values)
                self.loadDraw.setStyleSheet(self.values)
            elif selectedFilter == "Solar":
                self.unitName.setStyleSheet(self.values)
                self.batteryVoltage.setStyleSheet(self.values)
                self.solarPower.setStyleSheet(self.mainHeader)
                self.loadDraw.setStyleSheet(self.values)
            elif selectedFilter == "Load":
                self.unitName.setStyleSheet(self.values)
                self.batteryVoltage.setStyleSheet(self.values)
                self.solarPower.setStyleSheet(self.values)
                self.loadDraw.setStyleSheet(self.mainHeader)


            j = j + 1

    def closeEvent(self):
        self.hide()


class adminMonitoring(QWidget):
    def __init__(self):

        sunstoneIcon = resourcePath("Assets/Images/SunstoneLogo.png")

        self.listOfUnits = []
        self.listOfLocations = []

        fetchUnits = SQL.fetchUnitsSunstone()

        for row in fetchUnits:
            altered = list(row)
            self.listOfUnits.append(altered[0])
            self.listOfLocations.append(altered[1])

        self.dropdownLocations = list(dict.fromkeys(self.listOfLocations))
        self.dropdownLocations.insert(0, "All Units")

        super().__init__()

        self.setWindowTitle("Admin Dashboard")
        self.setGeometry(0, 0, 255, 600)
        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setWindowIconText("Logo")
        self.setWindowFlags(Qt.FramelessWindowHint)

        mainLayout = QVBoxLayout()

        self.unitsLayout = QVBoxLayout()

        groupBox = QGroupBox()

        j = 0

        for i in self.listOfUnits:
            self.testButton = QPushButton(str(f"{i} {self.listOfLocations[j]}"))

            buttonText = (self.testButton.text()).split()

            buttonText = buttonText[0]

            self.testButton.clicked.connect(lambda checked=None, text=buttonText: self.openUnitDashboard(text))

            self.unitsLayout.addWidget(self.testButton)

            j = j + 1

        groupBox.setLayout(self.unitsLayout)

        self.filterDropdown = QComboBox()
        self.filterDropdown.addItems(self.dropdownLocations)
        self.filterDropdown.currentIndexChanged.connect(self.filterChanged)

        mainLayout.addWidget(self.filterDropdown)

        scrollArea = QScrollArea()
        scrollArea.setWidget(groupBox)
        scrollArea.setWidgetResizable(True)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

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

        logoutButton = QPushButton("Logout")
        logoutButton.clicked.connect(self.closeEvent)
        logoutButton.setStyleSheet("""border-radius: 8px;
        color: white;
        border: 1px solid #202E23;
        background-color: #295231;
        padding: 5px 15px;""")

        mainLayout.addWidget(logoutButton)

        self.setLayout(mainLayout)

        self.setStyleSheet(baseSheet)

    def filterChanged(self, index):

        selectedFilter = self.dropdownLocations[index]

        for i in reversed(range(self.unitsLayout.count())):
            widgetToRemove = self.unitsLayout.itemAt(i).widget()
            self.unitsLayout.removeWidget(widgetToRemove)
            widgetToRemove.deleteLater()

        self.listOfUnits = []
        self.listOfLocations = []

        if selectedFilter == "All Units":

            fetchUnits = SQL.fetchUnitsSunstone()

            for row in fetchUnits:
                altered = list(row)
                self.listOfUnits.append(altered[0])
                self.listOfLocations.append(altered[1])

        else:

            fetchUnits = SQL.fetchFilteredUnitsSunstone(selectedFilter)

            for row in fetchUnits:
                altered = list(row)
                self.listOfUnits.append(altered[0])
                self.listOfLocations.append(altered[1])

        j = 0

        for i in self.listOfUnits:
            self.testButton = QPushButton(str(f"{i} {self.listOfLocations[j]}"))

            buttonText = (self.testButton.text()).split()

            buttonText = buttonText[0]

            self.testButton.clicked.connect(lambda checked=None, text=buttonText: self.openUnitDashboard(text))

            self.unitsLayout.addWidget(self.testButton)

            j = j + 1

    def openUnitDashboard(self, unitName):
        global selectedUnit
        global selectedUnitType
        global selectedIP
        global selectedVictron
        global selectedCCTV
        global selectedEfoyID
        global selectedEfoyID2
        global selectedCamera
        global selectedCompany
        global selectedTextDevice
        global selectedUnitSize


        unitType = SQL.fetchUnitType(unitName).strip()

        if str(unitType) == "ARC" or str(unitType) == "IO":
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
                selectedTextDevice = altered[9]
                selectedUnitSize = altered[10]

        elif str(unitType) == "GEN":
            data = SQL.fetchGenDetails(unitName)
            selectedUnit = unitName
            selectedUnitType = unitType

            for row in data:
                altered = list(row)

                selectedVictron = altered[0]
                selectedCompany = altered[2]
                selectedEfoyID = altered[3]
                selectedEfoyID2 = altered[4]

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

        elif str(unitType) == "GEN":

            pullVictronData(selectedUnit)

            self.openGenDashboard = generatorDashboard()
            self.openGenDashboard.show()

            self.hide()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openGenDashboard.frameGeometry()
            Geo.moveCenter(Center)
            self.openGenDashboard.move(Geo.topLeft())

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

    def closeEvent(self):
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

            for row in fetchUnits:
                altered = list(row)
                self.listOfUnits.append(altered[0])
                self.listOfLocations.append(altered[1])
        else:
            fetchUnits = SQL.fetchUnits(userCompany)

            for row in fetchUnits:
                altered = list(row)
                self.listOfUnits.append(altered[0])
                self.listOfLocations.append(altered[1])

        self.dropdownLocations = list(dict.fromkeys(self.listOfLocations))
        self.dropdownLocations.insert(0, "All Units")

        super().__init__()

        self.setWindowTitle("User Dashboard")
        self.setGeometry(0, 0, 255, 600)
        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setWindowIconText("Logo")
        self.setWindowFlags(Qt.FramelessWindowHint)

        mainLayout = QVBoxLayout()

        self.unitsLayout = QVBoxLayout()

        groupBox = QGroupBox()

        j = 0

        for i in self.listOfUnits:
            self.testButton = QPushButton(str(f"{i} {self.listOfLocations[j]}"))

            buttonText = (self.testButton.text()).split()

            buttonText = buttonText[0]

            self.testButton.clicked.connect(lambda checked=None, text=buttonText: self.openUnitDashboard(text))

            self.unitsLayout.addWidget(self.testButton)

            j = j + 1

        groupBox.setLayout(self.unitsLayout)

        self.filterDropdown = QComboBox()
        self.filterDropdown.addItems(self.dropdownLocations)
        self.filterDropdown.currentIndexChanged.connect(self.filterChanged)

        mainLayout.addWidget(self.filterDropdown)

        scrollArea = QScrollArea()
        scrollArea.setWidget(groupBox)
        scrollArea.setWidgetResizable(True)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        mainLayout.addWidget(scrollArea)

        mapButton = QPushButton("Interactive Map")
        mapButton.clicked.connect(self.openMap)

        mainLayout.addWidget(mapButton)

        victronButton = QPushButton("Victron Overview")
        victronButton.clicked.connect(self.openVictron)

        mainLayout.addWidget(victronButton)

        logoutButton = QPushButton("Logout")
        logoutButton.clicked.connect(self.closeEvent)
        logoutButton.setStyleSheet("""border-radius: 8px;
                color: white;
                border: 1px solid #202E23;
                background-color: #295231;
                padding: 5px 15px;""")

        mainLayout.addWidget(logoutButton)

        self.setLayout(mainLayout)

        self.setStyleSheet(baseSheet)

    def filterChanged(self, index):

        selectedFilter = self.dropdownLocations[index]

        for i in reversed(range(self.unitsLayout.count())):
            widgetToRemove = self.unitsLayout.itemAt(i).widget()
            self.unitsLayout.removeWidget(widgetToRemove)
            widgetToRemove.deleteLater()

        self.listOfUnits = []
        self.listOfLocations = []

        if selectedFilter == "All Units":
            if userCompany == "Sunstone":

                fetchUnits = SQL.fetchUnitsSunstone()

                for row in fetchUnits:
                    altered = list(row)
                    self.listOfUnits.append(altered[0])
                    self.listOfLocations.append(altered[1])
            else:
                fetchUnits = SQL.fetchUnits(userCompany)

                for row in fetchUnits:
                    altered = list(row)
                    self.listOfUnits.append(altered[0])
                    self.listOfLocations.append(altered[1])
        else:
            if userCompany == "Sunstone":
                fetchUnits = SQL.fetchFilteredUnitsSunstone(selectedFilter)

                for row in fetchUnits:
                    altered = list(row)
                    self.listOfUnits.append(altered[0])
                    self.listOfLocations.append(altered[1])
            else:
                fetchUnits = SQL.fetchFilteredUnits(selectedFilter, userCompany)

                for row in fetchUnits:
                    altered = list(row)
                    self.listOfUnits.append(altered[0])
                    self.listOfLocations.append(altered[1])

        j = 0

        for i in self.listOfUnits:
            self.testButton = QPushButton(str(f"{i} {self.listOfLocations[j]}"))

            buttonText = (self.testButton.text()).split()

            buttonText = buttonText[0]

            self.testButton.clicked.connect(lambda checked=None, text=buttonText: self.openUnitDashboard(text))

            self.unitsLayout.addWidget(self.testButton)

            j = j + 1

    def openUnitDashboard(self, unitName):
        global selectedUnit
        global selectedUnitType
        global selectedIP
        global selectedVictron
        global selectedCCTV
        global selectedEfoyID
        global selectedEfoyID2
        global selectedCamera
        global selectedCompany
        global selectedTextDevice
        global selectedUnitSize

        unitType = SQL.fetchUnitType(unitName).strip()

        if str(unitType) == "ARC" or str(unitType) == "IO":
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
                selectedTextDevice = altered[9]
                selectedUnitSize = altered[10]

        elif str(unitType) == "GEN":
            data = SQL.fetchGenDetails(unitName)
            selectedUnit = unitName
            selectedUnitType = unitType

            for row in data:
                altered = list(row)

                selectedVictron = altered[0]
                selectedCompany = altered[2]
                selectedEfoyID = altered[3]
                selectedEfoyID2 = altered[4]

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

        elif str(unitType) == "GEN":

            pullVictronData(selectedUnit)

            self.openGenDashboard = generatorDashboard()
            self.openGenDashboard.show()

            self.hide()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openGenDashboard.frameGeometry()
            Geo.moveCenter(Center)
            self.openGenDashboard.move(Geo.topLeft())

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

    def closeEvent(self):
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
        self.setWindowFlags(Qt.FramelessWindowHint)

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

        self.setStyleSheet("""

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
        combobox-popup: 0;
    }
    QPushButton {
        border-radius: 8px;
        color: white;
        border: 1px solid #202E23;
        background-color: #295231;
        padding: 5px 15px; 

    }
    QPushButton:hover {
        background-color: #295231;
        border: 1px solid #2d683a;
    }
    QSpinBox {
        border: 1px solid #e0e4e7;Jack
        background-color: #c8eacf;
        color: #0e2515;
        padding: 5px 15px; 

    }
    QMainWindow {
        background-color: qlineargradient(x1: 0, x2: 1, stop: 0 #358446, stop: 1 #6FFF63)
    }

""")

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