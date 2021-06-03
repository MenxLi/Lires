from PyQt5.QtWidgets import QApplication
from src.GUIs.mainWindow import MainWindow
import os, sys


if __name__=="__main__":
    app = QApplication(sys.argv)
    gui = MainWindow()
    sys.exit(app.exec_())
