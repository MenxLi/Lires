from __future__ import annotations
from typing import TypedDict

class LiresConfT(TypedDict):
    """
    Refer to lrs-resetconf 
    for the generation of default configuration file
    """

    """STATIC SETTINGS, refer to confReader.getConf()"""
    database: str
    user_database: str
    index_store: str

__all__ = ["LiresConfT"]