from .base import BaseConfig
from lires.api import IServerConn
import pytest

@pytest.fixture(scope="module")
def iconn():
    return IServerConn()
class TestIServer(BaseConfig):
    async def test_status(self, iconn: IServerConn):
        status = await iconn.status
        assert status is not None
        assert status["status"]

    async def test_featurize(self, iconn: IServerConn):
        feature = await iconn.featurize("Hello world")
        assert feature