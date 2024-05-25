"""
Utilities to load the database and other resources
"""

import os, shutil
from .core.base import LiresBase
from .core.dataClass import DataBase
from .config import DATABASE_HOME, USER_DIR
from .user import UserPool, LiresUser

import asyncio

class DatabasePool(LiresBase):
    def __init__(self, databse_home: str = DATABASE_HOME) -> None:
        super().__init__()
        self._home = databse_home

        self.__db_ins_cache: dict[int, DataBase] = {}
        self.__getting_db_lock = asyncio.Lock()
    
    async def get(self, user: LiresUser|int) -> DataBase:
        if not isinstance(user, int):
            user_id = user.id
        else:
            user_id = user

        async with self.__getting_db_lock:
            if not user_id in self.__db_ins_cache:
                database_dir = os.path.join(self._home, str(user_id))
                db = await DataBase().init(database_dir)
                self.__db_ins_cache[user_id] = db

        return self.__db_ins_cache[user_id]
    
    def __iter__(self):
        return iter(self.__db_ins_cache.values())
    
    async def commit(self):
        await asyncio.gather(*[db_ins.commit() for db_ins in self.__db_ins_cache.values()])
    
    async def close(self):
        await asyncio.gather(*[db_ins.close() for db_ins in self.__db_ins_cache.values()])
    
    async def preload(self, user_pool: UserPool):
        """ Load all databases to cache"""
        users = await user_pool.all()
        await asyncio.gather(*[self.get(user) for user in users])
    
    async def deleteDatabasePermanently(self, user: LiresUser|int):
        """
        Delete the database permanently! 
        Please be careful when using this method.
        """
        if not isinstance(user, int):
            user_id = user.id
        else:
            user_id = user
        db = await self.get(user_id)
        path_to_delete = db.path.main_dir

        await db.close()
        del self.__db_ins_cache[user_id]
        shutil.rmtree(path_to_delete)

async def initResources(pre_load: bool = False):
    user_pool = await UserPool().init(USER_DIR)
    db_pool = DatabasePool(DATABASE_HOME)
    if pre_load:
        await db_pool.preload(user_pool)
    return user_pool, db_pool