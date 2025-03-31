from __future__ import annotations
from .common import LiresAPIBase
from typing import TYPE_CHECKING, Optional, Any, Literal, TypedDict
import aiohttp, json, os
import deprecated
from lires.utils import randomAlphaNumeric
from lires.types.dataT import DataPointSummary
if TYPE_CHECKING:
    from lires.core.dataClass import DataPointSummary
    from lires_server.types import ServerStatus
    from lires.user import UserInfo

JsonDumpable = list | dict | str | int | float | bool | None
SearchType = Literal[ 'title', 'author', 'year', 'note', 'publication', 'feature', 'uuid'] | None
ReturnType = Literal['json', 'text']
class SearchRes(TypedDict):
    uids: list[str]
    scores: list[float]

class Connector(LiresAPIBase):
    def __init__(
        self, endpoint: str, token: str, 
        session_id: Optional[str] = None, verify_ssl: bool = True
        ):
        self._token = token
        self._endpoint = endpoint
        self._verify_ssl = verify_ssl
        if session_id is None:
            self._session_id = "default"
        self._session_id = 'py-api-'+randomAlphaNumeric(8)
    
    @property
    def token(self): return self._token
    @property
    def endpoint(self): return self._endpoint
    @property
    def session_id(self): return self._session_id

    def ensure_res(self, res: aiohttp.ClientResponse):
        if res.status == 401 or res.status == 403:
            raise self.Error.LiresConnectionAuthError("Invalid token ({}).".format(self.token))
        else:
            return super().ensure_res(res)
    
    async def _format_params(self, params: dict[str, JsonDumpable]):
        def _format_entry(x: Any):
            if x is None or isinstance(x, (list, dict)):
                return json.dumps(x)
            return x
        return {k: _format_entry(v) for k, v in params.items()}
    
    async def get(self, path: str, params: dict[str, JsonDumpable] = {}, headers: dict[str, str] = {}, return_type: ReturnType = "json"):
        headers['Authorization'] = f"Bearer {self.token}"
        async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(verify_ssl=self._verify_ssl), 
                headers=headers
            ) as session:
            async with session.get(
                    self.endpoint + path,
                    params={"session_id": self.session_id, **(await self._format_params(params))},
                ) as res:
                return await self._parse_res(res, return_type)
    
    async def post(self, path: str, data: dict[str, JsonDumpable] = {}, headers: dict[str, str] = {}, return_type: ReturnType = "json"):
        headers['Authorization'] = f"Bearer {self.token}"
        async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(verify_ssl=self._verify_ssl), 
                headers={"Content-Type": "application/x-www-form-urlencoded", **headers}
            ) as session:
            async with session.post(
                    self.endpoint + path,
                    data={"session_id": self.session_id, **(await self._format_params(data))},
                ) as res:
                return await self._parse_res(res, return_type)
    
    async def put(
        self, path: str, data: bytes, filename: str,
        metadata: dict[str, JsonDumpable] = {}, 
        content_type: str = "application/octet-stream",
        return_type: ReturnType = "json"):

        metadata = await self._format_params(metadata)

        form = aiohttp.FormData()
        form.add_field("key", self.token)
        form.add_field("session_id", self.session_id)
        for k, v in metadata.items():
            form.add_field(k, v)

        form.add_field("file", data, filename=filename, content_type=content_type)

        async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(verify_ssl=self._verify_ssl), 
                headers={"Authorization": f"Bearer {self.token}"}
            ) as session:
            async with session.put(
                    self.endpoint + path,
                    data=form,
                ) as res:
                return await self._parse_res(res, return_type)
    
    async def delete(
        self, path: str, data: dict[str, JsonDumpable] = {}, headers: dict[str, str] = {}, return_type: ReturnType = "json"):
        headers['Authorization'] = f"Bearer {self.token}"
        data = await self._format_params(data)
        form = aiohttp.FormData()
        form.add_field("key", self.token)
        form.add_field("session_id", self.session_id)
        for k, v in data.items():
            form.add_field(k, v)
        async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(verify_ssl=self._verify_ssl), 
                headers={"Content-Type": "application/x-www-form-urlencoded", **headers}
            ) as session:
            async with session.delete(
                    self.endpoint + path,
                    data=form,
                ) as res:
                return await self._parse_res(res, return_type)
        
    
    async def _parse_res(self, res: aiohttp.ClientResponse, return_type: ReturnType) -> Any:
        self.ensure_res(res)
        if return_type == "json":
            return await res.json()
        elif return_type == "text":
            return await res.text()
        else:
            raise ValueError(f"Invalid return_type: {return_type}")
    
class ServerConn:
    def __init__(
        self, endpoint: str, token: str, 
        session_id: Optional[str] = None, verify_ssl: bool = True
        ):
        self.__c = Connector(
            endpoint = endpoint, token = token,
            session_id = session_id, verify_ssl = verify_ssl
            )

    async def status(self) -> ServerStatus:
        return await self.__c.get("/api/status")

    async def authorize(self) -> UserInfo:
        return await self.__c.get("/api/auth")
    
    async def get_all_tags(self) -> list[str]:
        return await self.__c.get("/api/database/tags")

    async def get_all_keys(self) -> list[str]:
        return await self.__c.get("/api/database/keys")

    async def get_datapoint_summary(self, uuid: str) -> DataPointSummary:
        data = await self.__c.get(f"/api/datainfo/{uuid}")
        return DataPointSummary(**data)

    async def get_datapoint_summaries(self, uuids: list[str]) -> list[DataPointSummary]:
        data = await self.__c.post("/api/datainfo-list", {"uids": uuids})
        return [DataPointSummary(**x) for x in data]

    async def get_datapoint_abstract(self, uuid: str) -> str:
        return await self.__c.get(f"/api/datainfo-supp/abstract/{uuid}", return_type="text")

    async def set_datapoint_abstract(self, uuid: str, content: str):
        return await self.__c.post(f"/api/datainfo-supp/abstract-update/{uuid}", {"content": content}, return_type="text")
    
    async def get_datapoint_note(self, uuid: str) -> str:
        return await self.__c.get(f"/api/datainfo-supp/note/{uuid}", return_type="text")

    async def set_datapoint_note(self, uuid: str, content: str):
        return await self.__c.post(f"/api/datainfo-supp/note-update/{uuid}", {"content": content}, return_type="text")
    
    async def rename_tag_all(self, tag: str, new_tag: str):
        return await self.__c.post(f"/api/database/tag-rename", {"oldTag": tag, "newTag": new_tag}, return_type="text")
    
    async def delete_tag_all(self, tag: str):
        return await self.__c.post(f"/api/database/tag-delete", {"tag": tag}, return_type="text")
    
    async def delete_datapoint(self, uuid: str):
        return await self.__c.post(f"/api/dataman/delete", {
            "uuid": uuid
        }, return_type="text")
    
    async def upload_document(self, uid: str, file: str | bytes, filename: Optional[str] = None) -> DataPointSummary:
        if isinstance(file, str):
            if not filename:
                filename = os.path.basename(file)
            with open(file, "rb") as f:
                file = f.read()
        else:
            assert filename is not None

        ret = await self.__c.put(
            f"/doc/{uid}", file, filename, 
            return_type="json")
        return DataPointSummary(**ret)
    
    async def delete_document(self, uid: str) -> DataPointSummary:
        ret = await self.__c.delete(f"/doc/{uid}", return_type="json")
        return DataPointSummary(**ret)

    async def set_datapoint(
            self, uuid: Optional[str], 
            bibtex: Optional[str] = None, 
            tags: Optional[list[str]] = None,
            url: Optional[str] = None,
            ) -> DataPointSummary:
        """
        Create or update an entry in the database. 
        If `uuid` is not None, the entry with the given `uuid` will be updated.
        Otherwise, a new entry will be created, 
        all other fields should be complete when creating a new entry.
        """
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
            "bibtex": bibtex,
            "url": url,
        }

        res = await self.__c.post("/api/dataman/update", params)
        return DataPointSummary(**res)
    
    async def query(
        self, 
        tags: list[str] = [],
        search_by: SearchType = 'title',
        search_content: str = '',
        max_results: int = 99999,
    ) -> SearchRes:
        """ The main entry point for searching in the server. """
        params = {
            "tags": tags,
            "search_by": search_by,
            "search_content": search_content,
            "top_k": max_results,
        }
        return await self.__c.post("/api/filter/basic", params)