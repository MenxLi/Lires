from __future__ import annotations
from .common import LiresAPIBase
from typing import TYPE_CHECKING, Optional, Any, Literal, TypedDict
import aiohttp, json
from lires.utils import randomAlphaNumeric
if TYPE_CHECKING:
    from lires.core.dataClass import DataPointSummary
    from lires_server.types import ServerStatus
    from lires.user import UserInfo

JsonDumpable = list | dict | str | int | float | bool | None
SearchType = Literal[ 'title', 'author', 'year', 'note', 'publication', 'feature', 'uuid'] | None
class SearchRes(TypedDict):
    uids: list[str]
    scores: list[float]

def _makeDatapointSummary(js: dict[str, Any]) -> DataPointSummary:
    # avoid circular import
    from lires.core.dataClass import DataPointSummary
    return DataPointSummary(**js)

class ServerConn(LiresAPIBase):
    def __init__(self, endpoint: str, token: str, session_id: Optional[str] = None):
        self._token = token
        self._endpoint = endpoint
        if session_id is None:
            self._session_id = "default"
        self._session_id = 'py-api-'+randomAlphaNumeric(8)
    
    @property
    def token(self): return self._token
    @property
    def endpoint(self): return self._endpoint
    @property
    def session_id(self): return self._session_id

    def ensureRes(self, res: aiohttp.ClientResponse):
        if res.status == 401 or res.status == 403:
            raise self.Error.LiresConnectionAuthError("Invalid token ({}).".format(self.token))
        else:
            return super().ensureRes(res)
    
    async def _formatParams(self, params: dict[str, JsonDumpable]):
        def _formatEntry(x: Any):
            if x is None or isinstance(x, (list, dict)):
                return json.dumps(x)
            return x
        return {k: _formatEntry(v) for k, v in params.items()}
    
    async def _get(self, path: str, params: dict[str, JsonDumpable] = {}, headers: dict[str, str] = {}, return_type = "json"):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    self.endpoint + path,
                    params={"key": self.token, "session_id": self.session_id, **(await self._formatParams(params))},
                    headers=headers
                ) as res:
                return await self._parseRes(res, return_type)
    
    async def _post(self, path: str, data: dict[str, JsonDumpable] = {}, headers: dict[str, str] = {}, return_type = "json"):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    self.endpoint + path,
                    data={"key": self.token, "session_id": self.session_id, **(await self._formatParams(data))},
                    headers={"Content-Type": "application/x-www-form-urlencoded", **headers}
                ) as res:
                return await self._parseRes(res, return_type)
    
    async def _parseRes(self, res: aiohttp.ClientResponse, return_type: str) -> Any:
        self.ensureRes(res)
        if return_type == "json":
            return await res.json()
        elif return_type == "text":
            return await res.text()
        else:
            raise ValueError(f"Invalid return_type: {return_type}")
    
    async def status(self) -> ServerStatus:
        return await self._get("/api/status")
    async def authorize(self) -> UserInfo:
        return await self._get("/api/auth")
    
    async def reqAllTags(self) -> list[str]:
        return await self._get("/api/database/tags")
    async def reqAllKeys(self) -> list[str]:
        return await self._get("/api/database/keys")

    async def reqDatapointSummary(self, uuid: str) -> DataPointSummary:
        data = await self._get(f"/api/datainfo/{uuid}")
        return _makeDatapointSummary(data)
    async def reqDatapointSummaries(self, uuids: list[str]) -> list[DataPointSummary]:
        data = await self._post("/api/datainfo-list", {"uids": uuids})
        return [_makeDatapointSummary(x) for x in data]

    async def reqDatapointAbstract(self, uuid: str) -> str:
        return await self._get(f"/api/datainfo-supp/abstract/{uuid}", return_type="text")
    async def updateDatapointAbstract(self, uuid: str, content: str):
        return await self._post(f"/api/datainfo-supp/abstract-update/{uuid}", {"content": content}, return_type="text")
    
    async def reqDatapointNote(self, uuid: str) -> str:
        return await self._get(f"/api/datainfo-supp/note/{uuid}", return_type="text")
    async def updateDatapointNote(self, uuid: str, content: str):
        return await self._post(f"/api/datainfo-supp/note-update/{uuid}", {"content": content}, return_type="text")

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

        res = await self._post("/api/dataman/update", params)
        return _makeDatapointSummary(**res)
    
    async def filter(
        self, 
        tags: list[str] = [],
        search_by: SearchType = 'title',
        search_content: str = '',
        max_results: int = 99999,
    ) -> SearchRes:
        params = {
            "tags": tags,
            "search_by": search_by,
            "search_content": search_content,
            "top_k": max_results,
        }
        return await self._post("/api/filter/basic", params)