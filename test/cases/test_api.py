from .base import BaseConfig
from lires.api import IServerConn, ServerConn
import pytest

@pytest.fixture(scope="module")
def iconn():
    return IServerConn()

@pytest.fixture(scope="module")
def server_admin():
    return ServerConn(
        token=BaseConfig().admin_user["token"],
        server_url="http://localhost:8080"
    )

@pytest.fixture(scope="module")
def server_normal():
    return ServerConn(
        token=BaseConfig().normal_user["token"],
        server_url="http://localhost:8080"
    )

class TestIServer(BaseConfig):
    async def test_status(self):
        conn = IServerConn()
        status = await conn.status
        assert status is not None
        assert status["status"]

    async def test_featurize(self):
        conn = IServerConn()
        feature = await conn.featurize("Hello world")
        assert feature

class TestServer(BaseConfig):
    async def test_status(self, server_admin: ServerConn):
        status = await server_admin.status()
        assert status["status"] == "online"