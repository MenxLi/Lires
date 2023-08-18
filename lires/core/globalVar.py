from __future__ import annotations
import sys, shutil, logging, os, argparse
from typing import List, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from ..types.configT import ResbibmanConfT
    from ..server.auth.account import AccountPermission

__initialized: bool
logger_rbm: logging.Logger
logger_rbm_server: logging.Logger
last_status_code: int   # a register for last connection status code
tmpdirs: List[str]      # temporary directories, will be cleared on lires GUI exit

prog_args: Optional[argparse.Namespace]     # set by lires.exec
prog_parser: Optional[argparse.ArgumentParser]     # set by lires.exec
config:  ResbibmanConfT           # configuration, set by lires.confReader
account_permission: Optional[AccountPermission]     # account permission, set by Database.fetch

iserver_host: Optional[str] = None
iserver_port: Optional[str] = None

__global_dict: dict

def init():
    global tmpdirs
    global logger_rbm
    global logger_rbm_server
    global __initialized
    global last_status_code
    global prog_args, prog_parser
    global __global_dict
    global account_permission

    thismodule = sys.modules[__name__]
    if hasattr(thismodule, "__initialized") and __initialized:
        logger_rbm.debug("Skipping re-initialization of globalVar")
        return
    else:
        __initialized = True

    tmpdirs = []
    logger_rbm = logging.getLogger("rbm")
    logger_rbm_server = logging.getLogger("rbm_server")
    last_status_code = 200
    prog_args = None
    prog_parser = None
    account_permission = None
    __global_dict = dict()

def setGlobalAttr(key, val):
    global __global_dict
    __global_dict[key] = val

def getGlobalAttr(key):
    global __global_dict
    return __global_dict[key]

def deleteGlobalAttr(key):
    global __global_dict
    del __global_dict[key]

def hasGlobalAttr(key):
    global __global_dict
    return key in __global_dict.keys()

def clearTempDirs():
    global tmpdirs
    logger_rbm.info("Clearing temporary directories...")
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
