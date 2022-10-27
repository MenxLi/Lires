from __future__ import annotations
import sys, shutil, logging, os, argparse
from typing import List, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from ..types.configT import ResbibmanConfT

__initialized: bool
logger_rbm: logging.Logger
last_status_code: int   # a register for last connection status code
tmpdirs: List[str]      # temporary directories, will be cleared on resbibman GUI exit

prog_args: Optional[argparse.Namespace]     # set by resbibman.exec
config:  ResbibmanConfT           # configuration, set by resbibman.confReader

def init():
    global tmpdirs
    global logger_rbm
    global __initialized
    global last_status_code
    global prog_args

    thismodule = sys.modules[__name__]
    if hasattr(thismodule, "__initialized") and __initialized:
        return
    else:
        __initialized = True

    tmpdirs = []
    logger_rbm = logging.getLogger("rbm")
    last_status_code = 200
    prog_args = None

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
