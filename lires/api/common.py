from lires.core.base import LiresBase
import aiohttp, asyncio

class LiresAPIBase(LiresBase):
    logger = LiresBase.loggers().core
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

        if res.status in self._commonErrors:
            raise self.Error.LiresConnectionError(
                "Server returned {} ({}).".format(res.status, self._commonErrors[res.status])
            )

        raise self.Error.LiresConnectionError(
            "Server returned {}.".format(res.status)
        )
    
    def run_sync(self, coro):
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return asyncio.run_coroutine_threadsafe(coro, loop).result()
        else:
            return loop.run_until_complete(coro)