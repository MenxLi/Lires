from __future__ import annotations
from typing import TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from tiny_vectordb.wrap import CompileConfig as TinyVectordbCompileConfig

class LiresConfT(TypedDict):
    """
    Refer to lrs-reset
    for the generation of default configuration file,

    changes in v1.1.2:
        - Almost all fields are moved as static fields of lires.config, May add some fields in the future.
    
    changes in v1.7.5:
        - Add deploy_token field for server communication
        - Change database_id to group
    
    changes in v1.8.0:
        - Remove deploy_token field
    
    changes in v1.8.2:
        - Add max_users and default_user_max_storage fields
    """
    ## Should contain no optional or ambiguous type fields!!

    # An unique id for the LRS_HOME directory,
    # used for identifying different LRS_HOME directories
    group: str

    # Random port range for microservices, 
    # if the port is specified as 0, will use a random port in this range
    # otherwise, will use the specified port
    service_port_range: list[int]

    # The maximum number of users, 
    # set to 0 for unlimited users
    max_users: int

    # The maximum storage for each user
    # e.g 512m, 1g, 1t
    default_user_max_storage: str

    # jit compile configuration for tiny_vectordb
    tiny_vectordb_compile_config: TinyVectordbCompileConfig

__all__ = ["LiresConfT"]