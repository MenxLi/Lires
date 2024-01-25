
from .base import BaseConfig
from lires.api import ServerConn
from lires.core.bibReader import BibParser
from lires.utils import randomAlphaNumeric
import random, os
import pytest
import pybtex.database

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

        async def _testOneEntry(bibtex: str, tags: list, url: str):
            d_info = await server_admin.updateEntry(
                None,
                bibtex=bibtex,
                tags=tags,
                url=url,
                )
            
            b_parser = BibParser()
            assert (await b_parser(d_info.bibtex))[0] == (await b_parser(bibtex))[0]
            assert set(d_info.tags) == set(tags)
            assert d_info.url == url

            # update entry randomly
            uid = d_info.uuid

            new_bibtex = pybtex.database.parse_string(bibtex, bib_format="bibtex")
            _key = list(new_bibtex.entries.keys())[0]
            def _changeTitle(): 
                new_bibtex.entries[_key].fields["title"] = randomAlphaNumeric(10)
            def _changeYear():
                new_bibtex.entries[_key].fields["year"] = str(random.randint(1000, 3000))
            def _changeAuthor():
                ...
            random.choice([_changeTitle, _changeYear, _changeAuthor])()
            random.choice([_changeTitle, _changeYear, _changeAuthor])()
            new_bibtex = new_bibtex.to_string("bibtex")

            # update tags randomly
            new_tags = tags.copy()
            if random.random() > 0.5:
                new_tags.append(randomAlphaNumeric(10))
            else:
                new_tags.remove(random.choice(new_tags))
            
            # update url randomly
            new_url = randomAlphaNumeric(10) if random.random() > 0.5 else None
                
            # test update
            d_info_update = await server_admin.updateEntry(
                uid,
                bibtex=bibtex,
                tags=new_tags,
                url=new_url
                )

            assert set(d_info_update.tags) == set(new_tags)

        __this_dir = os.path.dirname(os.path.abspath(__file__))
        bibtex_case_file = os.path.join(__this_dir, "bibtex_cases.bib")
        with open(bibtex_case_file) as f:
            bibtex_cases = f.read().split("\n\n")
        
        for bibtex in bibtex_cases:
            tags = [randomAlphaNumeric(10) for _ in range(random.randint(1, 5))]
            url = randomAlphaNumeric(10)
            await _testOneEntry(bibtex, tags, url)
