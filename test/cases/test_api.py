from .base import BaseConfig
from lires.api import IServerConn, ServerConn
import pytest

@pytest.fixture(scope="module")
def iconn():
    return IServerConn(
        endpoint="http://localhost:8731"
    )

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
    async def test_status(self, iconn: IServerConn):
        status = await iconn.status
        assert status is not None
        assert status["status"]

    async def test_featurize(self, iconn: IServerConn):
        feature = await iconn.featurize("Hello world")
        assert feature

class TestServer(BaseConfig):
    async def test_status(self, server_admin: ServerConn):
        status = await server_admin.status()
        assert status["status"] == "online"
    
    async def test_auth(self, server_admin: ServerConn, server_normal: ServerConn):
        user_info = await server_admin.authorize()
        assert user_info["username"] == self.admin_user["username"]
        assert user_info["is_admin"] == True

        user_info = await server_normal.authorize()
        assert user_info["username"] == self.normal_user["username"]
        assert user_info["is_admin"] == False