import sys
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *

class loginUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dashboard Login")
        self.setGeometry(550,300,380,320)


app = QApplication([])
app.setStyle('GTK')
window = loginUI()

window.show()
sys.exit(app.exec())