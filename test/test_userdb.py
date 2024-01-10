import unittest
from lires.core import LiresError
from lires.user.conn import UsrDBConnection
from lires.confReader import USER_DIR

class TestUserDBConnection(unittest.TestCase):
    def setUp(self) -> None:
        self.userdb = UsrDBConnection(USER_DIR)

    def test_insert(self):
        self.userdb.insertUser(
            username="test0_username", 
            password="test0_password",
            name="test0_name",
            is_admin=False,
            mandatory_tags=['tag0']
            )
        self.userdb.insertUser(
            username="test1_username", 
            password="test1_password",
            name="test1_name",
            is_admin=True,
            mandatory_tags=["tag1", "tag2"]
            )

        self.assertTrue(self.userdb.getUser("test0_username") is not None)
        self.assertTrue(self.userdb.getUser("test1_username") is not None)

        self.assertRaises(LiresError.LiresUserDuplicationError, self.userdb.insertUser,
            username="test0_username", 
            password="test0_password",
            name="test0_name",
            is_admin=False,
            mandatory_tags=['tag0']
            )
        
