
"""
Connect to feed server
"""

from typing import Optional
from .common import LiresAPIBase, classCachedFunc
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
    
    @classCachedFunc()
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
        return await self.fetcher.post(
            await self.endpoint() + "/query",
            json = {
                "max_results": max_results,
                "category": category,
                "time_after": time_after if time_after > 0 else None,
                "time_before": time_before if time_before > 0 else None,
            }
        )
    
    async def categories(self) -> list[str]:
        return await self.fetcher.get(await self.endpoint() + "/categories")