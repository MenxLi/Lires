"""
Helper functions for the main modules, 
mostly without any external dependencies.
"""

from .log import initDefaultLogger, setupLogger
from .bcolors import BCOLORS, UseTermColor


__all__ = [
    "initDefaultLogger", "setupLogger",
    "BCOLORS", "UseTermColor",
]