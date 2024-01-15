
from .base import BaseConfig
from lires.config import DATABASE_DIR
from lires.core.dataClass import DataBase

class TestDBLoad(BaseConfig):

    def test_database_init(self):
        db = DataBase(DATABASE_DIR)
        assert db is not None