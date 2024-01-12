from lires.api import IServerConn

class TestIServer:
    def test_status(self):
        conn = IServerConn()
        status = conn.status
        assert status is not None
        assert status["status"]

    def test_featurize(self):
        conn = IServerConn()
        feature = conn.featurize("Hello world")
        assert feature