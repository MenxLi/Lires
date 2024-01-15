from lires.core.base import LiresBase
import aiohttp

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