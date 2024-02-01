from lires.api import ServerConn
from lires.utils import Timer
import asyncio
from .base import BaseConfig
import pytest

@pytest.fixture(scope="module")
def serverConn():
    config = BaseConfig()
    return ServerConn(config.admin_user["token"], "http://localhost:8080")

N_CONCURRENT = 10
SEMAPHORE = asyncio.Semaphore(N_CONCURRENT)
class TestStress:
    async def test_status(self, serverConn: ServerConn):
        async def makeRequest(conn: ServerConn) -> bool:
            try:
                async with SEMAPHORE:
                    await conn.status()
                return True
            except Exception as e:
                print(e)
                return False
        n_req = 100
        with Timer(f"{n_req} requests (concurrent {N_CONCURRENT})"):
            ret = await asyncio.gather(*[makeRequest(serverConn) for _ in range(n_req)])
        
        success = ret.count(True)
        assert success/len(ret) == 1.0, f"Success rate: {success}/{len(ret)}"