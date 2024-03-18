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


app = QApplication([])
app.setStyle('GTK')
window = loginUI()

window.show()
sys.exit(app.exec())