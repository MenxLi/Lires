import argparse
from json import decoder
from multiprocessing import Process
import subprocess
from PyQt5.QtWidgets import QApplication
import os, sys, platform
from .GUIs.mainWindow import MainWindow
from .backend.utils import getDateTime
from .confReader import getConf, getStyleSheets, VERSION, _VERSION_HISTORIES, LOG_FILE

def execProg_():
	app = QApplication(sys.argv)
	ss = getStyleSheets()[getConf()["stylesheet"]]
	if ss != "":
		with open(ss, "r", encoding="utf-8") as f:
			app.setStyleSheet(f.read())
	gui = MainWindow()
	sys.exit(app.exec_())

def execProg():
	"""
	Run as standalone process
	Log will be recorded in LOG_FILE
	"""
	log_file = open(LOG_FILE, "a")
	sys.stdout = log_file
	sys.stderr = log_file
	if platform.system() == 'Windows':    	# Windows
		log_file.write("\n\n============={}=============\n".format(getDateTime()))
		process = Process(target=execProg_)
		process.start()
	else:                                   # Mac and Linux variants
		pid = os.fork()
		if not pid: 						# pid==0, Child process
			log_file.write("\n\n============={}=============\n".format(getDateTime()))
			execProg_()
	log_file.close()

def run():
	parser = argparse.ArgumentParser()
	parser.add_argument("-n", "--not_run", action= "store_true", help = "Not to run main program")
	parser.add_argument("-v", "--version", action = "store_true", help = "Show version histories and current version")
	parser.add_argument("-w", "--window", action = "store_true", help = "Open the program with shell window (log will not be recorded)")
	parser.add_argument("--clear_log", action = "store_true", help = "Clear (delete) log file")
	parser.add_argument("--print_log", action = "store_true", help = "Print log")
	args = parser.parse_args()

	if args.version:
		for v,d in _VERSION_HISTORIES:
			print("v{version}: {history}".format(version = v, history = d))
		print("=====================================")
		print("Current version: ", VERSION)

	if args.clear_log:
		if os.path.exists(LOG_FILE):
			os.remove(LOG_FILE)
			print("log cleared")
	
	if args.print_log:
		with open(LOG_FILE, "r") as log_file:
			print(log_file.read())

	if not args.not_run:
		if args.window:
			execProg_()
		else:
			execProg()

if __name__=="__main__":
	run()
