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

class LiresError:
    class LiresErrorBase(Exception): ...
    class LiresUserDuplicationError(LiresErrorBase):...
    class LiresUserNotFoundError(LiresErrorBase):...

    class LiresToBeImplementedError(LiresErrorBase, NotImplementedError):...
    class LiresDocTypeNotSupportedError(LiresToBeImplementedError):...

    class LiresConnectionError(LiresErrorBase):...
    class LiresConnectionAuthError(LiresConnectionError):...

class LiresBase:
    """
    The base class of all classes in lires
    """
    Error = LiresError
    
    @staticmethod
    def loggers():
        return G.loggers

def initLoggers():
    # May move to other place...
    import os
    from lires.config import LOG_DIR
    from lires.utils import setupLogger, BCOLORS

    term_log_level = os.getenv("LRS_LOG_LEVEL", "INFO").upper()
    file_log_level = os.getenv("LRS_FILE_LOG_LEVEL", "_ALL").upper()
    # init loggers
    setupLogger(
        G.loggers.default,
        term_id_color=BCOLORS.OKGRAY,
        term_log_level=term_log_level,
        file_path = os.path.join(LOG_DIR, "default.log"),
        file_log_level=file_log_level,
    )
    setupLogger(
        G.loggers.server,
        term_id_color=BCOLORS.OKBLUE,
        term_log_level=term_log_level,
        file_path = os.path.join(LOG_DIR, "server.log"),
        file_log_level=file_log_level,
    )
    setupLogger(
        G.loggers.core,
        term_id_color=BCOLORS.OKGREEN,
        term_log_level=term_log_level,
        file_path = os.path.join(LOG_DIR, "core.log"),
        file_log_level=file_log_level,
    )
    setupLogger(
        G.loggers.iserver,
        term_id_color=BCOLORS.WHITE,
        term_log_level=term_log_level,
        file_path = os.path.join(LOG_DIR, "iserver.log"),
        file_log_level=file_log_level,
    )
initLoggers()