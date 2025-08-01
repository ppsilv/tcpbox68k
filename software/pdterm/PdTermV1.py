#!/usr/bin/python3
import sys
from PyQt6.QtWidgets import (QMainWindow, QApplication)
from PdTermPro import PDTermPro
              
if __name__ == "__main__":
    app = QApplication(sys.argv)
    #app.setStyle('Fusion')
    app.setStyle('Windows')
    window = PDTermPro()
    window.show()
    sys.exit(app.exec())
