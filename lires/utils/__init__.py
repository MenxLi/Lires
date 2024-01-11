"""
Helper functions for the main modules, 
mostly without any external dependencies.
"""

from .log import setupLogger
from .term import BCOLORS, UseTermColor, MuteEverything
from .time import TimeUtils, timedFunc, Timer
from .fs import openFile, isWebURL
from .random import randomAlphaNumeric


__all__ = [
    "setupLogger",
    "BCOLORS", "UseTermColor", "MuteEverything",
    "TimeUtils", "timedFunc", "Timer",
    "openFile", "isWebURL", 
    "randomAlphaNumeric"
]