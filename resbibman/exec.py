import argparse
from json import decoder
from multiprocessing import Process
from PyQt5.QtWidgets import QApplication
import os, sys, platform
from .GUIs.mainWindow import MainWindow
from .confReader import getConf, getStyleSheets, VERSION

def execProg():
	app = QApplication(sys.argv)
	ss = getStyleSheets()[getConf()["stylesheet"]]
	if ss != "":
		with open(ss, "r", encoding="utf-8") as f:
			app.setStyleSheet(f.read())
	gui = MainWindow()
	sys.exit(app.exec_())

def execProg_():
	# Run with standalone process
	if platform.system() == 'Windows':    # Windows
		execProg()
	else:                                   # Mac and Linux variants
		pid = os.fork()
		if pid == 0:
			# Child process
			execProg()

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-v", "--version", action="store_true", help = "Show version")
	args = parser.parse_args()

	if args.version:
		print(VERSION)
	else:
		execProg_()

if __name__=="__main__":
	main()
