from __future__ import annotations
from .logger import LoggerStorage
import dataclasses
from .error import LiresError

@dataclasses.dataclass(frozen=True)
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
    Error = LiresError
    @staticmethod
    def loggers():
        return G.loggers
