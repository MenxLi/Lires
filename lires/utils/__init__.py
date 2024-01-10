"""
Helper functions for the main modules, 
mostly without any external dependencies.
"""

from .log import initDefaultLogger, setupLogger
from .term import BCOLORS, UseTermColor, MuteEverything
from .time import TimeUtils, timedFunc, Timer
from .fs import openFile, isWebURL
from .random import randomAlphaNumeric


__all__ = [
    "initDefaultLogger", "setupLogger",
    "BCOLORS", "UseTermColor", "MuteEverything",
    "TimeUtils", "timedFunc", "Timer",
    "openFile", "isWebURL", 
    "randomAlphaNumeric"
]