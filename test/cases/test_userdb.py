import subprocess
import pytest
from lires.core import LiresError
from lires.user import UsrDBConnection, UserPool, LiresUser
from lires.config import USER_DIR


@pytest.fixture(scope="module")
async def user_pool() -> UserPool:
    return await UserPool().init(USER_DIR)

@pytest.fixture(scope="module")
async def userdb() -> UsrDBConnection:
    return await UsrDBConnection(USER_DIR).init()

class TestUserDBConnection:
    async def test_insert(self, userdb: UsrDBConnection):
        await userdb.insert_user(
            username="test0_username", 
            password="test0_password",
            name="test0_name",
            is_admin=False,
            mandatory_tags=['tag0']
            )
        await userdb.insert_user(
            username="test1_username", 
            password="test1_password",
            name="test1_name",
            is_admin=True,
            mandatory_tags=["tag1", "tag2"]
            )

        assert await userdb.get_user("test0_username") is not None
        assert await userdb.get_user("test1_username") is not None

        with pytest.raises(LiresError.LiresUserDuplicationError):
            await userdb.insert_user(
                username="test0_username", 
                password="test0_password",
                name="test0_name",
                is_admin=False,
                mandatory_tags=['tag0']
            )
        await userdb.commit()
    
    async def test_cmd(self, userdb: UsrDBConnection):
        subprocess.check_call(["lrs-user", "add", "test2_username", "test2_password", "--admin", "--tags", "tag3", "tag4", "-m", "10m"])
        user2 = await userdb.get_user("test2_username")
        assert user2 is not None
        assert user2["is_admin"]
        assert user2["mandatory_tags"], ["tag3", "tag4"]
        assert user2["max_storage"], 10*1024*1024
    
        subprocess.check_call(["lrs-user", "delete", "-u", "test2_username", "-y"])
        with pytest.raises(LiresError.LiresUserNotFoundError):
            await userdb.get_user("test2_username")
    
        subprocess.check_call(["lrs-user", "add", "test3_username", "test3_password", "--admin", "--tags", "tag3", "tag4"])
        subprocess.check_call(["lrs-user", "update", "test3_username", "--name", "test3_new_name"])
        user3 = await userdb.get_user("test3_username")
        assert user3['name'] == "test3_new_name"
    
    async def test_userPool(self, user_pool: UserPool):
        _n_base_user = 2
        assert await user_pool.size() == 3 + _n_base_user
        all_users = await user_pool.all()
        assert (await all_users[0 + _n_base_user].info())['username'] == "test0_username"
        assert (await all_users[1 + _n_base_user].info())['username'] == "test1_username"
        assert (await all_users[2 + _n_base_user].info())['username'] == "test3_username"
    
        user1 = await user_pool.get_user_by_username("test1_username")
        assert user1 is not None
        user1_info = await user1.info()
        assert await user1.equal(await user_pool.get_user_by_id(user1_info['id']))
        assert await user1.equal(await user_pool.get_user_by_key(user1_info['enc_key']))

    async def test_finalize(self, user_pool: UserPool, userdb: UsrDBConnection):
        await user_pool.conn.close()
        await userdb.close()