
from .base import BaseConfig
from lires.config import DATABASE_DIR
from lires.core.dataClass import DataBase

class TestDBLoad(BaseConfig):

    async def test_database_init(self):
        db = await DataBase().init(DATABASE_DIR)
        assert db is not None
        await db.conn.close()