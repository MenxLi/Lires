from __future__ import annotations
from lires.core.base import LiresBase
from typing import TYPE_CHECKING, Optional
import aiohttp, json
if TYPE_CHECKING:
    from lires.core.dataClass import DataPointSummary
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
        400: "Bad request",
        401: "Invalid token",
        403: "Invalid token",
        404: "Not found",
        405: "Method not allowed",
        409: "Conflict",
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

    async def updateEntry(
            self, uuid: Optional[str], 
            bibtex: Optional[str] = None, 
            tags: Optional[list[str]] = None,
            url: Optional[str] = None,
            ) -> DataPointSummary:
        if uuid is None:
            assert bibtex is not None
            assert tags is not None
            assert url is not None
            if uuid is None:
                # make sure other fields are not None
                if bibtex is None or tags is None or url is None:
                    raise ValueError("uid is None, other fields should be complete")

        params = {
            "key": self.token,
            "uuid": json.dumps(uuid),
            "tags": json.dumps(tags),
            # be careful with ""
            "bibtex": bibtex if bibtex is not None else json.dumps(None),
            "url": url if url is not None else json.dumps(None),
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.api_url}/api/dataman/update",
                                    data=params,
                                    headers={"Content-Type": "application/x-www-form-urlencoded"}) as response:
                self._ensureRes(response)
                return await response.json()