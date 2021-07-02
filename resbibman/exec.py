import argparse
from json import decoder
from multiprocessing import Process
import subprocess
from PyQt5.QtWidgets import QApplication
import os, sys, platform
from .GUIs.mainWindow import MainWindow
from .confReader import getConf, getStyleSheets, VERSION, _VERSION_HISTORIES

def execProg_():
	app = QApplication(sys.argv)
	ss = getStyleSheets()[getConf()["stylesheet"]]
	if ss != "":
		with open(ss, "r", encoding="utf-8") as f:
			app.setStyleSheet(f.read())
	gui = MainWindow()
	sys.exit(app.exec_())

def execProg():
	# Run as standalone process
	if platform.system() == 'Windows':    	# Windows
		process = Process(target=execProg_)
		process.start()
	else:                                   # Mac and Linux variants
		pid = os.fork()
		if not pid: 						# pid==0, Child process
			execProg_()

def run():
	parser = argparse.ArgumentParser()
	parser.add_argument("-v", "--version", action = "store_true", help = "Show version histories and current version")
	parser.add_argument("-w", "--window", action = "store_true", help = "Open the program with shell window")
	args = parser.parse_args()

	if args.version:
		for v,d in _VERSION_HISTORIES:
			print("v{version}: {history}".format(version = v, history = d))
		print("=====================================")
		print("Current version: ", VERSION)
	elif args.window:
		execProg_()
	else:
		execProg()

if __name__=="__main__":
	run()
