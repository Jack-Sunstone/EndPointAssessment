import sys
import os
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6 import QtWebEngineWidgets

def resourcePath(relativePath):
    try:
        basePath = sys._MEIPASS
    except Exception:
        basePath = os.path.abspath(".")

    return os.path.join(basePath, relativePath)

logoPath = resourcePath("Assets/Images/sunstone.png")

cameraPath = resourcePath("Assets/Images/CCTV.png")

sunPath = resourcePath("Assets/Images/Sun.png")

batteryPath = resourcePath("Assets/Images/fullBattery.png")

loadPath = resourcePath("Assets/Images/Load.png")

class ioDashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("IO Box Dashboard")
        self.setGeometry(0,0,760,200)

        layout = QGridLayout()

        pixmap = QPixmap(cameraPath)

        self.allCameras = QLabel()
        self.allCameras.setPixmap(pixmap)
        self.allCameras.setAlignment(Qt.AlignmentFlag.AlignCenter)

        allCamerasButton = QPushButton("All Cameras")

        layout.addWidget(self.allCameras, 0, 0)
        layout.addWidget(allCamerasButton,1,0)

        self.Camera1 = QLabel()
        self.Camera1.setPixmap(pixmap)
        self.Camera1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        camera1Button = QPushButton("Camera 1")

        layout.addWidget(self.Camera1, 0, 1)
        layout.addWidget(camera1Button, 1, 1)

        self.Camera2 = QLabel()
        self.Camera2.setPixmap(pixmap)
        self.Camera2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        camera2Button = QPushButton("Camera 2")

        layout.addWidget(self.Camera2, 0, 2)
        layout.addWidget(camera2Button, 1, 2)

        self.Camera3 = QLabel()
        self.Camera3.setPixmap(pixmap)
        self.Camera3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        camera3Button = QPushButton("Camera 3")

        layout.addWidget(self.Camera3, 0, 3)
        layout.addWidget(camera3Button, 1, 3)

        self.Camera4 = QLabel()
        self.Camera4.setPixmap(pixmap)
        self.Camera4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        camera4Button = QPushButton("Camera 4")

        layout.addWidget(self.Camera4, 0, 4)
        layout.addWidget(camera4Button, 1, 4)

        routerButton = QPushButton("Router Webpage")

        layout.addWidget(routerButton,2,1,1,3)

        self.setLayout(layout)

class arcDashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ARC Dashboard")
        self.setGeometry(0,0,760,300)

        layout = QGridLayout()

        sunPixmap = QPixmap(sunPath)
        batteryPixmap = QPixmap(batteryPath)
        loadPixmap = QPixmap(loadPath)
        cameraPixmap = QPixmap(cameraPath)

        self.sunImage = QLabel()
        self.sunImage.setPixmap(sunPixmap)
        self.sunImage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        solarPower = QLabel("Placeholder")
        solarPower.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.sunImage, 0, 0)
        layout.addWidget(solarPower, 0, 1)

        self.batteryImage = QLabel()
        self.batteryImage.setPixmap(batteryPixmap)
        self.batteryImage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        batteryVoltage = QLabel("Placeholder")
        batteryVoltage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.batteryImage, 1, 0)
        layout.addWidget(batteryVoltage, 1, 1)

        self.loadImage = QLabel()
        self.loadImage.setPixmap(loadPixmap)
        self.loadImage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        loadDraw = QLabel("Placeholder")
        loadDraw.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.loadImage, 2, 0)
        layout.addWidget(loadDraw, 2, 1)

        self.allCameras = QLabel()
        self.allCameras.setPixmap(cameraPixmap)
        self.allCameras.setAlignment(Qt.AlignmentFlag.AlignCenter)

        allCamerasButton = QPushButton("All Cameras")

        layout.addWidget(self.allCameras, 3, 0)
        layout.addWidget(allCamerasButton, 4, 0)

        self.Camera1 = QLabel()
        self.Camera1.setPixmap(cameraPixmap)
        self.Camera1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        camera1Button = QPushButton("Camera 1")

        layout.addWidget(self.Camera1, 3, 1)
        layout.addWidget(camera1Button, 4, 1)

        self.Camera2 = QLabel()
        self.Camera2.setPixmap(cameraPixmap)
        self.Camera2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        camera2Button = QPushButton("Camera 2")

        layout.addWidget(self.Camera2, 3, 2)
        layout.addWidget(camera2Button, 4, 2)

        self.Camera3 = QLabel()
        self.Camera3.setPixmap(cameraPixmap)
        self.Camera3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        camera3Button = QPushButton("Camera 3")

        layout.addWidget(self.Camera3, 3, 3)
        layout.addWidget(camera3Button, 4, 3)

        self.Camera4 = QLabel()
        self.Camera4.setPixmap(cameraPixmap)
        self.Camera4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        camera4Button = QPushButton("Camera 4")

        layout.addWidget(self.Camera4, 3, 4)
        layout.addWidget(camera4Button, 4, 4)

        victronButton = QPushButton("Victron Webpage")

        layout.addWidget(victronButton, 5, 1)

        routerButton = QPushButton("Router Webpage")

        layout.addWidget(routerButton, 5, 2)

        efoyButton = QPushButton("Efoy Webpage")

        layout.addWidget(efoyButton, 5, 3)

        self.setLayout(layout)

class unitManagement(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Unit Mangement")
        self.setGeometry(0, 0, 600, 300)

        layout = QGridLayout()

        unitManagementDropdown = QComboBox()
        unitManagementDropdown.setPlaceholderText("Unit Management")

        layout.addWidget(unitManagementDropdown, 0, 0, 1, 4)

        unitName = QLabel("Placeholder")

        layout.addWidget(unitName,1,0)

        locationEdit = QLineEdit()
        locationEdit.setPlaceholderText("Unit Location")

        layout.addWidget(locationEdit, 1, 1)

        companyEdit = QLineEdit()
        companyEdit.setPlaceholderText("Company")

        layout.addWidget(companyEdit, 1, 2)

        numCameras = QLineEdit()
        numCameras.setPlaceholderText("Number of Cameras")

        layout.addWidget(numCameras, 1, 3)

        changeButton = QPushButton("Change Details")

        layout.addWidget(changeButton,2,0,1,2)

        deleteButton = QPushButton("Delete")

        layout.addWidget(deleteButton, 2, 2,1,2)

        addNewUnitLabel = QLabel("--------------- Add New User ---------------")
        addNewUnitLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(addNewUnitLabel, 3, 0, 1, 4)

        unitNameAdd = QLineEdit()
        unitNameAdd.setPlaceholderText("Unit ID")

        layout.addWidget(unitNameAdd,4,0)

        locationAdd = QLineEdit()
        locationAdd.setPlaceholderText("Location")

        layout.addWidget(locationAdd,4,1)

        companyAdd = QLineEdit()
        companyAdd.setPlaceholderText("Company")

        layout.addWidget(companyAdd,4,2)

        numCamerasAdd = QLineEdit()
        numCamerasAdd.setPlaceholderText("Number of Cameras")

        layout.addWidget(numCamerasAdd,4,3)

        voltageAdd = QLineEdit()
        voltageAdd.setPlaceholderText("Unit Voltage")

        layout.addWidget(voltageAdd,5,0)

        routerAdd = QLineEdit()
        routerAdd.setPlaceholderText("Router Type")

        layout.addWidget(routerAdd,5,1)

        victronAdd = QLineEdit()
        victronAdd.setPlaceholderText("Victron Site ID")

        layout.addWidget(victronAdd,5,2)

        addUnit = QPushButton("Add New Unit")

        layout.addWidget(addUnit,6,0,1,4)
        self.setLayout(layout)

    def closeEvent(self, event):
        self.openAdminMenu = adminMenu()
        self.openAdminMenu.show()

        center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        geo = self.openAdminMenu.frameGeometry()
        geo.moveCenter(center)
        self.openAdminMenu.move(geo.topLeft())

        self.hide()

class userManagement(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("User Management")
        self.setGeometry(0,0,300,250)

        layout = QGridLayout()

        userSelection = QComboBox()
        userSelection.setPlaceholderText("User Selection")

        layout.addWidget(userSelection,0,0,1,3)

        usernameLabel = QLabel("PLACEHOLDER")

        layout.addWidget(usernameLabel,1,0.5)

        passwordLineEdit = QLineEdit()
        passwordLineEdit.setPlaceholderText("Password")

        layout.addWidget(passwordLineEdit,1,1,1,2)

        changeButton = QPushButton("Change Details")

        layout.addWidget(changeButton,2,1)

        deleteButton = QPushButton("Delete Unit")

        layout.addWidget(deleteButton,2,2)

        addNewUserLabel = QLabel("--------------- Add New User ---------------")
        addNewUserLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(addNewUserLabel,3,0,1,3)

        usernameEdit = QLineEdit()
        usernameEdit.setPlaceholderText("Username")

        layout.addWidget(usernameEdit,4,0)

        passwordAddLineEdit = QLineEdit()
        passwordAddLineEdit.setPlaceholderText("Password")

        layout.addWidget(passwordAddLineEdit,4,1)

        companyLineEdit = QLineEdit()
        companyLineEdit.setPlaceholderText("Company")

        layout.addWidget(companyLineEdit,4,2)

        addUserButton = QPushButton("Add New User")

        layout.addWidget(addUserButton,5,1)

        self.setLayout(layout)

    def closeEvent(self, event):
        self.openAdminMenu = adminMenu()
        self.openAdminMenu.show()

        center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        geo = self.openAdminMenu.frameGeometry()
        geo.moveCenter(center)
        self.openAdminMenu.move(geo.topLeft())

        self.hide()

class adminMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Admin Menu")
        self.setGeometry(0,0,430,180)

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

        center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        geo = self.openUserManagement.frameGeometry()
        geo.moveCenter(center)
        self.openUserManagement.move(geo.topLeft())

        self.hide()

    def openUnit(self):
        self.openUnitManagement = unitManagement()
        self.openUnitManagement.show()

        center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        geo = self.openUnitManagement.frameGeometry()
        geo.moveCenter(center)
        self.openUnitManagement.move(geo.topLeft())

        self.hide()

    def closeEvent(self, event):
        self.openMonitoring = adminMonitoring()
        self.openMonitoring.show()

        center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        geo = self.openMonitoring.frameGeometry()
        geo.moveCenter(center)
        self.openMonitoring.move(geo.topLeft())

        self.hide()

class interactiveMap(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Interactive Unit Map")
        self.setGeometry(0,0,550,550)

        layout = QGridLayout()

        self.mapBrowser = QtWebEngineWidgets.QWebEngineView(self)
        layout.addWidget(self.mapBrowser, 0, 0)

        self.setLayout(layout)

class adminMonitoring(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Admin Dashboard")
        self.setGeometry(0, 0, 255, 600)

        layout = QVBoxLayout()

        companyTabs = QTabWidget()

        placeholder = QLabel("placeholder")

        companyTabs.addTab(placeholder, "Company")

        layout.addWidget(companyTabs)

        mapButton = QPushButton("Interactive Map")
        mapButton.clicked.connect(self.openMap)

        layout.addWidget(mapButton)

        adminButton = QPushButton("Admin Menu")
        adminButton.clicked.connect(self.openAdmin)

        layout.addWidget(adminButton)

        self.setLayout(layout)

    def openMap(self):
        self.openMapPage = interactiveMap()
        self.openMapPage.show()

        center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        geo = self.openMapPage.frameGeometry()
        geo.moveCenter(center)
        self.openMapPage.move(geo.topLeft())

    def openAdmin(self):
        self.openAdminMenu = adminMenu()
        self.openAdminMenu.show()

        center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        geo = self.openAdminMenu.frameGeometry()
        geo.moveCenter(center)
        self.openAdminMenu.move(geo.topLeft())

        self.hide()

class userMonitoring(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dashboard")
        self.setGeometry(0,0,255,600)

        layout = QVBoxLayout()

        companyTabs = QTabWidget()

        placeholder = QLabel("placeholder")

        companyTabs.addTab(placeholder,"Company")

        layout.addWidget(companyTabs)

        mapButton = QPushButton("Interactive Map")
        mapButton.clicked.connect(self.openMap)

        layout.addWidget(mapButton)

        self.setLayout(layout)

    def openMap(self):
        self.openMapPage = interactiveMap()
        self.openMapPage.show()

        center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        geo = self.openMapPage.frameGeometry()
        geo.moveCenter(center)
        self.openMapPage.move(geo.topLeft())


class loginUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dashboard Login")
        self.setGeometry(0,0,380,320)

        layout = QGridLayout()

        self.Logo = QLabel()
        pixmap = QPixmap(logoPath)
        self.Logo.setPixmap(pixmap)
        self.Logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.Logo, 0,0)


        usernameEntry = QLineEdit()
        usernameEntry.setPlaceholderText("Username")

        layout.addWidget(usernameEntry, 4, 0)

        passwordEntry = QLineEdit()
        passwordEntry.setPlaceholderText("Password")

        layout.addWidget(passwordEntry, 5, 0)

        loginButton = QPushButton("Login")
        loginButton.clicked.connnect(self.openMonitoring)
        layout.addWidget(loginButton, 6,0)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


    def openMonitoring(self):
        userRights = "ADMIN"
        if "ADMIN" in userRights:
            self.adminMonitoring = adminMonitoring()
            self.adminMonitoring.show()

            center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            geo = self.adminMonitoring.frameGeometry()
            geo.moveCenter(center)
            self.adminMonitoring.move(geo.topLeft())

            self.hide()
        elif "USER" in userRights:
            self.userMonitoring = adminMonitoring()
            self.userMonitoring.show()

            center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
            geo = self.userMonitoring.frameGeometry()
            geo.moveCenter(center)
            self.userMonitoring.move(geo.topLeft())

            self.hide()

app = QApplication([])
app.setStyle('GTK')
window = loginUI()

window.show()

center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
geo = window.frameGeometry()
geo.moveCenter(center)
window.move(geo.topLeft())

sys.exit(app.exec())