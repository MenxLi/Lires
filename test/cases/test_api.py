import unittest
from lires.api import IServerConn

class TestIServer(unittest.TestCase):
    def test_status(self):
        conn = IServerConn()
        status = conn.status
        assert status is not None
        self.assertTrue(status["status"])
        self.assertTrue(status["device"] != "")

    def test_featurize(self):
        conn = IServerConn()
        feature = conn.featurize("Hello world")
        self.assertIsNotNone(feature)