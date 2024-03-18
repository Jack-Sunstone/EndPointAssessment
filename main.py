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

class userManagement(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("User Management")
        self.setGeometry(0,0,650,580)

class adminMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Admin Menu")
        self.setWindowTitle(0,0,430,180)

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

        loginLayout = QGridLayout()

        self.Logo = QLabel()
        pixmap = QPixmap(logoPath)
        self.Logo.setPixmap(pixmap)
        self.Logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        loginLayout.addWidget(self.Logo, 0,0)


        usernameEntry = QLineEdit()
        usernameEntry.setPlaceholderText("Username")

        loginLayout.addWidget(usernameEntry, 4, 0)

        passwordEntry = QLineEdit()
        passwordEntry.setPlaceholderText("Password")

        loginLayout.addWidget(passwordEntry, 5, 0)

        loginButton = QPushButton("Login")

        loginLayout.addWidget(loginButton, 6,0)

        loginWidget = QWidget()
        loginWidget.setLayout(loginLayout)
        self.setCentralWidget(loginWidget)

        self.monitor = ioDashboard()
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