import dataclasses

from lires.core.dataClass import DataBase
from lires.config import DATABASE_DIR, VECTOR_DB_PATH, USER_DIR, getConf
from lires.user import UserPool
from lires.api import IServerConn
from tiny_vectordb import VectorDatabase

@dataclasses.dataclass(frozen=True)
class GlobalStorage:
    """Global storage for all handlers"""
    database = DataBase(DATABASE_DIR)
    user_pool = UserPool(USER_DIR)
    vector_database = VectorDatabase(
        path = VECTOR_DB_PATH, 
        collection_configs = [{
            "name": "doc_feature",
            "dimension": 768
        }],
        compile_config=getConf()["tiny_vectordb_compile_config"]
    )

    iconn = IServerConn()   # temporary, the endpoint will be set when server starts

    def flush(self):
        """
        Commit and flush all changes to disk
        """
        self.database.conn.commit()
        self.vector_database.commit()
        self.user_pool.conn.commit()