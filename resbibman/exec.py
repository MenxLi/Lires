import argparse, subprocess, warnings
from PyQt5.QtWidgets import QApplication
import os, sys, platform
from .GUIs.mainWindow import MainWindow
from .backend.utils import getDateTime, Logger
from .confReader import getConf, getConfV, getStyleSheets, saveToConf, VERSION, _VERSION_HISTORIES, LOG_FILE, CONF_FILE_PATH, DEFAULT_DATA_PATH

def execProg_():
	print("************Welcome to ResBibMan-v{}**************".format(VERSION))
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
	_description = f"\
Reseach bibiography manager (Resbibman) and Reseach bibiography manager Web (RBMWeb) \
are literature managers developed by Li, Mengxun (mengxunli@whu.edu.cn).\
The configration file for the software is at {CONF_FILE_PATH},\n\
For more info and source code, visit: https://github.com/MenxLi/ResBibManager\
	"
	parser = argparse.ArgumentParser(description=_description)
	parser.add_argument("-n", "--not_run", action= "store_true", help = "Not to run main program")
	parser.add_argument("-v", "--version", action = "store_true", help = "Show version histories and current version and exit")
	parser.add_argument("-s", "--server", action = "store_true", help = "Start server (RBMWeb)")
	parser.add_argument("--no_log", action = "store_true", help = "Open the program without recording log, stdout/stderr will be shown in terminal")
	parser.add_argument("--clear_log", action = "store_true", help = "Clear (delete) log file")
	parser.add_argument("--print_log", action = "store_true", help = "Print log and exit")
	args = parser.parse_args()

	if not os.path.exists(CONF_FILE_PATH):
		subprocess.check_call("rbm-resetConf")  # Installed with setup.py

	if not os.path.exists(getConf()["database"]):
		warnings.warn("Database not exists, default database path is set. \
			The path can be changed in settings or conf.json")
		if not os.path.exists(DEFAULT_DATA_PATH):
			os.mkdir(DEFAULT_DATA_PATH)
		saveToConf(database=DEFAULT_DATA_PATH)

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
	
	if args.server:
		from RBMWeb.backend import startServerProcess
		proc = startServerProcess()

	if not args.not_run:
		if args.no_log:
			execProg_()
		else:
			execProg()

	if args.server:
		proc.join()

if __name__=="__main__":
	run()
