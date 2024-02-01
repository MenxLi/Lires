
from .base import BaseConfig
from lires.config import DATABASE_DIR
from lires.core.dataClass import DataBase
import asyncio

class TestDBLoad(BaseConfig):

    async def test_database_init(self):
        db = await DataBase().init(DATABASE_DIR)
        assert db is not None
        await db.conn.close()

        # we may emit some logs without waiting, 
        # so we need to wait for a while 
        # to make sure the coroutine is finished
        await asyncio.sleep(0.1)