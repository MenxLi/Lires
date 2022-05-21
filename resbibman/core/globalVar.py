import sys, shutil, logging
from typing import List

__initialized: bool
logger_rbm: logging.Logger
tmpdirs: List[str]      # temporary directories

def init():
    global tmpdirs
    global logger_rbm
    global __initialized

    thismodule = sys.modules[__name__]
    if hasattr(thismodule, "__initialized") and __initialized:
        return
    else:
        __initialized = True

    tmpdirs = []
    logger_rbm = logging.getLogger("rbm")


def clearTempDirs():
    global tmpdirs
    for d in tmpdirs:
        shutil.rmtree(d)
        logger_rbm.debug("Removed temporary directory - {}".format(d))
    tmpdirs = []

