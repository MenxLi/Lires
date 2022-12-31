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
    parser.add_argument("-c", "--config_file", action = "store", help = "Configuration file path", default = None)
    parser.add_argument("-L", "--log_level", action= "store", type = str, default="INFO", help = "log level")
    parser.add_argument("-H", "--show_home", action= "store_true", help = "Print RBM_HOME and exit")
    parser.add_argument("--no_log", action = "store_true", help = "Open the program without recording log, stdout/stderr will be shown in terminal")
    parser.add_argument("--clear_cache", action = "store_true", help = "clear cache and exit")
    parser.add_argument("--clear_log", action = "store_true", help = "Clear (delete) log file")
    parser.add_argument("--reset_conf", action = "store_true", help = "Reset configuration and exit")

    sp = parser.add_subparsers(dest = "subparser", help = "Sub-commands")

    parser_client = sp.add_parser("client", help = "Start client gui program (default)")

    parser_server = sp.add_parser("server", help = "Start RBMWeb server")
    parser_server.add_argument("-p", "--port", action = "store", default = "8080", help = "port, default to 8080")

    args = parser.parse_args()
    G.prog_args = args

    return args

