import argparse
from .core import globalVar as G

def parseArgs() -> argparse.Namespace:
    _description = f"\
Reseach bibiography manager (Resbibman) and Reseach bibiography manager Web (RBMWeb) \
are literature managers\
For more info and source code, visit: https://github.com/MenxLi/ResBibManager\
    "
    parser = argparse.ArgumentParser(description=_description)
    parser.add_argument("-v", "--version", action = "store_true", help = "Show version histories and current version and exit")
    parser.add_argument("-l", "--print_log", action = "store_true", help = "Print log and exit")
    parser.add_argument("-c", "--config_file", action = "store", help = "Configuration file path, \
                        if not specified, use default configuration file in RBM_HOME", default = None)
    parser.add_argument("-H", "--show_home", action= "store_true", help = "Print RBM_HOME and exit")
    parser.add_argument("--clear_cache", action = "store_true", help = "clear cache and exit")
    parser.add_argument("--reset_conf", action = "store_true", help = "Reset configuration and exit")

    sp = parser.add_subparsers(dest = "subparser", help = "Sub-commands")

    parser_client = sp.add_parser("client", help = "Start client gui program")

    parser_server = sp.add_parser("server", help = "Start resbibman server")
    parser_server.add_argument("-p", "--port", action = "store", default = "8080", help = "port, default to 8080")
    parser_server.add_argument("--rbmweb_port", action = "store", default = "8081", help = "port, default to 8081, set to 0 to disable RBMWeb")
    parser_server.add_argument("--iserver_host", action = "store", default = "127.0.0.1", help = "host, default to 127.0.0.1")
    parser_server.add_argument("--iserver_port", action = "store", default = "8731", help = "port, default to 8731")

    parser_iserver = sp.add_parser("iserver", help = "Start iRBM server")
    # set according to iRBM.server
    parser_iserver.add_argument("--port", type=int, default=8731, help="port, default to 8731")
    parser_iserver.add_argument("--host", type=str, default="0.0.0.0")
    parser_iserver.add_argument("--openai-api-base", type=str, default="https://api.openai.com/v1")
    parser_iserver.add_argument("--fastchat-api-base", type=str, default="")

    args = parser.parse_args()
    G.prog_args = args
    G.prog_parser = parser

    return args

