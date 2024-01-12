from lires.api import IServerConn

class TestIServer:
    async def test_status(self):
        conn = IServerConn()
        status = await conn.status
        assert status is not None
        assert status["status"]

    async def test_featurize(self):
        conn = IServerConn()
        feature = await conn.featurize("Hello world")
        assert feature