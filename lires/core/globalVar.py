"""
WILL BE DEPRECATED!
"""

from __future__ import annotations
import sys
from typing import Optional

__initialized: bool
last_status_code: int   # a register for last connection status code

iserver_host: Optional[str] = None
iserver_port: Optional[str] = None

def init():
    global __initialized
    global last_status_code

    thismodule = sys.modules[__name__]
    if hasattr(thismodule, "__initialized") and __initialized:
        return
    else:
        __initialized = True

    last_status_code = 200