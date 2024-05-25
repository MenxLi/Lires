
import os
from .base import BaseConfig
from lires.config import LRS_HOME
from lires.core.dataClass import DataBase

class TestDBLoad(BaseConfig):

    async def test_database_init(self):
        db = await DataBase().init(os.path.join(LRS_HOME, "db_tmp"))
        assert db is not None
        await db.close()