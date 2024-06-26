"""
Helper functions for the main modules, 
mostly without any external dependencies.
"""

from .log import setupLogger
from .term import BCOLORS, UseTermColor, MuteEverything, tablePrint
from .time import TimeUtils, timedFunc, Timer
from .fs import openFile, isWebURL
from .random import randomAlphaNumeric
from .network import getLocalIP


__all__ = [
    "setupLogger",
    "BCOLORS", "UseTermColor", "MuteEverything", "tablePrint",
    "TimeUtils", "timedFunc", "Timer",
    "openFile", "isWebURL", 
    "randomAlphaNumeric",
    "getLocalIP",
]