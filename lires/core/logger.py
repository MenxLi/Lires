from __future__ import annotations
import logging, os, asyncio
from typing import Optional, TYPE_CHECKING
from lires.utils import BCOLORS, TimeUtils
from lires.api import LServerConn
if TYPE_CHECKING:
    from lires.api.log import levelT

class LiresLogger(logging.Logger):

    def __init__(self, name: str, level = 0) -> None:
        super().__init__(name, level)
        self.__log_server = LServerConn(ignore_connection_error=True)
    
    async def __log(self, level: levelT, msg: str):
        # a coroutine that will not block the main thread
        # set timestamp to now, as the sending time may be postponed
        asyncio.ensure_future(
            self.__log_server.log(self.name, level, msg, timestamp=TimeUtils.nowStamp())
            )

    async def debug(self, msg: str, *args, **kwargs):
        if self.isEnabledFor(logging.DEBUG):
            await self.__log("DEBUG", msg)
        return super().debug(msg, *args, **kwargs)
    
    async def info(self, msg: str, *args, **kwargs):
        if self.isEnabledFor(logging.INFO):
            await self.__log("INFO", msg)
        return super().info(msg, *args, **kwargs)
    
    async def warning(self, msg: str, *args, **kwargs):
        if self.isEnabledFor(logging.WARNING):
            await self.__log("WARNING", msg)
        return super().warning(msg, *args, **kwargs)
    
    async def error(self, msg: str, *args, **kwargs):
        if self.isEnabledFor(logging.ERROR):
            await self.__log("ERROR", msg)
        return super().error(msg, *args, **kwargs)
    
    async def critical(self, msg: str, *args, **kwargs):
        if self.isEnabledFor(logging.CRITICAL):
            await self.__log("CRITICAL", msg)
        return super().critical(msg, *args, **kwargs)
    
    async def log(self, level: int, msg: str, *args, **kwargs):
        if self.isEnabledFor(level):
            await self.__log(logging.getLevelName(level), msg)
        return super().log(level, msg, *args, **kwargs)

def getFormatter(
    term_id: str = "default",
    term_id_color = BCOLORS.OKGRAY,
    ):
    PREFIX_LEN = 12
    def __formatTermID(term_id: str) -> str:
        if len(term_id) > PREFIX_LEN:
            return term_id[:PREFIX_LEN-1] + "-"
        else:
            return term_id.rjust(PREFIX_LEN)
    return term_id_color +f'[{__formatTermID(term_id)}]' \
            + BCOLORS.OKCYAN + ' %(asctime)s ' \
            + BCOLORS.OKCYAN + '[%(levelname)s] ' + BCOLORS.ENDC + ' %(message)s'

def setupRemoteLogger(
        _logger: str | LiresLogger, 
        term_id: Optional[str] = None, 
        term_id_color = BCOLORS.OKGRAY, 
        term_log_level: levelT = "INFO",
        remote_log_level: levelT | None = "DEBUG",
        ) -> LiresLogger:

    # check log level name
    assert term_log_level in logging._nameToLevel, f"Invalid log level name: {term_log_level}"
    assert remote_log_level in logging._nameToLevel, f"Invalid log level name: {remote_log_level}"

    if logging._nameToLevel[term_log_level] < logging._nameToLevel[remote_log_level]:
        print(f"{BCOLORS.WARNING}WARNING: Remote log level must be less critical than terminal log level{BCOLORS.ENDC}")

    if term_id is None:
        if isinstance(_logger, str):
            term_id = _logger
        else:
            term_id = _logger.name
    if isinstance(_logger, str):
        logger = LiresLogger(_logger)
    else:
        logger = _logger

    # get less critical log level and set it to be the level of logger
    if remote_log_level:
        logger.setLevel(min(logging.getLevelName(term_log_level), logging.getLevelName(remote_log_level)))
    else:
        logger.setLevel(logging.getLevelName(term_log_level))
        

    # remove all other handlers
    logger.handlers.clear()
    # set up terminal handler
    _ch = logging.StreamHandler()
    _ch.setLevel(term_log_level)
    _ch.setFormatter(logging.Formatter(getFormatter(term_id, term_id_color)))
    logger.addHandler(_ch)
    return logger

class LoggerStorage:
    _logger_dict: dict[str, LiresLogger] = {}

    def __init__(self):
        ...
    
    @property
    def core(self):
        return self.get("core")
    
    @property
    def server(self):
        return self.get("server")

    def get(self, _name: str) -> LiresLogger:
        from lires.config import getConf
        name = f"{_name}_{getConf()['database_id']}"
        # assure the name is a valid sqlite table name
        assert name.isidentifier(), f"Invalid logger name: {name}"
        if not name in self._logger_dict:
            logger = self.initLogger(name)
            self._logger_dict[name] = logger
        return self._logger_dict[name]
    
    def getdefault(self) -> logging.Logger:
        return logging.getLogger("default")

    def initLogger(self, name: str) -> LiresLogger:
        term_log_level: levelT = os.getenv("LRS_TERM_LOG_LEVEL", "INFO").upper()     # type: ignore
        logger = setupRemoteLogger(
            name,
            term_id=name,
            term_log_level=term_log_level,
            remote_log_level=os.getenv("LRS_LOG_LEVEL", "DEBUG").upper()     # type: ignore
        )
        return logger

