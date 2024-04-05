import sys
import os
import webbrowser
import cv2
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6 import QtWebEngineWidgets
import SQL
import requests
import json
import threading
import socket
import plotly.graph_objects as go

selectedUnit = ""
selectedIP = ""
selectedVictron = ""
selectedCompany = ""
selectedCCTV = ""
selectedUnitType = ""
selectedCamera = ""
selectedEfoyID = ""

userRights = ""

unitSolar = ""
formattedSolar = ""
unitVoltage = ""
unitLoad = ""
formattedLoad = ""

sunstonePassword = "(10GIN$t0n3)"
wjPassword = "12Sunstone34"

mapboxAccessToken = open(".mapbox_token").read()

def axisPath(password,IPaddress, cameraNumber):

    Axis = f"rtsp://root:{password}@{IPaddress}:{cameraNumber}554/axis-media/media.amp"

    return Axis

def hikPath(IPaddress, cameraNumber):

    Hik = f"rtsp://admin:(10GIN$t0n3)@{IPaddress}:{cameraNumber}554/Streaming/Channels/102/?transportmode=unicast"

    return Hik

def hanwhaPath(password, IPaddress, cameraNumber):

    Hanwha = f"rtsp://admin:{password}@{IPaddress}:{cameraNumber}554/profile2/media.smp"

    return Hanwha

def cameraOne(cap):
    cap = cv2.VideoCapture(str(cap))
    if cap is None or not cap.isOpened():
        print("Camera Not Available")
    else:
        while (True):
            ret, Cam1 = cap.read()
            cv2.imshow("Camera Live View", Cam1)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

def threading1Camera(cameraURL):
    thread1 = threading.Thread(target=cameraOne, args=(cameraURL,))
    thread1.start()
    thread1.join()
    cv2.destroyAllWindows()

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

def getVictronValues():

    global unitSolar
    global unitVoltage
    global unitLoad
    global formattedLoad
    global formattedSolar

    # Defining login details to access Sites
    login_url = 'https://vrmapi.victronenergy.com/v2/auth/login'
    login_string = '{"username":"support@sunstone-systems.com","password":"12Security34!"}'
    # Stores and loads Json request to the login URL
    response = requests.post(login_url, login_string)
    token = json.loads(response.text).get("token")
    headers = {"X-Authorization": 'Bearer ' + token}

    diags_url = "https://vrmapi.victronenergy.com/v2/installations/{}/diagnostics?count=1000".format(selectedVictron)
    response = requests.get(diags_url, headers=headers)
    data = response.json().get("records")

    unitSolar = str([element['rawValue'] for element in data if element['code'] == "PVP"][0])
    formattedSolar = str([element['formattedValue'] for element in data if element['code'] == "PVP"][0])

    unitVoltage = str([element['rawValue'] for element in data if element['code'] == "bv"][0])

    unitLoad = str([element['rawValue'] for element in data if element['code'] == "dc"][0])
    formattedLoad = str([element['formattedValue'] for element in data if element['code'] == "dc"][0])

class ioDashboard(QWidget):
    def __init__(self):

        ioBoxIcon = resourcePath("Assets/Images/IOBox.png")
        cameraPath = resourcePath("Assets/Images/CCTV.png")

        super().__init__()

        self.setWindowTitle("IO Box Dashboard")
        self.setGeometry(0,0,760,200)
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

            layout.addWidget(self.errorMessage,4, 0)

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

    def viewIndividualCamera(self, cameraNumber):
        if selectedCamera == "Axis":
            if selectedCompany == "WJ":
                cameraURL = axisPath(wjPassword, selectedIP, cameraNumber)
                threading1Camera(str(cameraURL))
            else:
                cameraURL = axisPath(sunstonePassword, selectedIP, cameraNumber)
                threading1Camera(cameraURL)
        elif selectedCamera == "Hik":
            cameraURL = hikPath(selectedIP, cameraNumber)
            threading1Camera(cameraURL)
        elif selectedCamera == "Hanwha":
            if selectedCompany == "WJ":
                cameraURL = hanwhaPath(wjPassword, selectedIP, cameraNumber)
                threading1Camera(cameraURL)
            else:
                cameraURL = hanwhaPath(sunstonePassword, selectedIP, cameraNumber)
                threading1Camera(cameraURL)

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
        if userRights == "ADMIN":
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

        unitVoltage = float(unitVoltage)
        unitLoad = float(unitLoad)
        unitSolar = float(unitSolar)

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
        self.setGeometry(0,0,600,300)
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

        self.solarPower = QLabel(formattedSolar)


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

        self.loadDraw = QLabel(formattedLoad)

        layout.addWidget(self.loadImage, 3, 0)
        layout.addWidget(self.loadDraw, 3, 1)

        self.allCameras = QLabel()
        self.allCameras.setPixmap(cameraPixmap)
        self.allCameras.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.allCamerasButton = QPushButton("All Cameras")

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

            layout.addWidget(self.Camera1, 4,0)
            layout.addWidget(self.camera1Button,5, 0)

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
            layout.addWidget(self.allCamerasButton,5, 0)

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

        self.checkUnitStatus()

        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateData)
        self.timer.start(30000)

    def viewIndividualCamera(self, cameraNumber):
        if selectedCamera == "Axis":
            if selectedCompany == "WJ":
                cameraURL = axisPath(wjPassword, selectedIP, cameraNumber)
                threading1Camera(str(cameraURL))
            else:
                cameraURL = axisPath(sunstonePassword, selectedIP, cameraNumber)
                threading1Camera(cameraURL)
        elif selectedCamera == "Hik":
            cameraURL = hikPath(selectedIP, cameraNumber)
            threading1Camera(cameraURL)
        elif selectedCamera == "Hanwha":
            if selectedCompany == "WJ":
                cameraURL = hanwhaPath(wjPassword, selectedIP, cameraNumber)
                threading1Camera(cameraURL)
            else:
                cameraURL = hanwhaPath(sunstonePassword, selectedIP, cameraNumber)
                threading1Camera(cameraURL)

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
        global formattedLoad
        global formattedSolar

        getVictronValues()

        unitVoltage = float(unitVoltage)
        unitLoad = float(unitLoad)
        unitSolar = float(unitSolar)

        self.batteryVoltage.setText(str(unitVoltage) + " V")
        self.loadDraw.setText(formattedLoad)
        self.solarPower.setText(formattedSolar)

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
        if userRights == "ADMIN":
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

class unitManagement(QWidget):
    def __init__(self):

        sunstoneIcon = resourcePath("Assets/Images/SunstoneLogo.png")

        self.listOfUnits = []

        fetchUnits = SQL.fetchUnits()
        for item in fetchUnits:
            self.listOfUnits.append(item)

        #Current Selected Unit
        self.selectedUnit = ""
        self.selectedLocation = ""
        self.selectedCompany = ""
        self.selectedCameras = ""

        #Add new Unit
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

        super().__init__()

        self.setWindowTitle("Unit Mangement")
        self.setGeometry(0, 0, 650, 300)
        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setWindowIconText("Logo")

        layout = QGridLayout()

        unitManagementDropdown = QComboBox()
        unitManagementDropdown.addItems(self.listOfUnits)
        unitManagementDropdown.setPlaceholderText("Unit Management")
        unitManagementDropdown.currentIndexChanged.connect(self.unitChanged)

        layout.addWidget(unitManagementDropdown, 0, 0, 1, 4)

        self.unitName = QLabel("Placeholder")

        layout.addWidget(self.unitName,1,0)

        self.locationEdit = QLineEdit()
        self.locationEdit.setPlaceholderText("Location")
        self.locationEdit.textChanged.connect(self.getUpdatedLocation)

        layout.addWidget(self.locationEdit, 1, 1)

        self.companyEdit = QLineEdit()
        self.companyEdit.setPlaceholderText("Company")
        self.companyEdit.textChanged.connect(self.getUpdatedCompany)

        layout.addWidget(self.companyEdit, 1, 2)

        self.numCameras = QLineEdit()
        self.numCameras.setPlaceholderText("Number of Cameras")
        self.numCameras.textChanged.connect(self.getUpdatedNumCCTV)

        layout.addWidget(self.numCameras, 1, 3)

        changeButton = QPushButton("Change Details")
        changeButton.clicked.connect(self.changeUnit)

        layout.addWidget(changeButton,2,0,1,2)

        deleteButton = QPushButton("Delete")

        layout.addWidget(deleteButton, 2, 2,1,2)

        addNewUnitLabel = QLabel("--------------- Add New Unit ---------------")
        addNewUnitLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(addNewUnitLabel, 3, 0, 1, 4)

        self.unitNameAdd = QLineEdit()
        self.unitNameAdd.setPlaceholderText("Unit ID")
        self.unitNameAdd.textChanged.connect(self.getNewUnitName)

        layout.addWidget(self.unitNameAdd,4,0)

        self.locationAdd = QLineEdit()
        self.locationAdd.setPlaceholderText("Location")
        self.locationAdd.textChanged.connect(self.getNewLocation)

        layout.addWidget(self.locationAdd,4,1)

        self.companyAdd = QLineEdit()
        self.companyAdd.setPlaceholderText("Company")
        self.companyAdd.textChanged.connect(self.getNewCompany)

        layout.addWidget(self.companyAdd,4,2)

        self.numCamerasAdd = QLineEdit()
        self.numCamerasAdd.setPlaceholderText("Number of Cameras")
        self.numCamerasAdd.textChanged.connect(self.getNewNumCCTV)

        layout.addWidget(self.numCamerasAdd,4,3)

        self.cameratypeAdd = QLineEdit()
        self.cameratypeAdd.setPlaceholderText("Camera Manufacturer")
        self.cameratypeAdd.textChanged.connect(self.getCameraType)

        layout.addWidget(self.cameratypeAdd, 5, 0)

        self.IPAdd = QLineEdit()
        self.IPAdd.setPlaceholderText("IP Address")
        self.IPAdd.textChanged.connect(self.getNewIP)

        layout.addWidget(self.IPAdd,5,1)

        unitType = QComboBox()
        unitType.setPlaceholderText("Unit Type")
        unitType.addItems(["ARC","IO"])
        unitType.currentIndexChanged.connect(self.getNewUnitType)

        layout.addWidget(unitType,5,2)

        self.victronAdd = QLineEdit()
        self.victronAdd.setPlaceholderText("Victron Site ID")
        self.victronAdd.textChanged.connect(self.getNewVictronID)

        layout.addWidget(self.victronAdd,5,3)

        self.efoyAdd = QLineEdit()
        self.efoyAdd.setPlaceholderText("Efoy ID")
        self.efoyAdd.textChanged.connect(self.getNewEfoy)

        layout.addWidget(self.efoyAdd,6,0)

        self.latAdd = QLineEdit("")
        self.latAdd.setPlaceholderText("Latitude")
        self.latAdd.textChanged.connect(self.getNewLat)

        layout.addWidget(self.latAdd,6,1)

        self.lonAdd = QLineEdit("")
        self.lonAdd.setPlaceholderText("Longitude")
        self.lonAdd.textChanged.connect(self.getNewLon)

        layout.addWidget(self.lonAdd,6,2)

        addUnit = QPushButton("Add New Unit")
        addUnit.clicked.connect(self.addNewUnit)

        layout.addWidget(addUnit,7,0,1,4)

        self.errorMessage = QLabel("")
        self.errorMessage.setStyleSheet("color: red")
        self.errorMessage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.errorMessage, 8, 1, 1, 2)

        self.setLayout(layout)

    def getUpdatedLocation(self, Location):
        self.selectedLocation = Location

    def getUpdatedCompany(self, Company):
        self.selectedCompany = Company

    def getUpdatedNumCCTV(self, CCTV):
        self.selectedCameras = CCTV

    def getNewUnitName(self,Name):
        self.newUnitName = Name

    def getNewLocation(self, Location):
        self.newLocation = Location

    def getNewCompany(self, Company):
        self.newCompany = Company

    def getNewNumCCTV(self, Number):
        self.NoCCTV = Number

    def getCameraType(self, Type):
        self.newCameraType = Type

    def getNewIP(self,IPADDRESS):
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

    def getNewVictronID(self,ID):
        self.newVictronID = ID

    def getNewEfoy(self, EFOY):
        self.newEfoy = EFOY

    def getNewLat(self,Lat):
        self.newLat = Lat

    def getNewLon(self,Lon):
        self.newLon = Lon

    def unitChanged(self, index):

        self.selectedUnit = self.listOfUnits[index]

        data = SQL.fetchUnitDetails(self.selectedUnit)

        for row in data:
            altered = list(row)
            self.selectedLocation = altered[2]
            self.selectedCompany = altered[3]
            self.selectedCameras = str(altered[4])

        self.unitName.setText(self.selectedUnit)
        self.locationEdit.setText(self.selectedLocation)
        self.companyEdit.setText(self.selectedCompany)
        self.numCameras.setText(self.selectedCameras)

    def changeUnit(self):

        SQL.updateunit(self.selectedUnit, self.selectedLocation, self.selectedCompany, self.selectedCameras)
        self.errorMessage.setText("Unit Updated")

    def deleteUnit(self):
        SQL.deleteUnits(self.selectedUnit)
        self.errorMessage.setText("Unit Deleted")

    def addNewUnit(self):
        checkUnit = SQL.checkUnit(self.newUnitName)

        if checkUnit is None:

            if not [x for x in (self.newUnitName, self.newIP, self.newLocation, self.NoCCTV, self.newCompany, self.newLat, self.newLon, self.newUnitType, self.newCameraType) if x == ""]:
                SQL.addUnits(self.newUnitName,self.newIP, self.newVictronID, self.newLocation, self.NoCCTV, self.newCompany, self.newLat, self.newLon, self.newUnitType, self.newCameraType, self.newEfoy)
                self.errorMessage.setText("Unit Added")
                self.unitNameAdd.setText("")
                self.locationAdd.setText("")
                self.companyAdd.setText("")
                self. numCamerasAdd.setText("")
                self.cameratypeAdd.setText("")
                self.IPAdd.setText("")
                self.victronAdd.setText("")
                self.efoyAdd.setText("")
                self.latAdd.setText("")
                self.lonAdd.setText("")
            else:
                self.errorMessage.setText("One or All Field Is Empty")
        else:

            self.errorMessage.setText("Unit already in database")

    def closeEvent(self, event):
        self.openAdminMenu = adminMenu()
        self.openAdminMenu.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.openAdminMenu.frameGeometry()
        Geo.moveCenter(Center)
        self.openAdminMenu.move(Geo.topLeft())

        self.hide()

class userManagement(QWidget):
    def __init__(self):

        sunstoneIcon = resourcePath("Assets/Images/SunstoneLogo.png")

        self.listOfUsers = []

        fetchUsers = SQL.fetchUsers()

        for item in fetchUsers:
            self.listOfUsers.append(item)

        #Current Selected User
        self.selectedUser = ""
        self.selectedPassword = ""

        #New User
        self.newUsername = ""
        self.newPassword = ""
        self.newCompany = ""

        super().__init__()

        self.setWindowTitle("User Management")
        self.setGeometry(0,0,350,250)
        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setWindowIconText("Logo")

        layout = QGridLayout()

        self.userSelection = QComboBox()
        self.userSelection.addItems(self.listOfUsers)
        self.userSelection.setPlaceholderText("User Selection")
        self.userSelection.currentIndexChanged.connect(self.userChanged)

        layout.addWidget(self.userSelection,0,0,1,3)

        self.usernameLabel = QLabel("")

        layout.addWidget(self.usernameLabel,1,0.5)

        self.passwordLineEdit = QLineEdit()
        self.passwordLineEdit.setPlaceholderText("Password")
        self.passwordLineEdit.textChanged.connect(self.getPasswordChanged)

        layout.addWidget(self.passwordLineEdit,1,1,1,2)

        changeButton = QPushButton("Change Details")
        changeButton.clicked.connect(self.changeUser)

        layout.addWidget(changeButton,2,1)

        deleteButton = QPushButton("Delete")
        deleteButton.clicked.connect(self.deleteUser)

        layout.addWidget(deleteButton,2,2)

        addNewUserLabel = QLabel("--------------- Add New User ---------------")
        addNewUserLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(addNewUserLabel,3,0,1,3)

        self.usernameEdit = QLineEdit()
        self.usernameEdit.setPlaceholderText("Username")
        self.usernameEdit.textChanged.connect(self.getNewUsername)

        layout.addWidget(self.usernameEdit,4,0)

        self.passwordAddLineEdit = QLineEdit()
        self.passwordAddLineEdit.setPlaceholderText("Password")
        self. passwordAddLineEdit.textChanged.connect(self.getNewPassword)

        layout.addWidget(self.passwordAddLineEdit,4,1)

        self.companyLineEdit = QLineEdit()
        self.companyLineEdit.setPlaceholderText("Company")
        self.companyLineEdit.textChanged.connect(self.getNewCompany)

        layout.addWidget(self.companyLineEdit,4,2)

        addUserButton = QPushButton("Add New User")
        addUserButton.clicked.connect(self.addUser)

        layout.addWidget(addUserButton,5,1)

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

        self.usernameLabel.setText(self.selectedUser)
        self.passwordLineEdit.setText(self.selectedPassword)

    def changeUser(self):
        SQL.updateUser(self.selectedPassword, self.selectedUser)
        self.errorMessage.setText("User Updated")

    def deleteUser(self):

        SQL.deleteUsers(self.selectedUser)
        self.errorMessage.setText("User Deleted")

    def addUser(self):
        checkUsername = SQL.checkUsername(self.newUsername)

        if checkUsername is None:
            if not [x for x in (self.newUsername, self.newPassword, self.newCompany) if x == ""]:
                self.errorMessage.setText("User Added")
                SQL.addUsers(self.newUsername, self.newPassword, self.newCompany)
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

        self.setLayout(layout)

    def openUser(self):
        self.openUserManagement = userManagement()
        self.openUserManagement.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.openUserManagement.frameGeometry()
        Geo.moveCenter(Center)
        self.openUserManagement.move(Geo.topLeft())

        self.hide()

    def openUnit(self):
        self.openUnitManagement = unitManagement()
        self.openUnitManagement.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.openUnitManagement.frameGeometry()
        Geo.moveCenter(Center)
        self.openUnitManagement.move(Geo.topLeft())

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
        self.setGeometry(0,0,550,550)
        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setWindowIconText("Logo")

        layout = QGridLayout()

        self.mapBrowser = QtWebEngineWidgets.QWebEngineView(self)
        layout.addWidget(self.mapBrowser, 0, 0)

        self.setLayout(layout)

    def importMap(self):
        names = []

        lat = []

        lon = []

        data = SQL.fetchLocations()

        for row in data:
            altered = list(row)
            names.append(altered[0])
            lat.append(altered[1])
            lon.append(altered[2])


class adminMonitoring(QWidget):
    def __init__(self):

        sunstoneIcon = resourcePath("Assets/Images/SunstoneLogo.png")

        self.listOfUnits = []
        self.listOfCompanies = []

        fetchUnits = SQL.fetchUnits()
        for item in fetchUnits:
            self.listOfUnits.append(item)

        fetchCompanies = SQL.fetchCompanies()
        for item in fetchCompanies:
            self.listOfCompanies.append(item)

        self.listOfCompanies = list(dict.fromkeys(self.listOfCompanies))

        super().__init__()

        self.setWindowTitle("Admin Dashboard")
        self.setGeometry(0, 0, 255, 600)
        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setWindowIconText("Logo")

        mainLayout = QVBoxLayout()

        unitsLayout = QVBoxLayout()

        groupBox = QGroupBox()

        for i in self.listOfUnits:

            self.testButton = QPushButton(str(i))

            buttonText = self.testButton.text()

            self.testButton.clicked.connect(lambda checked=None, text=buttonText: self.openUnitDashboard(text))

            unitsLayout.addWidget(self.testButton)

        groupBox.setLayout(unitsLayout)

        scrollArea = QScrollArea()
        scrollArea.setWidget(groupBox)
        scrollArea.setWidgetResizable(True)

        mainLayout.addWidget(scrollArea)

        mapButton = QPushButton("Interactive Map")
        mapButton.clicked.connect(self.openMap)

        mainLayout.addWidget(mapButton)

        adminButton = QPushButton("Admin Menu")
        adminButton.clicked.connect(self.openAdmin)

        mainLayout.addWidget(adminButton)

        self.setLayout(mainLayout)

    def openUnitDashboard(self,unitName):
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
            getVictronValues()

            self.openARCDashboard = arcDashboard()
            self.openARCDashboard.show()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openARCDashboard.frameGeometry()
            Geo.moveCenter(Center)
            self.openARCDashboard.move(Geo.topLeft())

            self.hide()
        elif str(unitType) == "IO":
            self.openIODashboard = ioDashboard()
            self.openIODashboard.show()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openIODashboard.frameGeometry()
            Geo.moveCenter(Center)
            self.openIODashboard.move(Geo.topLeft())

            self.hide()

    def openMap(self):
        self.openMapPage = interactiveMap()
        self.openMapPage.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.openMapPage.frameGeometry()
        Geo.moveCenter(Center)
        self.openMapPage.move(Geo.topLeft())

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
        self.listOfCompanies = []

        fetchUnits = SQL.fetchUnits()
        for item in fetchUnits:
            self.listOfUnits.append(item)

        fetchCompanies = SQL.fetchCompanies()
        for item in fetchCompanies:
            self.listOfCompanies.append(item)

        self.listOfCompanies = list(dict.fromkeys(self.listOfCompanies))

        super().__init__()

        self.setWindowTitle("User Dashboard")
        self.setGeometry(0, 0, 255, 600)
        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setWindowIconText("Logo")

        mainLayout = QVBoxLayout()

        unitsLayout = QVBoxLayout()

        groupBox = QGroupBox()

        for i in self.listOfUnits:
            self.testButton = QPushButton(str(i))

            buttonText = self.testButton.text()

            self.testButton.clicked.connect(lambda checked=None, text=buttonText: self.openUnitDashboard(text))

            unitsLayout.addWidget(self.testButton)

        groupBox.setLayout(unitsLayout)

        scrollArea = QScrollArea()
        scrollArea.setWidget(groupBox)
        scrollArea.setWidgetResizable(True)

        mainLayout.addWidget(scrollArea)

        self.setLayout(mainLayout)

    def openUnitDashboard(self,unitName):
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
            getVictronValues()

            self.openARCDashboard = arcDashboard()
            self.openARCDashboard.show()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openARCDashboard.frameGeometry()
            Geo.moveCenter(Center)
            self.openARCDashboard.move(Geo.topLeft())

            self.hide()
        elif str(unitType) == "IO":
            self.openIODashboard = ioDashboard()
            self.openIODashboard.show()

            Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            Geo = self.openIODashboard.frameGeometry()
            Geo.moveCenter(Center)
            self.openIODashboard.move(Geo.topLeft())

            self.hide()

    def openMap(self):
        self.openMapPage = interactiveMap()
        self.openMapPage.show()

        Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        Geo = self.openMapPage.frameGeometry()
        Geo.moveCenter(Center)
        self.openMapPage.move(Geo.topLeft())

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
        self.setGeometry(0,0,380,320)
        self.setWindowIcon(QIcon(sunstoneIcon))
        self.setWindowIconText("Logo")

        layout = QGridLayout()

        self.Logo = QLabel()
        pixmap = QPixmap(logoPath)
        self.Logo.setPixmap(pixmap)
        self.Logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.Logo, 0,0)


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
        layout.addWidget(loginButton, 6,0)

        self.errorMessage = QLabel("WRONG USERNAME OR PASSWORD")
        self.errorMessage.setStyleSheet("color: red")
        self.errorMessage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.errorMessage,7,0)

        self.errorMessage.hide()

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def getUser(self, Username):
        global username
        self.username = Username
        self.errorMessage.hide()

    def getPassword(self, Password):
        global password
        self.password = Password
        self.errorMessage.hide()


    def openMonitoring(self):

        global userRights

        checkUsername = SQL.checkUsername(self.username)

        if checkUsername is None:
            self.errorMessage.show()

        else:
            checkPassword = SQL.fetchPassword(self.username)

            loggedIn = self.password == checkPassword.strip()


            if loggedIn:
                userRights = SQL.fetchRights(self.username)
                if "ADMIN" in userRights:
                    self.adminMonitoring = adminMonitoring()
                    self.adminMonitoring.show()

                    Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
                    Geo = self.adminMonitoring.frameGeometry()
                    Geo.moveCenter(Center)
                    self.adminMonitoring.move(Geo.topLeft())

                    self.hide()
                elif "USER" in userRights:
                    self.userMonitoring = userMonitoring()
                    self.userMonitoring.show()

                    Center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
                    Geo = self.userMonitoring.frameGeometry()
                    Geo.moveCenter(Center)
                    self.userMonitoring.move(geo.topLeft())

                    self.hide()
            else:
                self.errorMessage.show()

app = QApplication([])
app.setStyle('Fusion')
window = loginUI()

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
""")

window.show()

center = QScreen.availableGeometry(QApplication.primaryScreen()).center()

geo = window.frameGeometry()
geo.moveCenter(center)
window.move(geo.topLeft())

sys.exit(app.exec())