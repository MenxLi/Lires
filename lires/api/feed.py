
"""
Connect to feed server
"""

import aiohttp
from typing import Optional
from .common import LiresAPIBase
from .registry import RegistryConn

class FServerConn(LiresAPIBase):
    """
    Connect to log server
    """
    def __init__(self, endpoint: Optional[str] = None):
        if endpoint is None:
            self._url = None
        else:
            self._url = endpoint
    
    async def endpoint(self):
        if self._url is None:
            reg = await RegistryConn().get("feed")
            return reg["endpoint"]
        return self._url
    
    async def query(
        self, max_results: int = 10, 
        category: Optional[str] = None,
        time_after: float = -1,
        time_before: float = -1,
        ) -> list[dict]:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                await self.endpoint() + "/query",
                json = {
                    "max_results": max_results,
                    "category": category,
                    "time_after": time_after if time_after > 0 else None,
                    "time_before": time_before if time_before > 0 else None,
                }
            ) as res:
                self.ensureRes(res)
                return await res.json()
    
    async def categories(self) -> list[str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                await self.endpoint() + "/categories",
            ) as res:
                self.ensureRes(res)
                return await res.json()
    