from __future__ import annotations
from .common import LiresAPIBase
from typing import TYPE_CHECKING, Optional, Any
import aiohttp, json
if TYPE_CHECKING:
    from lires.core.dataClass import DataPointSummary
    from lires_server.types import ServerStatus
    from lires.user import UserInfo

JsonDumpable = list | dict | str | int | float | bool | None

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
    
    async def _formatParams(self, params: dict[str, JsonDumpable]):
        # _formatEntry = lambda x: json.dumps(x) if isinstance(x, (list, dict)) or x is None else x
        # _formatEntry = json.dumps
        def _formatEntry(x: Any):
            if x is None or isinstance(x, (list, dict)):
                return json.dumps(x)
            return x
        return {k: _formatEntry(v) for k, v in params.items()}
    
    async def _get(self, path: str, params: dict[str, JsonDumpable] = {}, headers: dict[str, str] = {}):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    path,
                    params={"key": self.token, **(await self._formatParams(params))}, 
                    headers=headers
                ) as res:
                self.ensureRes(res)
                return await res.json()
    
    async def _post(self, path: str, data: dict[str, JsonDumpable] = {}, headers: dict[str, str] = {}):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    path,
                    data={"key": self.token, **(await self._formatParams(data))},
                    headers={"Content-Type": "application/x-www-form-urlencoded", **headers}
                ) as res:
                self.ensureRes(res)
                return await res.json()
    
    async def status(self) -> ServerStatus:
        return await self._get(self.api_url + "/api/status")
    
    async def authorize(self) -> UserInfo:
        return await self._get(self.api_url + "/api/auth")

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
            "uuid": uuid,
            "tags": tags,
            # be careful with ""
            "bibtex": bibtex,
            "url": url,
        }

        # avoid circular import
        from lires.core.dataClass import DataPointSummary
        res = await self._post(self.api_url + "/api/dataman/update", params)
        return DataPointSummary(**res)