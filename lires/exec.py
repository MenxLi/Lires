import os, logging
from .parser import prepareParser
from .cmd.generateDefaultConf import generateDefaultConf

def run():
    parser = prepareParser()
    args = parser.parse_args()
    assert args is not None     # type checking purpose

    # Read configuration file after parse agruments
    from .config import CONF_FILE_PATH, DATABASE_DIR, LRS_HOME
    from .version import VERSION, VERSION_HISTORIES

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
        from .cmd.log import main as showLog
        showLog()
        NOT_RUN = True

    if args.show_home:
        print(LRS_HOME)
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
            iserver_endpoint = args.iserver_endpoint,
            )
    
    if args.subparser == "iserver":
        from lires_ai.server import startServer as startIServer
        startIServer(
            host = args.host,
            port = args.port, 
            local_llm_chat = args.local_llm_chat,
            openai_models = args.openai_models,
        )
    
    if args.subparser == "lserver":
        from lires_log.server import startLoggerServer
        if args.file is None:
            args.file = "lires_log.db"
        startLoggerServer(
            file = args.file,
            host = args.host,
            port = args.port,
        )

if __name__=="__main__":
    run()
