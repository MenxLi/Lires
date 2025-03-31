"""
Helper functions for the main modules, 
mostly without any external dependencies.
"""

from .log import setup_logger
from .term import BCOLORS, UseTermColor, MuteEverything, table_print
from .time import TimeUtils, timed_func, Timer
from .fs import open_file, is_web_url
from .random import random_alphanumeric
from .network import get_local_ip


__all__ = [
    "setup_logger",
    "BCOLORS", "UseTermColor", "MuteEverything", "table_print",
    "TimeUtils", "timed_func", "Timer",
    "open_file", "is_web_url", 
    "random_alphanumeric",
    "get_local_ip",
]