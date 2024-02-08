from lires.core.bibReader import parseBibtex
from lires.core.dbConn import DBConnection
from lires.core.fileTools import FileManipulator

bib_str = """
@article{test,
    title={test},
    year={2021},
    author={test},
    journal={test}
}
"""

async def test():
    conn = await FileManipulator.getDatabaseConnection("test_db_dir")
    bib = await parseBibtex(bib_str)
    uid = await conn.addEntry(
        title=bib["title"],
        year=bib["year"],
        authors=bib["authors"],
        publication=bib["publication"],
        tags=[],
        bibtex=bib_str
    )
    assert uid
    fm = await FileManipulator(uid).init(conn)
    await fm.setWebUrl("https://example.com")
    print(await fm.getWebUrl())
    print(await fm.getTags())
    await fm.deleteEntry()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test())