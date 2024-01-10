import dataclasses

from lires.core.dataClass import DataBase
from lires.confReader import DATABASE_DIR, VECTOR_DB_PATH, USER_DIR, getConf
from lires.user import UserPool
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

    def flush(self):
        """
        Commit and flush all changes to disk
        """
        self.database.conn.commit()

        self.vector_database.commit()
        self.vector_database.flush()

        self.user_pool.conn.commit()