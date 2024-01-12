import subprocess
import pytest
from lires.core import LiresError
from lires.user import UsrDBConnection, UserPool, LiresUser
from lires.config import USER_DIR


@pytest.fixture(scope="module")
def user_pool() -> UserPool:
    return UserPool(USER_DIR)

@pytest.fixture(scope="module")
def userdb() -> UsrDBConnection:
    return UsrDBConnection(USER_DIR)

class TestUserDBConnection:
    def test_insert(self, userdb: UsrDBConnection):
        userdb.insertUser(
            username="test0_username", 
            password="test0_password",
            name="test0_name",
            is_admin=False,
            mandatory_tags=['tag0']
            )
        userdb.insertUser(
            username="test1_username", 
            password="test1_password",
            name="test1_name",
            is_admin=True,
            mandatory_tags=["tag1", "tag2"]
            )

        assert userdb.getUser("test0_username") is not None
        assert userdb.getUser("test1_username") is not None

        with pytest.raises(LiresError.LiresUserDuplicationError):
            userdb.insertUser(
                username="test0_username", 
                password="test0_password",
                name="test0_name",
                is_admin=False,
                mandatory_tags=['tag0']
            )
        userdb.commit()
    
    def test_cmd(self, userdb: UsrDBConnection):
        subprocess.check_call(["lrs-user", "add", "test2_username", "test2_password", "--admin", "--tags", "tag3", "tag4"])
        user2 = userdb.getUser("test2_username")
        assert user2 is not None
        assert user2["is_admin"]
        assert user2["mandatory_tags"], ["tag3", "tag4"]
    
        subprocess.check_call(["lrs-user", "delete", "-u", "test2_username"])
        with pytest.raises(LiresError.LiresUserNotFoundError):
            userdb.getUser("test2_username")
    
        subprocess.check_call(["lrs-user", "add", "test3_username", "test3_password", "--admin", "--tags", "tag3", "tag4"])
        subprocess.check_call(["lrs-user", "update", "test3_username", "--name", "test3_new_name"])
        user3 = userdb.getUser("test3_username")
        assert user3['name'] == "test3_new_name"
    
    def test_userPool(self, user_pool: UserPool, userdb: UsrDBConnection):
        _n_base_user = 2
        assert len(user_pool) == 3 + _n_base_user
        assert user_pool[0 + _n_base_user].info()['username'] == "test0_username"
        assert user_pool[1 + _n_base_user].info()['username'] == "test1_username"
        assert user_pool[2 + _n_base_user].info()['username'] == "test3_username"
    
        user1 = user_pool.getUserByUsername("test1_username")
        assert user1 is not None
        assert user_pool.getUserById(user1.info()['id']) == user1
        assert user_pool.getUserByKey(user1.info()['enc_key']) == user1
