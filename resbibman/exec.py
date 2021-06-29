from PyQt5.QtWidgets import QApplication
import os, sys
from .GUIs.mainWindow import MainWindow
from .confReader import getConf, getStyleSheets

def main():
	app = QApplication(sys.argv)
	ss = getStyleSheets()[getConf()["stylesheet"]]
	if ss != "":
		with open(ss, "r") as f:
			app.setStyleSheet(f.read())
	gui = MainWindow()
	sys.exit(app.exec_())
if __name__=="__main__":
	main()
