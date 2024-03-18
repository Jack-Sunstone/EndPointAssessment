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

class ioDashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("IO Box Dashboard")
        self.setGeometry(0,0,760,305)

class arcDashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ARC Dashboard")
        self.setGeometry(0,0,760,520)

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

        self.setWindowTitle("Admin Dashboard")
        self.setGeometry(0,0,255,600)

class userMonitoring(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dashboard")
        self.setGeometry(0,0,255,600)

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

        self.monitor = userManagement()
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