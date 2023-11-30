from __future__ import annotations
from typing import TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from tiny_vectordb.wrap import CompileConfig as TinyVectordbCompileConfig

class LiresConfT(TypedDict):
    """
    Refer to lrs-resetconf 
    for the generation of default configuration file,

    changed in v1.1.2:
        - Almost all fields are moved as static fields of lires.confReader, May add some fields in the future.
    """

    # Should contain no optional or ambiguous type fields!!
    # as we will use __default_config to compare with the configuration file in confReader.py

    tiny_vectordb_compile_config: TinyVectordbCompileConfig

__all__ = ["LiresConfT"]