from __future__ import annotations
from typing import TypeVar, Callable
import aiohttp, asyncio, sys, time
import asyncio.coroutines
from lires.core.error import LiresError

FuncT = TypeVar("FuncT", bound=Callable)
def cachedFunc(cache_time: float = 0.1):
    def decorator(func: FuncT) -> FuncT:
        func_name = func.__name__
        async def wrapper(self: LiresAPIBase, *args, **kwargs):
            if func_name not in self._cache_method_res:
                self._cache_method_res[func_name] = {
                    "time": 0,
                    "res": None
                }
            if time.time() - self._cache_method_res[func_name]["time"] > cache_time:
                if asyncio.iscoroutinefunction(func):
                    self._cache_method_res[func_name]["res"] = await func(self, *args, **kwargs)
                else:
                    self._cache_method_res[func_name]["res"] = func(self, *args, **kwargs)
                self._cache_method_res[func_name]["time"] = time.time()
            return self._cache_method_res[func_name]["res"]
        return wrapper # type: ignore
    return decorator


class LiresAPIBase:
    Error = LiresError
    _cache_method_res = {}
    _commonErrors = {
        400: "Bad request",
        401: "Invalid token",
        403: "Invalid token",
        404: "Not found",
        405: "Method not allowed",
        409: "Conflict",
        500: "Internal server error",
    }
    def ensureRes(self, res: aiohttp.ClientResponse):
        if res.status == 200:
            return True
        
        if res.status == 404:
            raise self.Error.LiresResourceNotFoundError(
                "Server returned 404 ({}).".format(self._commonErrors[res.status])
            )
        
        if res.status == 401 or res.status == 403:
            raise self.Error.LiresConnectionAuthError(
                "Server returned {} ({}).".format(res.status, self._commonErrors[res.status])
            )

        if res.status in self._commonErrors:
            raise self.Error.LiresConnectionError(
                "Server returned {} ({}).".format(res.status, self._commonErrors[res.status])
            )

        raise self.Error.LiresConnectionError(
            "Server returned {}.".format(res.status)
        )
    
    def run_sync(self, coro):
        NEED_CLOSE = False
        if sys.version_info < (3, 10):
            loop = asyncio.get_event_loop()
        else:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError as e:
                if 'There is no current event loop in thread' in str(e) \
                    or 'no running event loop' in str(e):
                    loop = asyncio.new_event_loop()
                    NEED_CLOSE = True
                else:
                    raise e
        res = loop.run_until_complete(coro)
        if NEED_CLOSE:
            loop.close()
        return res