import sys
import os
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *

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
        self.setGeometry(0,0,600,680)

class userManagement(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("User Management")
        self.setGeometry(0,0,650,580)

        layout = QGridLayout()

        userSelection = QComboBox()

        layout.addWidget(userSelection,0,0)

        usernameLabel = QLabel("PLACEHOLDER")

        layout.addWidget(usernameLabel,1,0)

        passwordLineEdit = QLineEdit()
        passwordLineEdit.setPlaceholderText("Password")

        layout.addWidget(passwordLineEdit,1,1)

        changeButton = QPushButton("Change Details")

        layout.addWidget(changeButton,2,0)

        deleteButton = QPushButton("Delete Unit")

        layout.addWidget(deleteButton,2,1)

        usernameEdit = QLineEdit()

        layout.addWidget(usernameEdit,3,0)

        passwordAddLineEdit = QLineEdit()

        layout.addWidget(passwordAddLineEdit,3,1)

        companyLineEdit = QLineEdit()

        layout.addWidget(companyLineEdit,3,2)

        addUserButton = QPushButton("Add New User")

        layout.addWidget(addUserButton,4,0)

        self.setLayout(layout)

class adminMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Admin Menu")
        self.setGeometry(0,0,430,180)

        layout = QVBoxLayout()

        userManagementButton = QPushButton("User Management")

        layout.addWidget(userManagementButton)

        unitManagementButton = QPushButton("Unit Management")

        layout.addWidget(unitManagementButton)

        self.setLayout(layout)

class interactiveMap(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Interactive Unit Map")
        self.setGeometry(0,0,550,550)

class adminMonitoring(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        companyTabs = QTabWidget()

        placeholder = QLabel("placeholder")

        companyTabs.addTab(placeholder, "Company")

        layout.addWidget(companyTabs)

        mapButton = QPushButton("Interactive Map")

        layout.addWidget(mapButton)

        adminButton = QPushButton("Admin Menu")

        layout.addWidget(adminButton)

        self.setWindowTitle("Admin Dashboard")
        self.setGeometry(0,0,255,600)

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

        layout.addWidget(mapButton)

        self.setLayout(layout)

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

        layout.addWidget(loginButton, 6,0)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.monitor = arcDashboard()
        self.monitor.show()

app = QApplication([])
app.setStyle('GTK')
window = loginUI()

window.show()

center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
geo = window.frameGeometry()
geo.moveCenter(center)
window.move(geo.topLeft())

sys.exit(app.exec())