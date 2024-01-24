
"""
Connect to log server
"""

import aiohttp
import logging
from lires.utils import BCOLORS
from typing import Literal, Optional
from .common import LiresAPIBase
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
    
    async def endpoint(self):
        if self._url is None:
            reg = await RegistryConn().get("log")
            return reg["endpoint"]
        return self._url
    
    async def log(self, logger_name: str, level: levelT, message: str):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    await self.endpoint() + "/log/" + logger_name, 
                    json = {
                        "level": level,
                        "message": message,
                    },
                ) as res:
                    self.ensureRes(res)
        except Exception as e:
            if self.ignore_connection_error and isinstance(e, aiohttp.ClientConnectionError):
                # maybe server is not ready
                pass
            else:
                raise e
    
    def log_sync(self, logger_name: str, level: levelT, message: str):
        import requests
        try:
            requests.post(
                "http://127.0.0.1" + "/log/" + logger_name, 
                json = {
                    "level": level,
                    "message": message,
                },
            )
        except Exception as e:
            if self.ignore_connection_error \
                and (isinstance(e, requests.ConnectionError) or isinstance(e, requests.ConnectTimeout)):
                # maybe server is not ready
                pass
            else:
                raise e
        return 
        # try:
        #     self.run_sync(self.log(logger_name, level, message))
        # except RuntimeError as e:
        #     if 'Event loop stopped before Future completed.' in str(e):
        #         # ignore this error, it should be caused by the loop is closed on exiting
        #         # may cause some log loss, but it's ok
        #         pass
        #     else:
        #         raise e

class ClientHandler(logging.Handler):
    """
    A logging handler that sends log to log server
    """
    def __init__(self, logger_name):
        super().__init__()
        self.logger_name = logger_name
        self.conn = LServerConn(endpoint=None, ignore_connection_error=True)
    def emit(self, record: logging.LogRecord):
        level_name: levelT = record.levelname # type: ignore
        self.conn.log_sync(
            self.logger_name, 
            level_name, 
            record.getMessage()
            )
