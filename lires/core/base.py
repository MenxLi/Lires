from __future__ import annotations
import logging
import dataclasses

@dataclasses.dataclass(frozen=True)
class LoggerStorage:
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
