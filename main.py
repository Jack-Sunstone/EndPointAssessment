import sys
import os
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6 import QtWebEngineWidgets
import SQL

username =  ""
password =  ""

listOfUnits = []

fetchUnits = SQL.fetchUnits()
for item in fetchUnits:
   listOfUnits.append(item)

listOfUsers = []

fetchUsers = SQL.fetchUsers()

for item in fetchUsers:
   listOfUsers.append(item)

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

        #Current Selected Unit
        self.selectedUnit = ""
        self.selectedLocation = ""
        self.selectedCompany = ""
        self.selectedCameras = ""

        #Add new Unit
        self.newUnitName = ""
        self.newIP = ""
        self.newVictronID = ""
        self.newLocation = ""
        self.NoCCTV = ""
        self.newCompany = ""
        self.newLat = ""
        self.newLon = ""
        self.newUnitType = ""

        super().__init__()

        self.setWindowTitle("Unit Mangement")
        self.setGeometry(0, 0, 650, 300)

        layout = QGridLayout()

        unitManagementDropdown = QComboBox()
        unitManagementDropdown.addItems(listOfUnits)
        unitManagementDropdown.setPlaceholderText("Unit Management")
        unitManagementDropdown.currentIndexChanged.connect(self.unitChanged)

        layout.addWidget(unitManagementDropdown, 0, 0, 1, 4)

        self.unitName = QLabel("Placeholder")

        layout.addWidget(self.unitName,1,0)

        self.locationEdit = QLineEdit()
        self.locationEdit.setPlaceholderText("Location")

        layout.addWidget(self.locationEdit, 1, 1)

        self.companyEdit = QLineEdit()
        self.companyEdit.setPlaceholderText("Company")

        layout.addWidget(self.companyEdit, 1, 2)

        self.numCameras = QLineEdit()
        self.numCameras.setPlaceholderText("Number of Cameras")

        layout.addWidget(self.numCameras, 1, 3)

        changeButton = QPushButton("Change Details")

        layout.addWidget(changeButton,2,0,1,2)

        deleteButton = QPushButton("Delete")

        layout.addWidget(deleteButton, 2, 2,1,2)

        addNewUnitLabel = QLabel("--------------- Add New Unit ---------------")
        addNewUnitLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(addNewUnitLabel, 3, 0, 1, 4)

        self.unitNameAdd = QLineEdit()
        self.unitNameAdd.setPlaceholderText("Unit ID")
        self.unitNameAdd.textChanged.connect(self.getUnitName)

        layout.addWidget(self.unitNameAdd,4,0)

        self.locationAdd = QLineEdit()
        self.locationAdd.setPlaceholderText("Location")
        self.locationAdd.textChanged.connect(self.getLocation)

        layout.addWidget(self.locationAdd,4,1)

        self.companyAdd = QLineEdit()
        self.companyAdd.setPlaceholderText("Company")
        self.companyAdd.textChanged.connect(self.getCompany)

        layout.addWidget(self.companyAdd,4,2)

        self.numCamerasAdd = QLineEdit()
        self.numCamerasAdd.setPlaceholderText("Number of Cameras")
        self.numCamerasAdd.textChanged.connect(self.getNumCCTV)

        layout.addWidget(self.numCamerasAdd,4,3)

        self.IPAdd = QLineEdit()
        self.IPAdd.setPlaceholderText("IP Address")
        self.IPAdd.textChanged.connect(self.getIP)

        layout.addWidget(self.IPAdd,5,0)

        unitType = QComboBox()
        unitType.setPlaceholderText("Unit Type")
        unitType.addItems(["ARC","IO"])
        unitType.currentIndexChanged.connect(self.getUnitType)

        layout.addWidget(unitType,5,1)

        self.victronAdd = QLineEdit()
        self.victronAdd.setPlaceholderText("Victron Site ID")
        self.victronAdd.textChanged.connect(self.getVictronID)

        layout.addWidget(self.victronAdd,5,2)

        self.latAdd = QLineEdit("")
        self.latAdd.setPlaceholderText("Latitude")
        self.latAdd.textChanged.connect(self.getLat)

        layout.addWidget(self.latAdd,6,0)

        self.lonAdd = QLineEdit("")
        self.lonAdd.setPlaceholderText("Longitude")
        self.lonAdd.textChanged.connect(self.getLon)

        layout.addWidget(self.lonAdd,6,1)

        addUnit = QPushButton("Add New Unit")
        addUnit.clicked.connect(self.addNewUnit)

        layout.addWidget(addUnit,7,0,1,4)

        self.errorMessage = QLabel("")
        self.errorMessage.setStyleSheet("color: red")
        self.errorMessage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.errorMessage, 8, 1, 1, 2)

        self.setLayout(layout)

    def getUnitName(self,Name):
        self.newUnitName = Name

    def getLocation(self, Location):
        self.newLocation = Location

    def getCompany(self, Company):
        self.newCompany = Company

    def getNumCCTV(self, Number):
        self.NoCCTV = Number

    def getIP(self,IPADDRESS):
        self.newIP = IPADDRESS

    def getUnitType(self, unitIndex):
        if unitIndex == 0:
            self.newUnitType = "ARC"
            self.victronAdd.show()
        elif unitIndex == 1:
            self.newUnitType = "IO"
            self.victronAdd.hide()

    def getVictronID(self,ID):
        self.newVictronID = ID

    def getLat(self,Lat):
        self.newLat = Lat

    def getLon(self,Lon):
        self.newLon = Lon

    def unitChanged(self, index):

        self.selectedUnit = listOfUnits[index]

        data = SQL.fetchUnitDetails(self.selectedUnit)

        for row in data:
            altered = list(row)
            self.selectedLocation = altered[0]
            self.selectedCompany = altered[1]
            self.selectedCameras = altered[2]

    

    def addNewUnit(self):
        if not [x for x in (self.newUnitName, self.newIP, self.newLocation, self.NoCCTV, self.newCompany, self.newLat, self.newLon, self.newUnitType) if x == ""]:
            SQL.addUnits(self.newUnitName,self.newIP, self.newVictronID, self.newLocation, self.NoCCTV, self.newCompany, self.newLat, self.newLon, self.newUnitType)
            self.errorMessage.setText("Unit Added")
            self.unitNameAdd.setText("")
            self.locationAdd.setText("")
            self.companyAdd.setText("")
            self. numCamerasAdd.setText("")
            self.IPAdd.setText("")
            self.victronAdd.setText("")
            self.latAdd.setText("")
            self.lonAdd.setText("")
        else:
            self.errorMessage.setText("One or All Field Is Empty")

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

        layout = QGridLayout()

        userSelection = QComboBox()
        userSelection.addItems(listOfUsers)
        userSelection.setPlaceholderText("User Selection")
        userSelection.currentIndexChanged.connect(self.userChanged)

        layout.addWidget(userSelection,0,0,1,3)

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

        self.selectedUser = listOfUsers[index]

        self.selectedPassword = SQL.fetchPassword(self.selectedUser)

        self.usernameLabel.setText(self.selectedUser)
        self.passwordLineEdit.setText(self.selectedPassword)

    def changeUser(self):
        SQL.updateUser(self.selectedPassword, self.selectedUser)
        self.errorMessage.setText("User Updated")

    def deleteUser(self):

        SQL.deleteUsers(self.selectedUser)
        self.errorMessage.setText("User Deleted")

    def addUser(self):

        if not [x for x in (self.newUsername, self.newPassword, self.newCompany) if x == ""]:
            self.errorMessage.setText("User Added")
            SQL.addUsers(self.newUsername, self.newPassword, self.newCompany)
            self.usernameEdit.setText("")
            self.passwordAddLineEdit.setText("")
            self.companyLineEdit.setText("")
        else:
            self.errorMessage.setText("One or All Field Is Empty")

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
        self.setGeometry(0, 0, 430, 180)

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

        placeholder = QPushButton("placeholder")

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

    def closeEvent(self, event):
        self.login = loginUI()
        self.login.show()

        center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        geo = self.login.frameGeometry()
        geo.moveCenter(center)
        self.login.move(geo.topLeft())

        self.hide()
class userMonitoring(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dashboard")
        self.setGeometry(0,0,255,600)
        self.setStyleSheet("background-color: white;")

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

    def closeEvent(self, event):
        self.login = loginUI()
        self.login.show()

        center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        geo = self.login.frameGeometry()
        geo.moveCenter(center)
        self.login.move(geo.topLeft())

        self.hide()


class loginUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dashboard Login")
        self.setGeometry(0,0,380,320)
        #self.setStyleSheet("background-color: white;")

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
        username = Username
        self.errorMessage.hide()

    def getPassword(self, Password):
        global password
        password = Password
        self.errorMessage.hide()


    def openMonitoring(self):
        userRights = "ADMIN" #Placeholder
        placeholderUsername = "Jack"
        placeholderpassword = "Password"

        if username == placeholderUsername:
            loggedIn = password == placeholderpassword
        else:
            self.errorMessage.show()

        if loggedIn:

            if "ADMIN" in userRights:
                self.adminMonitoring = adminMonitoring()
                self.adminMonitoring.show()

                center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
                geo = self.adminMonitoring.frameGeometry()
                geo.moveCenter(center)
                self.adminMonitoring.move(geo.topLeft())

                self.hide()
            elif "USER" in userRights:
                self.userMonitoring = userMonitoring()
                self.userMonitoring.show()

                center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
                geo = self.userMonitoring.frameGeometry()
                geo.moveCenter(center)
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