from __future__ import annotations
from typing import TypeVar, Callable, overload, Literal, Any
import aiohttp, asyncio, sys, time
import asyncio.coroutines
from lires.core.error import LiresError
from lires.config import LRS_KEY

FuncT = TypeVar("FuncT", bound=Callable)
def classCachedFunc(cache_time: float = 0.1):
    def decorator(func: FuncT) -> FuncT:
        func_name = func.__name__
        async def wrapper(self: LiresAPIBase, *args, **kwargs):
            assert args == (), 'classCachedFunc does not support args'
            assert kwargs == {}, 'classCachedFunc does not support kwargs'
            req_name = f"cls_id:{id(self.__class__)}.{func_name}"
            if req_name not in self._cache_method_res:
                self._cache_method_res[req_name] = {
                    "time": 0,
                    "res": None
                }
            if time.time() - self._cache_method_res[req_name]["time"] > cache_time:
                if asyncio.iscoroutinefunction(func):
                    self._cache_method_res[req_name]["res"] = await func(self, *args, **kwargs)
                else:
                    self._cache_method_res[req_name]["res"] = func(self, *args, **kwargs)
                self._cache_method_res[req_name]["time"] = time.time()
            return self._cache_method_res[req_name]["res"]
        return wrapper # type: ignore
    return decorator


class ServiceFetcher:

    @overload
    async def post(self, url, json: dict, return_raw: Literal[False] = False) -> Any: ...
    @overload
    async def post(self, url, json: dict, return_raw: Literal[True]) -> aiohttp.ClientResponse: ...
    async def post(self, url: str, json: dict, return_raw: bool = False) -> Any | aiohttp.ClientResponse:
        async with aiohttp.ClientSession(
            headers = { "Authorization": "Bearer " + LRS_KEY }
            ) as session:
            async with session.post(url, json = json) as res:
                LiresAPIBase.ensureRes(res)
                if return_raw:
                    return res
                return await res.json()
    
    async def get(self, url: str):
        async with aiohttp.ClientSession(
            headers = { "Authorization": "Bearer " + LRS_KEY }
            ) as session:
            async with session.get(url) as res:
                LiresAPIBase.ensureRes(res)
                return await res.json()

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
        507: "Disk full"
    }
    fetcher = ServiceFetcher()

    @property
    def logger(self):
        # avoid circular import
        from lires.core.logger import LoggerStorage
        return LoggerStorage().get('api')

    @classmethod
    def ensureRes(cls, res: aiohttp.ClientResponse):
        if res.status == 200:
            return True
        
        if res.status == 404:
            raise cls.Error.LiresResourceNotFoundError(
                "Server returned 404 ({}).".format(cls._commonErrors[res.status])
            )
        
        if res.status == 401 or res.status == 403:
            raise cls.Error.LiresConnectionAuthError(
                "Server returned {} ({}).".format(res.status, cls._commonErrors[res.status])
            )
        
        if res.status == 507:
            raise cls.Error.LiresExceedLimitError(
                "Server returned 507 ({}).".format(cls._commonErrors[res.status])
            )

        if res.status in cls._commonErrors:
            raise cls.Error.LiresConnectionError(
                "Server returned {} ({}).".format(res.status, cls._commonErrors[res.status])
            )

        raise cls.Error.LiresConnectionError(
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