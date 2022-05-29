
from typing import TypeVar, Awaitable
import asyncio, nest_asyncio


T = TypeVar("T")
def asyncioLoopRun(call: Awaitable[T]) -> T:
    """
    Should be used instead of asyncio.run when already running a main loop
    (e.g. inside tornado server loop)
    """
    try:
        nest_asyncio.apply()
    except RuntimeError:
        pass
    CLOSE_LOOP = True
    try:
        loop = asyncio.get_event_loop()
        CLOSE_LOOP = False
    except RuntimeError:
        loop = asyncio.new_event_loop()
    out = loop.run_until_complete(call)
    if CLOSE_LOOP: loop.close()
    return out
