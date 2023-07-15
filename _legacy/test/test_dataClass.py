from baseTestSetup import *

class TestOfflineDataclass(TestBase):

    def test_databaseLoading(self):
        from resbibman.core.dataClass import DataBase
        db = DataBase()
        db.init(self.rbm_config["database"], force_offline=True)
        self.assertTrue(db.offline)


class TestOnlineDataclass(TestBase):

    @classmethod
    def setUpThisClass(cls):
        ...

    @classmethod
    def tearDownThisClass(cls):
        ...
