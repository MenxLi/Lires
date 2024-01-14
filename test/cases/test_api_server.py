
from .base import BaseConfig
from lires.api import ServerConn
import pytest

@pytest.fixture(scope="module")
def server_admin():
    return ServerConn(
        token=BaseConfig().admin_user["token"],
        server_url="http://localhost:8080"
    )

@pytest.fixture(scope="module")
def server_normal():
    return ServerConn(
        token=BaseConfig().normal_user["token"],
        server_url="http://localhost:8080"
    )

class TestServer(BaseConfig):
    async def test_status(self, server_admin: ServerConn):
        status = await server_admin.status()
        assert status["status"] == "online"
    
    async def test_auth(self, server_admin: ServerConn, server_normal: ServerConn):
        user_info = await server_admin.authorize()
        assert user_info["username"] == self.admin_user["username"]
        assert user_info["is_admin"] == True

        user_info = await server_normal.authorize()
        assert user_info["username"] == self.normal_user["username"]
        assert user_info["is_admin"] == False
    
    async def test_updateEntry(self, server_admin: ServerConn):
        d_info = await server_admin.updateEntry(
            None,
            bibtex="""
            @article{test,
                title={Hello world},
                author={John Doe},
                year={2020},
                journal={Journal of Test},
                volume={1},
                number={1},
                pages={1--10}
            }
            """,
            tags=["test"],
            url="https://example.com",
            )
        bibtex = d_info["bibtex"]
        uid = d_info["uuid"]
        tags = d_info["tags"]
        url = d_info["url"]

        assert uid 
        assert tags == ["test"]
        assert url == "https://example.com"

        # test update
        d_info_update = await server_admin.updateEntry(
            uid,
            bibtex=bibtex,
            tags=tags + ["test2"],
            url=None,
            )
        assert set(d_info_update["tags"]) == set(["test", "test2"])
