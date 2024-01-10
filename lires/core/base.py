from __future__ import annotations
import logging
import dataclasses

@dataclasses.dataclass(frozen=True)
class LoggerStorage:
    default = logging.getLogger('default')
    core = logging.getLogger("core")
    server = logging.getLogger("server")
    iserver = logging.getLogger("iserver")

@dataclasses.dataclass
class GlobalVar:
    loggers: LoggerStorage

# Global variables
G = GlobalVar(
    loggers=LoggerStorage()
)

class LiresBase:
    """
    The base class of all classes in lires
    """
    class Error:
        class LiresError(Exception): ...
        class LiresUserDuplicationError(LiresError):...
        class LiresUserNotFoundError(LiresError):...
        class LiresToBeImplementedError(LiresError, NotImplementedError):...
        class LiresDocTypeNotSupportedError(LiresToBeImplementedError):...
    
    @staticmethod
    def loggers():
        return G.loggers

def initLoggers():
    # May move to other place...
    import os
    from lires.confReader import LOG_DIR
    from lires.utils import setupLogger, BCOLORS
    # init loggers
    setupLogger(
        G.loggers.default,
        term_id_color=BCOLORS.OKGRAY,
        term_log_level="DEBUG",
        file_path = os.path.join(LOG_DIR, "default.log"),
        file_log_level="_ALL",
    )
    setupLogger(
        G.loggers.server,
        term_id_color=BCOLORS.OKBLUE,
        term_log_level="DEBUG",
        file_path = os.path.join(LOG_DIR, "server.log"),
        file_log_level="_ALL",
    )
    setupLogger(
        G.loggers.core,
        term_id_color=BCOLORS.OKGREEN,
        term_log_level="DEBUG",
        file_path = os.path.join(LOG_DIR, "core.log"),
        file_log_level="_ALL",
    )
    setupLogger(
        G.loggers.iserver,
        term_id_color=BCOLORS.WHITE,
        term_log_level="DEBUG",
        file_path = os.path.join(LOG_DIR, "iserver.log"),
        file_log_level="_ALL",
    )
initLoggers()