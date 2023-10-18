from __future__ import annotations
import sys, shutil, logging, os, argparse
from typing import List, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from ..types.configT import LiresConfT
    from ..server.auth.account import AccountPermission

__initialized: bool
logger_lrs: logging.Logger
logger_lrs_server: logging.Logger
last_status_code: int   # a register for last connection status code

prog_args: Optional[argparse.Namespace]     # set by lires.exec
prog_parser: Optional[argparse.ArgumentParser]     # set by lires.exec
config:  LiresConfT           # configuration, set by lires.confReader

iserver_host: Optional[str] = None
iserver_port: Optional[str] = None

__global_dict: dict

def init():
    global logger_lrs
    global logger_lrs_server
    global __initialized
    global last_status_code
    global prog_args, prog_parser
    global __global_dict

    thismodule = sys.modules[__name__]
    if hasattr(thismodule, "__initialized") and __initialized:
        logger_lrs.debug("Skipping re-initialization of globalVar")
        return
    else:
        __initialized = True

    logger_lrs = logging.getLogger("lires")
    logger_lrs_server = logging.getLogger("lires_server")
    last_status_code = 200
    prog_args = None
    prog_parser = None
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

def resetGlobalConfVar():
    global config
    thismodule = sys.modules[__name__]
    if hasattr(thismodule, "config"):
        del config
