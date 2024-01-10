"""
Helper functions for the main modules, 
mostly without any external dependencies.
"""

from .log import initDefaultLogger, setupLogger
from .term import BCOLORS, UseTermColor
from .time import TimeUtils, timedFunc, Timer


__all__ = [
    "initDefaultLogger", "setupLogger",
    "BCOLORS", "UseTermColor",
    "TimeUtils", "timedFunc", "Timer",
]