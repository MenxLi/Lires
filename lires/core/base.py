import logging
import dataclasses

@dataclasses.dataclass(frozen=True)
class LoggerStorage:
    default = logging.getLogger()
    core = logging.getLogger("core")
    server = logging.getLogger("server")
    iserver = logging.getLogger("iserver")

g_loggers = LoggerStorage()

class LiresBase:

    class Error:
        class LiresError(Exception): ...
        class LiresUserDuplicationError(LiresError):...
        class LiresUserNotFoundError(LiresError):...
        class LiresToBeImplementedError(LiresError, NotImplementedError):...
        class LiresDocTypeNotSupportedError(LiresToBeImplementedError):...
    
    @staticmethod
    def loggers():
        return g_loggers