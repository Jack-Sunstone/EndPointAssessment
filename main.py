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

class loginUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dashboard Login")
        self.setGeometry(550,300,380,320)

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


app = QApplication([])
app.setStyle('GTK')
window = loginUI()

window.show()
sys.exit(app.exec())