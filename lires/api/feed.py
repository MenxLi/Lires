
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
    
    async def getLatest(self, max_results: int = 10, category: Optional[str] = None) -> list[dict]:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                await self.endpoint() + "/latest",
                json = {
                    "max_results": max_results,
                    "category": category,
                }
            ) as res:
                self.ensureRes(res)
                return await res.json()
    