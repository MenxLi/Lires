import subprocess, warnings, logging
import shutil
from PyQt6.QtWidgets import QApplication
import os, sys
from .core import globalVar as G
from .parser import parseArgs

def execProg():
    from .GUIs.mainWindow import MainWindow
    from .confReader import getStyleSheets, getConf, VERSION
    from .core.utils import getDateTimeStr
    logger = logging.getLogger("rbm")
    logger.info("************Welcome to ResBibMan-v{} | {}**************".format(VERSION, getDateTimeStr()))
    app = QApplication(sys.argv)
    ss = getStyleSheets()[getConf()["stylesheet"]]
    if ss != "":
        with open(ss, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    gui = MainWindow()
    EXIT_CODE =  app.exec()
    
    G.clearTempDirs()

    return EXIT_CODE

def run():
    parseArgs()
    args = G.prog_args
    assert args is not None     # type checking purpose

    # Read configuration file after parse agruments
    from .confReader import getConf, saveToConf, VERSION, _VERSION_HISTORIES, CONF_FILE_PATH, DEFAULT_DATA_PATH, TMP_DIR, LOG_FILE
    from .initLogger import initLogger

    if not args.no_log:
        initLogger(args.log_level)

    procs = []

    NOT_RUN = False     # Indicates whether to run main GUI

    if not os.path.exists(CONF_FILE_PATH):
        #  subprocess.check_call("rbm-resetConf")  # Installed with setup.py
        print("Generating default configuration...")
        args.reset_conf = True

    if args.reset_conf:
        from resbibman.cmdTools.generateDefaultConf import generateDefaultConf
        generateDefaultConf()
        NOT_RUN = True

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

    if NOT_RUN:
        exit()

    # ======== Parse subcommands ========

    if args.subparser is None:
        # Set default to GUI
        args.subparser = "gui"

    if args.subparser == "server":
        from RBMWeb.server import startServerProcess
        procs.append(startServerProcess(args.port))

    if args.subparser == "gui":
        execProg()

    for proc in procs:
        proc.join()

if __name__=="__main__":
    run()
