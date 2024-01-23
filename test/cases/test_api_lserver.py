from lires.api import LServerConnection
from .base import *

class TestAPI_LServer():
    async def test_lserver(self):
        conn = LServerConnection("localhost", 8730)
        await conn.log("test", "INFO", "test")
