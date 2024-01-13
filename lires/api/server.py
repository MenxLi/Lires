from __future__ import annotations
from lires.core.base import LiresBase
from typing import TYPE_CHECKING
import aiohttp
if TYPE_CHECKING:
    from lires_server.types import ServerStatus
    from lires.user import UserInfo

class ServerConn(LiresBase):
    logger = LiresBase.loggers().core
    def __init__(self, token: str, server_url: str = ""):
        self._token = token
        self._api_url = server_url
    
    @property
    def token(self):
        return self._token
    
    @property
    def api_url(self):
        return self._api_url
    
    __commonErrors = {
        401: "Invalid token",
        403: "Invalid token",
        404: "Not found",
        405: "Method not allowed",
        500: "Internal server error",
    }
    def _ensureRes(self, res: aiohttp.ClientResponse):
        if res.status == 200:
            return

        if res.status == 401 or res.status == 403:
            raise self.Error.LiresConnectionAuthError("Invalid token ({}).".format(self.token))
        
        if res.status in self.__commonErrors:
            raise self.Error.LiresConnectionError(
                "Server returned {} ({}).".format(res.status, self.__commonErrors[res.status])
            )

        raise self.Error.LiresConnectionError(
            "Server returned {}.".format(res.status)
        )
    
    async def status(self) -> ServerStatus:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    self.api_url + "/api/status", 
                    params={"key": self.token}
                ) as res:
                self._ensureRes(res)
                return await res.json()
    
    async def authorize(self) -> UserInfo:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    self.api_url + "/api/auth", 
                    params={"key": self.token}
                ) as res:
                self._ensureRes(res)
                return await res.json()
