import dataclasses

import asyncio
from lires.core.dataClass import DataBase
from lires.config import DATABASE_DIR, VECTOR_DB_PATH, USER_DIR, getConf
from lires.user import UserPool
from lires.api import IServerConn
from tiny_vectordb import VectorDatabase

@dataclasses.dataclass(frozen=True)
class GlobalStorage:
    """Global storage for all handlers"""
    database = asyncio.run(DataBase().init(DATABASE_DIR))
    user_pool = asyncio.run(UserPool().init(USER_DIR))
    vector_database = VectorDatabase(
        path = VECTOR_DB_PATH, 
        collection_configs = [{
            "name": "doc_feature",
            "dimension": 768
        }],
        compile_config=getConf()["tiny_vectordb_compile_config"]
    )

    iconn = IServerConn()   # temporary, the endpoint will be set when server starts

    async def flush(self):
        """
        Commit and flush all changes to disk
        """
        await self.database.conn.commit()
        await self.user_pool.conn.commit()
        self.vector_database.commit()
    
    async def finalize(self):
        """
        Finalize the storage
        """
        await self.flush()
        await self.database.conn.close()
        await self.user_pool.conn.close()