"""
WILL BE DEPRECATED!
"""

from __future__ import annotations
import sys
from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from ..types.configT import LiresConfT

__initialized: bool
last_status_code: int   # a register for last connection status code

config:  LiresConfT           # configuration, set by lires.confReader

iserver_host: Optional[str] = None
iserver_port: Optional[str] = None

__global_dict: dict

def init():
    global __initialized
    global last_status_code
    global __global_dict

    thismodule = sys.modules[__name__]
    if hasattr(thismodule, "__initialized") and __initialized:
        return
    else:
        __initialized = True

    last_status_code = 200
    __global_dict = dict()

def resetGlobalConfVar():
    global config
    thismodule = sys.modules[__name__]
    if hasattr(thismodule, "config"):
        del config
