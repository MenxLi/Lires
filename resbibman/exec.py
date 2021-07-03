import argparse
from PyQt5.QtWidgets import QApplication
import os, sys, platform
from .GUIs.mainWindow import MainWindow
from .backend.utils import getDateTime, Logger
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
	Log will be recorded in LOG_FILE
	"""
	log_file = open(LOG_FILE, "a")
	sys.stdout = Logger(log_file)
	sys.stderr = Logger(log_file)
	log_file.write("\n\n============={}=============\n".format(getDateTime()))
	execProg_()
	log_file.close()

def run():
	parser = argparse.ArgumentParser()
	parser.add_argument("-n", "--not_run", action= "store_true", help = "Not to run main program")
	parser.add_argument("-v", "--version", action = "store_true", help = "Show version histories and current version and exit")
	parser.add_argument("--no_log", action = "store_true", help = "Open the program without recording log, stdout/stderr will be shown in terminal")
	parser.add_argument("--clear_log", action = "store_true", help = "Clear (delete) log file")
	parser.add_argument("--print_log", action = "store_true", help = "Print log and exit")
	args = parser.parse_args()

	if args.version:
		for v,d in _VERSION_HISTORIES:
			print("v{version}: {history}".format(version = v, history = d))
		print("=====================================")
		print("Current version: ", VERSION)
		args.not_run = True

	if args.clear_log:
		if os.path.exists(LOG_FILE):
			os.remove(LOG_FILE)
			print("log cleared")
		else: print("Log file not exits, run the program to create the log file")
	
	if args.print_log:
		if os.path.exists(LOG_FILE):
			with open(LOG_FILE, "r") as log_file:
				print(log_file.read())
		else: print("Log file not exits, run the program to create the log file")
		args.not_run = True

	if not args.not_run:
		if args.no_log:
			execProg_()
		else:
			execProg()

if __name__=="__main__":
	run()
