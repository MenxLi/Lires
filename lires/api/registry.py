from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING, Optional
import aiohttp
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
                self.url + "/get",
                json = {
                    "name": name,
                    "group": group,
                }
            ) as res:
                self.ensureRes(res)
                return await res.json()
    
    async def register(self, info: Registration, ensure_status: bool = True):
        if ensure_status:
            await self.status()
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url + "/register",
                json = info
            ) as res:
                self.ensureRes(res)
    
    def register_sync(self, info: Registration, ensure_status: bool = True):
        # try to run in current loop, if not, create a new one
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(self.register(info, ensure_status), loop)
        else:
            loop.run_until_complete(self.register(info, ensure_status))