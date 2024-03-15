import dataclasses

import asyncio
from lires.core.dataClass import DataBase
from lires.config import DATABASE_DIR, USER_DIR
from lires.user import UserPool
from lires.api import IServerConn
from lires.core.vector import initVectorDB

@dataclasses.dataclass(frozen=True)
class GlobalStorage:
    """Global storage for all handlers"""
    database = asyncio.run(DataBase().init(DATABASE_DIR))
    user_pool = asyncio.run(UserPool().init(USER_DIR))
    vector_database = initVectorDB(database.path.vector_db_file)
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