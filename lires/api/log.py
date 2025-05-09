
"""
Connect to log server
"""

import aiohttp
from typing import Literal, Optional
from .common import LiresAPIBase, class_cached_fn
from .registry import RegistryConn

levelT = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
class LServerConn(LiresAPIBase):
    """
    Connect to log server
    """
    def __init__(self, endpoint: Optional[str] = None, ignore_connection_error: bool = False):
        if endpoint is None:
            self._url = None
        else:
            self._url = endpoint
        self.ignore_connection_error = ignore_connection_error
    
    @class_cached_fn()
    async def endpoint(self):
        if self._url is None:
            reg = await RegistryConn().get("log")
            return reg["endpoint"]
        return self._url
    
    async def log(self, logger_name: str, level: levelT, message: str, timestamp: float):
        try:
            await self.fetcher.post(
                await self.endpoint() + "/log/" + logger_name, 
                json = {
                    "level": level,
                    "message": message,
                    "timestamp": timestamp,
                },
                return_raw = True
            )
        except Exception as e:
            if self.ignore_connection_error and \
                isinstance(e, aiohttp.ClientConnectionError) or isinstance(e, self.Error.LiresResourceNotFoundError):
                # maybe server is not ready
                pass
            else:
                raise e