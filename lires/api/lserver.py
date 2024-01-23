
"""
Connect to log server
"""

import aiohttp, asyncio
from typing import Literal
from .common import LiresAPIBase

levelT = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
class LServerConnection(LiresAPIBase):
    """
    Connect to log server
    """
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.session = aiohttp.ClientSession()
        self.url = f"http://{host}:{port}/log"
    
    async def log(self, logger_name: str, level: levelT, message: str):
        async with self.session.post(
            self.url + "/" + logger_name, 
            json = {
                "level": level,
                "message": message,
            }
        ) as res:
            self.ensureRes(res)
    
    # sync version of log
    def log_(self, logger_name: str, level: levelT, message: str):
        asyncio.run(self.log(logger_name, level, message))
    
    async def close(self):
        await self.session.close()