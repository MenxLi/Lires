import argparse

def _prepareRegistryServerParser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("--host", default="127.0.0.1", help="The host to listen")
    parser.add_argument("--port", default=8700, type=int, help="The port to listen")
    return parser

def _prepareServerParser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("-p", "--port", action = "store", default = "8080", help = "port, default to 8080")
    parser.add_argument("--host", action = "store", default = "0.0.0.0", help = "host, default to 0.0.0.0")
    return parser

def _prepareAIServerParser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("-p", "--port", type=int, default=0, help="port, default to 8731")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="host, default to 0.0.0.0")
    parser.add_argument("--local-llm-chat", type=str, default="", 
        help = "name of the local llm chat model, default is not using local llm chat")
    parser.add_argument("--openai-models", nargs="+", default=["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"], type=str,
        help="models that can be used with openai-api, you would typically specify a different openai-base if you change this")
    return parser

def _prepareLogServerParser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("--file", default="", help="The log file path")
    parser.add_argument("--host", default="127.0.0.1", help="The host to listen")
    parser.add_argument("--port", default=0, type=int, help="The port to listen")
    return parser

def prepareParser() -> argparse.ArgumentParser:
    _description = f"\
Lires, a self-hosted research literature manager. \
For more info and source code, visit: https://github.com/MenxLi/Lires\
    "
    parser = argparse.ArgumentParser(description=_description)
    parser.add_argument("-v", "--version", action = "store_true", help = "Show version histories and current version and exit")
    parser.add_argument("-H", "--show_home", action= "store_true", help = "Print LRS_HOME and exit")
    parser.add_argument("--reset_conf", action = "store_true", help = "Reset configuration and exit")

    sp = parser.add_subparsers(dest = "subparser", help = "Sub-commands")

    parser_registry = sp.add_parser("registry", help = "Start lires registry server")
    _prepareRegistryServerParser(parser_registry)

    parser_server = sp.add_parser("server", help = "Start lires main server")
    _prepareServerParser(parser_server)

    parser_ai = sp.add_parser("ai", help = "Start lires ai server")
    _prepareAIServerParser(parser_ai)

    parser_log = sp.add_parser("log", help = "Start lires log server")
    _prepareLogServerParser(parser_log)

    return parser

