import subprocess
import pytest
from lires.core import LiresError
from lires.user.conn import UsrDBConnection
from lires.config import USER_DIR

g_userdb = UsrDBConnection(USER_DIR)
class TestUserDBConnection:
    def test_insert(self):
        g_userdb.insertUser(
            username="test0_username", 
            password="test0_password",
            name="test0_name",
            is_admin=False,
            mandatory_tags=['tag0']
            )
        g_userdb.insertUser(
            username="test1_username", 
            password="test1_password",
            name="test1_name",
            is_admin=True,
            mandatory_tags=["tag1", "tag2"]
            )

        assert g_userdb.getUser("test0_username") is not None
        assert g_userdb.getUser("test1_username") is not None

        with pytest.raises(LiresError.LiresUserDuplicationError):
            g_userdb.insertUser(
                username="test0_username", 
                password="test0_password",
                name="test0_name",
                is_admin=False,
                mandatory_tags=['tag0']
            )
        g_userdb.commit()
    
    def test_cmd(self):
        subprocess.check_call(["lrs-user", "add", "test2_username", "test2_password", "--admin", "--tags", "tag3", "tag4"])
        user2 = g_userdb.getUser("test2_username")
        assert user2 is not None
        assert user2["is_admin"]
        assert user2["mandatory_tags"], ["tag3", "tag4"]
    
        subprocess.check_call(["lrs-user", "delete", "-u", "test2_username"])
        with pytest.raises(LiresError.LiresUserNotFoundError):
            g_userdb.getUser("test2_username")
    
        subprocess.check_call(["lrs-user", "add", "test3_username", "test2_password", "--admin", "--tags", "tag3", "tag4"])
        subprocess.check_call(["lrs-user", "update", "test3_username", "--name", "test3_new_name"])
        user3 = g_userdb.getUser("test3_username")
        assert user3['name'] == "test3_new_name"
