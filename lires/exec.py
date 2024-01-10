import shutil
import os
from .core import globalVar as G
from .parser import prepareParser
from .cmd.generateDefaultConf import generateDefaultConf

def run():
    parser = prepareParser()
    args = parser.parse_args()
    assert args is not None     # type checking purpose

    # Read configuration file after parse agruments
    from .confReader import CONF_FILE_PATH, DATABASE_DIR, TMP_DIR, LOG_DIR, LRS_HOME
    from .version import VERSION, VERSION_HISTORIES

    # Init logger will import lires.core, 
    # May cause dependency error if only runs lires.ai
    try:
        from .utils import initDefaultLogger
        initDefaultLogger("DEBUG")
    except ImportError:
        pass

    NOT_RUN = False     # Indicates whether to run main program

    if not os.path.exists(CONF_FILE_PATH):
        print("Generating default configuration...")
        generateDefaultConf()

    if args.reset_conf:
        generateDefaultConf()
        NOT_RUN = True

    if not os.path.exists(DATABASE_DIR):
        os.mkdir(DATABASE_DIR)
        G.logger_lrs.info("Database directory not exists, create new. ")

    if args.version:
        for v,change_list in VERSION_HISTORIES:
            change_strings = []
            for change in change_list:
                if isinstance(change, str):
                    change_strings.append(change)
                elif isinstance(change, dict):
                    __only_key:str = list(change.keys())[0]
                    change_strings.append(f"{__only_key}: ")
                    for item in change[__only_key] if isinstance(change[__only_key], list) else [change[__only_key]]:   # type: ignore
                        item: str
                        change_strings.append("  "+item)
            print("v{version}: \n\t{history}".format(version = v, history = "\n\t".join(change_strings)))
        print("=====================================")
        print("Current version: ", VERSION)
        NOT_RUN = True

    if args.print_log:
        __find_log_fnames = []
        for fname in ["log.txt", "core.log", "server.log"]:
            if os.path.exists(os.path.join(LOG_DIR, fname)):
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
        parser.print_help()

    if args.subparser == "server":
        from lires_server.main import startServer
        startServer(
            host = args.host,
            port = args.port, 
            iserver_host = args.iserver_host, 
            iserver_port = args.iserver_port
            )
    
    if args.subparser == "iserver":
        from lires_ai.server import startServer
        startServer(
            host = args.host,
            port = args.port, 
            local_llm_chat = args.local_llm_chat,
            openai_models = args.openai_models,
        )

if __name__=="__main__":
    run()
