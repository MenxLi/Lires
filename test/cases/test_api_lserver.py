from lires.api.log import LServerConn
from .base import *

class TestAPI_LServer():
    async def test_lserver(self):
        conn = LServerConn()
        await conn.log("test", "INFO", "test", 0.0)
