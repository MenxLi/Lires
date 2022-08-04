import sys, shutil, logging, os
from typing import List, TypedDict
from ..confReader import getConf

__initialized: bool
logger_rbm: logging.Logger
last_status_code: int   # a register for last connection status code
tmpdirs: List[str]      # temporary directories

config: dict            # configuration, set by ..confReader.py

def init():
    global tmpdirs
    global logger_rbm
    global __initialized
    global last_status_code

    thismodule = sys.modules[__name__]
    if hasattr(thismodule, "__initialized") and __initialized:
        return
    else:
        __initialized = True

    tmpdirs = []
    logger_rbm = logging.getLogger("rbm")
    last_status_code = 200

def clearTempDirs():
    global tmpdirs
    for d in tmpdirs:
        if os.path.exists(d):
            shutil.rmtree(d)
            logger_rbm.debug("Removed temporary directory - {}".format(d))
    tmpdirs = []

def resetGlobalConfVar():
    global config
    thismodule = sys.modules[__name__]
    if hasattr(thismodule, "config"):
        del config
