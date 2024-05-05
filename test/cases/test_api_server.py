
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
        endpoint="http://localhost:8080"
    )

@pytest.fixture(scope="module")
def server_normal():
    return ServerConn(
        token=BaseConfig().normal_user["token"],
        endpoint="http://localhost:8080"
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
            d_summary = await server_admin.updateEntry(
                None,
                bibtex=bibtex,
                tags=tags,
                url=url,
                )
            
            b_parser = BibParser()
            assert (await b_parser(d_summary.bibtex))[0] == (await b_parser(bibtex))[0]
            assert set(d_summary.tags) == set(tags)
            assert d_summary.url == url

            # update entry randomly
            uid = d_summary.uuid

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
            d_summary_update = await server_admin.updateEntry(
                uid,
                bibtex=bibtex,
                tags=new_tags,
                url=new_url
                )

            assert set(d_summary_update.tags) == set(new_tags)

        __this_dir = os.path.dirname(os.path.abspath(__file__))
        bibtex_case_file = os.path.join(__this_dir, "bibtex_cases.bib")
        with open(bibtex_case_file) as f:
            bibtex_cases = f.read().split("\n\n")
        
        for bibtex in bibtex_cases:
            tags = [randomAlphaNumeric(10) for _ in range(random.randint(1, 5))]
            url = randomAlphaNumeric(10)
            await _testOneEntry(bibtex, tags, url)

    async def test_uploadDocument(self, server_normal: ServerConn):
        def createNewEntry():
            bibtex = "@article{test, title={Test}, author={Test}}"
            tags = ["test"]
            url = "http://test.com"
            return server_normal.updateEntry( None,
                bibtex=bibtex,
                tags=tags,
                url=url
            )
        await createNewEntry()

        # make a fake document
        f_blob = randomAlphaNumeric(1000).encode()

        # get the first entry
        dp_id = (await server_normal.filter(max_results=1))['uids'][0]
        d_summary = await server_normal.uploadDocument(dp_id, f_blob, filename="test.pdf")
        assert d_summary.uuid == dp_id
        assert d_summary.has_file

        # remove the document
        d_summary = await server_normal.deleteDocument(dp_id)
        assert d_summary.uuid == dp_id
        assert not d_summary.has_file
    
    async def _getFirstEntry(self, server_normal: ServerConn):
        entry_id = (await server_normal.filter(max_results=1))['uids'][0]
        return await server_normal.reqDatapointSummary(entry_id)
    
    async def test_updateTag(self, server_normal: ServerConn):
        curr_data = await self._getFirstEntry(server_normal)
        dp_id = curr_data.uuid

        new_tag = randomAlphaNumeric(10)
        updated_tags = curr_data.tags + [new_tag]
        await server_normal.updateEntry(dp_id, tags = updated_tags)
        assert set((await server_normal.reqDatapointSummary(dp_id)).tags) == set(updated_tags)

        await server_normal.updateTagAll(new_tag, 'xxx_new')
        assert new_tag not in (curr_tags:=await server_normal.reqAllTags())
        assert 'xxx_new' in curr_tags
        await server_normal.deleteTagAll('xxx_new')
        assert 'xxx_new' not in (await server_normal.reqAllTags())

    async def test_updateNote(self, server_normal: ServerConn):
        # get the first entry
        note = randomAlphaNumeric(1000)
        dp_id = (await self._getFirstEntry(server_normal)).uuid
        await server_normal.updateDatapointNote(dp_id, note)
        assert await server_normal.reqDatapointNote(dp_id) == note

    async def test_updateAbstract(self, server_normal: ServerConn):
        # get the first entry
        dp_id = (await self._getFirstEntry(server_normal)).uuid
        abstract = randomAlphaNumeric(1000)
        await server_normal.updateDatapointAbstract(dp_id, abstract)
        assert await server_normal.reqDatapointAbstract(dp_id) == abstract
    
    async def test_deleteEntry(self, server_normal: ServerConn):
        dp_id = (await self._getFirstEntry(server_normal)).uuid
        await server_normal.deleteDatapoint(dp_id)
        assert dp_id not in (await server_normal.reqAllKeys())
