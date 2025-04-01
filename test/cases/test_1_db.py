
from lires.core.dbConn import DBConnection
from lires.core.dataClass import DataBase
from lires.config import LRS_HOME
import pytest, os, asyncio

db_dir = os.path.join(LRS_HOME, "db_tmp")
@pytest.fixture(scope="module")
def conn():
    return DBConnection(db_dir)

class TestDB:
    def test_init(self, conn: DBConnection):
        asyncio.run(conn.init())
    
    def test_db_search(self, conn: DBConnection):
        async def _test():
            uid0 = await conn.add_entry(
                bibtex="",
                dtype="article",
                title="test title0",
                year = "2021",
                publication = "test publication0",
                authors = ["author0", "author1"],
                tags = ["tag0", "tag1->tag2", 'tag3->tag4'],
                url = "https://www.google.com",
                abstract = "This is a test abstract", 
                comments = "This is a test comment",
            )
            assert uid0
            assert (raw := await conn.get(uid0))
            assert raw["title"] == "test title0"

            uid1 = await conn.add_entry(
                bibtex="",
                dtype="inproceedings",
                title="test title1",
                year = 2021,
                publication = "test publication1",
                authors = ["author0", "author2 fam2", "fam3,author3"],
                tags = ["tag0", "tag1", 'tag3->tag5'],
                url = "https://www.google.com",
                abstract = "This is a test abstract", 
                comments = "This is second test comment",
            )

            search_res = await conn.filter( title="test Title1", ignore_case=True)
            assert len(search_res) == 1
            assert search_res[0] == uid1

            assert len(await conn.filter( title="est titl", ignore_case=False, strict=False))==2

            search_res = await conn.filter( tags = ["tag1"],)
            assert search_res[0] == uid1

            search_res = await conn.filter( tags = ["tag0"],)
            assert len(search_res) == 2

            # search_res = await conn.filter( tags = ["tag0", "tag1"],)
            # assert len(search_res) == 1

            assert len(await conn.filter(year=2021)) == len(await conn.filter(year=(2021, None))) == len(await conn.filter(year=(None, 2022))) == 2
            assert len(await conn.filter(year=(None,2020))) == 0

            assert (await conn.filter( note="second", strict=False )) == [uid1]

            assert (await conn.filter( tags = ["tag1"], authors=["author1"])) == []

            assert (await conn.filter( tags = ["tag0"], from_uids=[uid0])) == [uid0]

            assert set(await conn.tags()) == set(("tag0", "tag1", "tag1->tag2", "tag3->tag4", "tag3->tag5"))
            assert set(await conn.authors()) == set(("author0", "author1", "fam2, author2", "fam3, author3"))

            await conn.commit()
        
        asyncio.run(_test())
    
    def test_database_search(self):
        async def _test():
            database = await DataBase().init(db_dir)
            assert len(await database.data_from_tags(['tag1', 'tag0'])) == 2
            assert len(await database.data_from_tags(['tag0'])) == 2
            assert len(await database.data_from_tags(['tag1'])) == 2
            assert len(await database.data_from_tags(['tag1->tag2'])) == 1
            assert len(await database.data_from_tags(['tag3'])) == 2
            assert len(await database.data_from_tags(['tag3', 'tag1'])) == 2
            await database.close()
        asyncio.run(_test())
    
    def test_finalize(self, conn: DBConnection):
        asyncio.run(conn.commit())
        asyncio.run(conn.close())
