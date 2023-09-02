import shutil
import os
from .core import globalVar as G
from .parser import parseArgs

def run():
    parseArgs()
    args = G.prog_args
    assert args is not None     # type checking purpose

    # Read configuration file after parse agruments
    from .confReader import getConf, saveToConf, CONF_FILE_PATH, DEFAULT_DATA_PATH, TMP_DIR, LOG_FILE, LRS_HOME
    from .version import VERSION, VERSION_HISTORIES

    # Init logger will import lires.core, 
    # May cause dependency error if only runs lires.ai
    try:
        from .initLogger import initDefaultLogger
        initDefaultLogger("DEBUG")
    except ImportError:
        pass

    procs = []

    NOT_RUN = False     # Indicates whether to run main GUI

    def resetConf():
        from lires.cmd.generateDefaultConf import generateDefaultConf
        generateDefaultConf()

    if not os.path.exists(CONF_FILE_PATH):
        print("Generating default configuration...")
        resetConf()

    if args.reset_conf:
        resetConf()
        NOT_RUN = True

    if not os.path.exists(getConf()["database"]):
        G.logger_lrs.warn("Database not exists, default database path is set. "\
                          "The path can be changed in settings or edit conf.json")
        if not os.path.exists(DEFAULT_DATA_PATH):
            os.mkdir(DEFAULT_DATA_PATH)
        saveToConf(database=DEFAULT_DATA_PATH)

    if args.version:
        for v,change_list in VERSION_HISTORIES:
            change_strings = []
            for change in change_list:
                if isinstance(change, str):
                    change_strings.append(change)
                elif isinstance(change, dict):
                    __only_key = list(change.keys())[0]
                    change_strings.append(f"{__only_key}: ")
                    for item in change[__only_key]:
                        change_strings.append("  "+item)
            print("v{version}: \n\t{history}".format(version = v, history = "\n\t".join(change_strings)))
        print("=====================================")
        print("Current version: ", VERSION)
        NOT_RUN = True

    if args.print_log:
        __find_log_fnames = []
        for fname in ["log.txt", "core.log", "server.log"]:
            if os.path.exists(os.path.join(LRS_HOME, fname)):
                __find_log_fnames.append(fname)
        if not __find_log_fnames: print("Log file not exits, run the program to create the log file")
        else:
            print("\n".join([f"{idx}. {f}" for idx, f in enumerate(__find_log_fnames)]))
            __to_show_idx = input("Choose which log to show (default: 0): ")
            if not __to_show_idx: __to_show_idx = 0
            with open(os.path.join(LRS_HOME, __find_log_fnames[int(__to_show_idx)]), "r") as f:
                print(f.read())
        print("=======================Above is the log=======================")
        NOT_RUN = True

    if args.show_home:
        print(LRS_HOME)
        NOT_RUN = True
    
    if args.clear_cache:
        prompt_msgs = [
            "This action is going to delete: {}".format(TMP_DIR),
            "Please make sure that lires is not running in online mode",
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
        # show help
        assert G.prog_parser is not None
        G.prog_parser.print_help()

    if args.subparser == "server":
        from .server.main import startServerProcess
        procs.append(startServerProcess(args.port, args.iserver_host, args.iserver_port))
    
    if args.subparser == "web":
        from .server.main import startFrontendServerProcess
        procs.append(startFrontendServerProcess(args.port))
    
    if args.subparser == "iserver":
        import subprocess
        call_args = ["python3", "-m", "lires_ai.server"]
        for k in [
            "port", "host", 
            ]:
            val = getattr(args, k.replace("-", "_"))
            call_args += ["--" + k, str(val)]

        subprocess.check_call(call_args)

    if args.subparser == "client":
        from lires_qt.main import execProg as execProgQt
        execProgQt()

    for proc in procs:
        proc.join()

if __name__=="__main__":
    run()
