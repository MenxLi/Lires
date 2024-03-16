"""
Utilities to load the database and other resources
"""

import os, dataclasses
from .core.base import LiresBase
from .core.dataClass import DataBase
from .core.vector import initVectorDB
from .config import DATABASE_HOME, USER_DIR
from .user import UserPool, LiresUser

from tiny_vectordb import VectorDatabase
import asyncio

@dataclasses.dataclass(frozen=True)
class DatabaseInstance:
    database: DataBase
    vector_db: VectorDatabase
    async def close(self):
        await self.database.conn.close()
        self.vector_db.disk_io.conn.close()

async def loadDatabaseInstance(user_id: int, database_home: str):
    database_dir = os.path.join(database_home, str(user_id))
    db = await DataBase().init(database_dir)
    vec_db = initVectorDB(db.path.vector_db_file)
    return DatabaseInstance(db, vec_db)

class DatabasePool(LiresBase):
    def __init__(self, databse_home: str = DATABASE_HOME) -> None:
        super().__init__()
        self.__db_ins_cache: dict[int, DatabaseInstance] = {}
        self._home = databse_home
    
    async def get(self, user: LiresUser) -> DatabaseInstance:
        if not user.id in self.__db_ins_cache:
            db_ins = await loadDatabaseInstance(user.id, self._home)
            self.__db_ins_cache[user.id] = db_ins
        return self.__db_ins_cache[user.id]
    
    async def close(self):
        await asyncio.gather(*[db_ins.close() for db_ins in self.__db_ins_cache.values()])
    
    async def preload(self, user_pool: UserPool):
        """ Load all databases to cache"""
        users = await user_pool.all()
        await asyncio.gather(*[self.get(user) for user in users])

async def initResources(pre_load: bool = True):
    user_pool = await UserPool().init(USER_DIR)
    db_pool = DatabasePool(DATABASE_HOME)
    if pre_load:
        await db_pool.preload(user_pool)
    return user_pool, db_pool