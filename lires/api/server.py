from __future__ import annotations
from .common import LiresAPIBase
from typing import TYPE_CHECKING, Optional
import aiohttp, json
if TYPE_CHECKING:
    from lires.core.dataClass import DataPointSummary
    from lires_server.types import ServerStatus
    from lires.user import UserInfo

class ServerConn(LiresAPIBase):
    def __init__(self, token: str, server_url: str = ""):
        self._token = token
        self._api_url = server_url
    
    @property
    def token(self):
        return self._token
    
    @property
    def api_url(self):
        return self._api_url

    def ensureRes(self, res: aiohttp.ClientResponse):
        if res.status == 401 or res.status == 403:
            raise self.Error.LiresConnectionAuthError("Invalid token ({}).".format(self.token))
        else:
            return super().ensureRes(res)
    
    async def status(self) -> ServerStatus:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    self.api_url + "/api/status", 
                    params={"key": self.token}
                ) as res:
                self.ensureRes(res)
                return await res.json()
    
    async def authorize(self) -> UserInfo:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    self.api_url + "/api/auth", 
                    params={"key": self.token}
                ) as res:
                self.ensureRes(res)
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

        # avoid circular import
        from lires.core.dataClass import DataPointSummary
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.api_url}/api/dataman/update",
                                    data=params,
                                    headers={"Content-Type": "application/x-www-form-urlencoded"}) as response:
                self.ensureRes(response)
                return DataPointSummary(**(await response.json()))