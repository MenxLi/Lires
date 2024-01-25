from __future__ import annotations
import logging, os
from typing import Optional, TYPE_CHECKING
from lires.utils import BCOLORS
if TYPE_CHECKING:
    from lires.api.lserver import levelT

class LiresLogger(logging.Logger):
    ...


def setupRemoteLogger(
        _logger: str | LiresLogger, 
        term_id: Optional[str] = None, 
        term_id_color = BCOLORS.OKGRAY, 
        term_log_level: levelT = "INFO",
        remote_log_level: levelT | None = "DEBUG",
        ) -> LiresLogger:
    from lires.api.lserver import ClientHandler
    PREFIX_LEN = 12

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
    def __formatTermID(term_id: str) -> str:
        if len(term_id) > PREFIX_LEN:
            return term_id[:PREFIX_LEN-1] + "-"
        else:
            return term_id.rjust(PREFIX_LEN)
    # set up terminal handler
    _ch = logging.StreamHandler()
    _ch.setLevel(term_log_level)
    _ch.setFormatter(logging.Formatter(term_id_color +f'[{__formatTermID(term_id)}]'
                                       +BCOLORS.OKCYAN + ' %(asctime)s '
                                       +BCOLORS.OKCYAN + '[%(levelname)s] ' + BCOLORS.ENDC + ' %(message)s'))
    logger.addHandler(_ch)

    if remote_log_level:
        _rh = ClientHandler(logger.name)
        _rh.setLevel(remote_log_level)
        logger.addHandler(_rh)
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
        name = f"{_name}.{getConf()['database_id']}"
        if not name in self._logger_dict:
            logger = self.initLogger(name)
            self._logger_dict[name] = logger
        return self._logger_dict[name]

    def initLogger(self, name: str) -> LiresLogger:
        term_log_level: levelT = os.getenv("LRS_LOG_LEVEL", "INFO")     # type: ignore
        logger = setupRemoteLogger(
            name,
            term_id=name,
            term_log_level=term_log_level,
            remote_log_level="DEBUG",
        )
        return logger

