from __future__ import annotations
from typing import TypedDict

class LiresConfT(TypedDict):
    """
    Refer to lrs-resetconf 
    for the generation of default configuration file,

    changed in v1.1.2:
        - All fields are moved as static fields of lires.confReader, May add some fields in the future.
    """
    ...

__all__ = ["LiresConfT"]