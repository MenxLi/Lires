from __future__ import annotations
from typing import TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from tiny_vectordb.wrap import CompileConfig as TinyVectordbCompileConfig

class LiresConfT(TypedDict):
    """
    Refer to lrs-reset
    for the generation of default configuration file,

    changed in v1.1.2:
        - Almost all fields are moved as static fields of lires.config, May add some fields in the future.
    """
    ## Should contain no optional or ambiguous type fields!!

    # An unique id for the LRS_HOME directory,
    # used for identifying different LRS_HOME directories
    database_id: str

    # Random port range for microservices, 
    # if the port is specified as 0, will use a random port in this range
    # otherwise, will use the specified port
    service_port_range: list[int]

    # jit compile configuration for tiny_vectordb
    tiny_vectordb_compile_config: TinyVectordbCompileConfig

__all__ = ["LiresConfT"]