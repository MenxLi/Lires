import argparse
from .core import globalVar as G

# a standalone parser for iserver, this is also used in lires_ai.server
def prepareIServerParser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("--port", type=int, default=8731, help="port, default to 8731")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="host, default to 0.0.0.0")
    parser.add_argument("--local-llm-chat", type=str, default="", 
        help = "name of the local llm chat model, default is not using local llm chat")
    parser.add_argument("--openai-models", nargs="+", default=["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"], type=str,
        help="models that can be used with openai-api, you would typically specify a different openai-base if you change this")
    return parser

def parseArgs() -> argparse.Namespace:
    _description = f"\
Lires, a research bibliography manager. \
For more info and source code, visit: https://github.com/MenxLi/ResBibManager\
    "
    parser = argparse.ArgumentParser(description=_description)
    parser.add_argument("-v", "--version", action = "store_true", help = "Show version histories and current version and exit")
    parser.add_argument("-l", "--print_log", action = "store_true", help = "Print log and exit")
    parser.add_argument("-c", "--config_file", action = "store", help = "Configuration file path, \
                        if not specified, use default configuration file in LRS_HOME", default = None)
    parser.add_argument("-H", "--show_home", action= "store_true", help = "Print LRS_HOME and exit")
    parser.add_argument("--clear_cache", action = "store_true", help = "clear cache and exit")
    parser.add_argument("--reset_conf", action = "store_true", help = "Reset configuration and exit")

    sp = parser.add_subparsers(dest = "subparser", help = "Sub-commands")

    parser_server = sp.add_parser("server", help = "Start lires server")
    parser_server.add_argument("-p", "--port", action = "store", default = "8080", help = "port, default to 8080")
    parser_server.add_argument("--iserver_host", action = "store", default = "127.0.0.1", help = "host, default to 127.0.0.1")
    parser_server.add_argument("--iserver_port", action = "store", default = "8731", help = "port, default to 8731")

    parser_iserver = sp.add_parser("iserver", help = "Start LiresAI server")
    prepareIServerParser(parser_iserver)

    args = parser.parse_args()
    G.prog_args = args
    G.prog_parser = parser

    return args

