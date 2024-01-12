from __future__ import annotations
from lires.core.base import LiresBase
from typing import TYPE_CHECKING
import aiohttp
if TYPE_CHECKING:
    from lires_server.types import ServerStatus

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
    
    def _checkRes(self, res: aiohttp.ClientResponse) -> bool:
        if res.status != 200:
            self.logger.error("Server returned {}".format(res.status))
            return False
        return True
    
    async def status(self) -> ServerStatus:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.api_url + "/api/status", 
                params={"key": self.token}
                ) as res:
                if self._checkRes(res):
                    return await res.json()
                else:
                    if res.status == 401 or res.status == 403:
                        raise self.Error.LiresConnectionAuthError("Invalid token")
                    raise self.Error.LiresConnectionError("Server returned {}".format(res.status))
