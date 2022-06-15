import argparse, subprocess, warnings, logging
import shutil
from PyQt6.QtWidgets import QApplication
import os, sys, platform
from .core import globalVar as G
from .GUIs.mainWindow import MainWindow
from .core.utils import getDateTimeStr, Logger, LoggingLogger
from .confReader import getConf, getConfV, getStyleSheets, saveToConf, VERSION, _VERSION_HISTORIES, LOG_FILE, CONF_FILE_PATH, DEFAULT_DATA_PATH, TMP_DIR

def execProg_():
    print("************Welcome to ResBibMan-v{}**************".format(VERSION))
    app = QApplication(sys.argv)
    ss = getStyleSheets()[getConf()["stylesheet"]]
    if ss != "":
        with open(ss, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    gui = MainWindow()
    EXIT_CODE =  app.exec()
    
    G.clearTempDirs()

    return EXIT_CODE

def execProg(log_level = "INFO"):
    """
    Log will be recorded in LOG_FILE
    """
    logger = logging.getLogger("rbm")
    #  logger.setLevel(getattr(logging, log_level))
    logger.setLevel(logging.DEBUG)

    # StreamHandler show user defined log level
    s_handler = logging.StreamHandler(sys.stdout)
    s_handler.setLevel(getattr(logging, log_level))
    fomatter = logging.Formatter('%(asctime)s (%(levelname)s) - %(message)s')
    s_handler.setFormatter(fomatter)
    logger.addHandler(s_handler)

    # FileHandler show DEBUG log level
    f_handler = logging.FileHandler(LOG_FILE)
    f_handler.setLevel(logging.DEBUG)
    fomatter = logging.Formatter('%(asctime)s (%(levelname)s) - %(message)s')
    f_handler.setFormatter(fomatter)
    logger.addHandler(f_handler)

    # re-direct stdout and error
    sys.stdout = LoggingLogger(logger, logging.INFO, write_to_terminal = False)
    sys.stderr = LoggingLogger(logger, logging.ERROR, write_to_terminal = False)
    # re-direct unhandled exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
        else:
            logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        logger.info("Exit.")
        sys.exit()
    sys.excepthook = handle_exception

    print("\n\n============={}=============\n".format(getDateTimeStr()))
    return execProg_()

def run():
    _description = f"\
Reseach bibiography manager (Resbibman) and Reseach bibiography manager Web (RBMWeb) \
are literature managers\
The configration file for the software is at {CONF_FILE_PATH},\n\
For more info and source code, visit: https://github.com/MenxLi/ResBibManager\
    "
    parser = argparse.ArgumentParser(description=_description)
    parser.add_argument("-v", "--version", action = "store_true", help = "Show version histories and current version and exit")
    parser.add_argument("-s", "--server", action = "store_true", help = "Start server (RBMWeb) and resbibman GUI")
    parser.add_argument("-S", "--server_headless", action = "store_true", help = "Start server (RBMWeb) without resbibman GUI")
    parser.add_argument("-l", "--print_log", action = "store_true", help = "Print log and exit")
    parser.add_argument("-L", "--log_level", action= "store", type = str, default="INFO", help = "log level")
    parser.add_argument("-c", "--clear_cache", action = "store_true", help = "clear cache and exit")
    parser.add_argument("--no_log", action = "store_true", help = "Open the program without recording log, stdout/stderr will be shown in terminal")
    parser.add_argument("--clear_log", action = "store_true", help = "Clear (delete) log file")
    parser.add_argument("--reset_conf", action = "store_true", help = "Reset configuration and exit")
    args = parser.parse_args()

    procs = []

    NOT_RUN = False     # Indicates whether to run main GUI

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
        NOT_RUN = True

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
        NOT_RUN = True
    
    if args.clear_cache:
        prompt_msgs = [
            "This action is going to delete: {}".format(TMP_DIR),
            "Please make sure that resbibman is not running in online mode",
            "Proceed? (y/[else]): "
        ]
        if input("\n".join(prompt_msgs)) == "y":
            if os.path.exists(TMP_DIR):
                shutil.rmtree(TMP_DIR)
            print("success.")
        else:
            print("abort.")
        NOT_RUN = True
    
    if args.server_headless:
        NOT_RUN = True
        args.server = True

    if args.server:
        from RBMWeb.server import startServerProcess
        procs.append(startServerProcess())

    if args.reset_conf:
        from resbibman.cmdTools.generateDefaultConf import generateDefaultConf
        generateDefaultConf()
        NOT_RUN = True

    if not NOT_RUN:
        if args.no_log:
            execProg_()
        else:
            execProg(args.log_level)

    if args.server:
        for proc in procs:
            proc.join()

if __name__=="__main__":
    run()
