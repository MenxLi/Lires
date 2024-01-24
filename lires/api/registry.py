from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import aiohttp
import aiohttp.client_exceptions
from .common import LiresAPIBase
if TYPE_CHECKING:
    from lires_service.registry import ServiceName, Registration

    
class RegistryConn(LiresAPIBase):

    def __init__(self):
        ...
    
    @property
    def url(self):
        # TODO: get from env
        return "http://localhost:8700"
    
    async def status(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url + "/status") as res:
                self.ensureRes(res)
                return await res.json()
    
    async def get(self, name: ServiceName, group: Optional[str] = None) -> Registration:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url + "/query",
                json = {
                    "name": name,
                    "group": group,
                }
            ) as res:
                self.ensureRes(res)
                return await res.json()
    
    async def register(self, info: Registration, ensure_status: bool = True):
        if ensure_status:
            try:
                await self.status()
            except aiohttp.client_exceptions.ClientConnectorError:
                exit("ERROR: Registry server not running")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url + "/register",
                json = info
            ) as res:
                self.ensureRes(res)
    
    def register_sync(self, info: Registration, ensure_status: bool = True):
        if ensure_status:
            try:
                self.run_sync(self.status())
            except aiohttp.client_exceptions.ClientConnectorError:
                exit("ERROR: Registry server not running")

        self.run_sync(self.register(info, ensure_status))