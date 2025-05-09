import os, asyncio
from .parser import prepareParser
from .config import generate_default_conf

def initLoggers():
    # May move to other place...
    import os
    from lires.utils import setup_logger, BCOLORS
    from lires.utils.log import TermLogLevelT

    term_log_level: TermLogLevelT = os.getenv("LRS_LOG_LEVEL", "INFO").upper()          # type: ignore

    # init loggers for wild usage
    setup_logger(
        'default',
        term_id_color=BCOLORS.OKGRAY,
        term_log_level=term_log_level,
    )

def run():
    parser = prepareParser()
    args = parser.parse_args()
    assert args is not None     # type checking purpose

    # Read configuration file after parse agruments
    from .config import CONF_FILE_PATH, LRS_HOME
    from .version import VERSION, VERSION_HISTORIES
    initLoggers()

    NOT_RUN = False     # Indicates whether to run main program

    if not os.path.exists(CONF_FILE_PATH):
        generate_default_conf()

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

    if args.show_home:
        print(LRS_HOME)
        NOT_RUN = True
    
    if NOT_RUN:
        exit()

    # ======== Parse subcommands ========

    if args.subparser is None:
        # show help
        parser.print_help()
    
    if args.subparser == "registry":
        from lires_service.registry.server import start_server as startRegistryServer
        asyncio.run(startRegistryServer(
            host = args.host,
            port = args.port,
        ))

    if args.subparser == "server":
        from lires_server.main import start_server
        start_server(
            host = args.host,
            port = args.port, 
            )
    
    if args.subparser == "ai":
        from lires_service.ai.server import start_server as startIServer
        asyncio.run(startIServer(
            host = args.host,
            port = args.port, 
            local_llm_chat = args.local_llm_chat,
            openai_models = args.openai_models,
        ))
    
    if args.subparser == "log":
        from lires_service.log.server import start_logger_server
        asyncio.run(start_logger_server(
            file = args.file,
            host = args.host,
            port = args.port,
        ))
    
    if args.subparser == "feed":
        from lires_service.feed.server import start_server as startFeedServer
        asyncio.run(startFeedServer(
            host = args.host,
            port = args.port,
        ))

if __name__=="__main__":
    run()
