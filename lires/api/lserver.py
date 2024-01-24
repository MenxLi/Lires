
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

def setupRemoteLogger(
        _logger: str | logging.Logger, 
        term_id: Optional[str] = None, 
        term_id_color = BCOLORS.OKGRAY, 
        term_log_level: levelT = "INFO",
        remote_log_level: levelT = "DEBUG",
        ) -> logging.Logger:
    if term_id is None:
        if isinstance(_logger, str):
            term_id = _logger
        else:
            term_id = _logger.name
    if isinstance(_logger, str):
        logger = logging.getLogger(_logger)
    else:
        logger = _logger

    # get less critical log level and set it to be the level of logger
    logger.setLevel(min(logging.getLevelName(term_log_level), logging.getLevelName(remote_log_level)))

    # remove all other handlers
    logger.handlers.clear()
    def __formatTermID(term_id: str) -> str:
        fix_len = 8
        if len(term_id) > fix_len:
            return term_id[:fix_len-3] + "..."
        else:
            return term_id.rjust(fix_len)
    # set up terminal handler
    _ch = logging.StreamHandler()
    _ch.setLevel(term_log_level)
    _ch.setFormatter(logging.Formatter(term_id_color +f'[{__formatTermID(term_id)}]'
                                       +BCOLORS.OKCYAN + ' %(asctime)s '
                                       +BCOLORS.OKCYAN + '[%(levelname)s] ' + BCOLORS.ENDC + ' %(message)s'))
    logger.addHandler(_ch)

    _rh = ClientHandler(logger.name)
    _rh.setLevel(remote_log_level)
    logger.addHandler(_rh)
    return logger