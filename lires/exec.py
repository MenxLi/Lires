import shutil
import os, logging
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
        logging.getLogger('default').info("Database directory not exists, create new. ")

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
        _all_log_files = os.listdir(LOG_DIR)
        _all_log_files.sort()
        print("Find {} log files: ".format(len(_all_log_files)))
        for i, log_file in enumerate(_all_log_files):
            print("[{}] {}".format(i+1, log_file))
        _sel = input("Select one to print: ")
        try:
            _sel = int(_sel)
            assert _sel >= 1 and _sel <= len(_all_log_files)
            with open(os.path.join(LOG_DIR, _all_log_files[_sel-1]), "r", encoding="utf-8") as fp:
                print("=======================Below is the log=======================")
                print(fp.read())
        except Exception as e:
            print("Error: ", e)
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
