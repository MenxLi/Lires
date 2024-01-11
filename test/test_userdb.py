import unittest
import subprocess
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
    
    def test_cmd(self):
        subprocess.check_call(["lrs-user", "add", "test2_username", "test2_password", "--admin", "--tags", "tag3", "tag4"])
        user2 = self.userdb.getUser("test2_username")
        self.assertTrue(user2 is not None)
        self.assertTrue(user2["is_admin"])
        self.assertEqual(user2["mandatory_tags"], ["tag3", "tag4"])
    
        subprocess.check_call(["lrs-user", "delete", "-u", "test2_username"])
        self.assertRaises(
            LiresError.LiresUserNotFoundError, 
            self.userdb.getUser, 
            "test2_username"
            )
    
        subprocess.check_call(["lrs-user", "add", "test3_username", "test2_password", "--admin", "--tags", "tag3", "tag4"])
        subprocess.check_call(["lrs-user", "update", "test3_username", "--name", "test3_new_name"])
        user3 = self.userdb.getUser("test3_username")
        self.assertEqual(user3["name"], "test3_new_name")
