import os, asyncio
from .collector import ArticleInfo
from lires.core.dataClass import DataBase
from lires.core.fileTools import addDocument
from lires.config import TMP_DIR

async def initDatabase(db_path = os.path.join(TMP_DIR, 'feed')):
    database = DataBase()
    await database.init(db_path)
    return database

async def toDatabase(database: DataBase, articles: list[ArticleInfo]):
    conn = database.conn
    new_articles = [
        article for article in articles
        if not (await database.has(article.id))
    ]

    await asyncio.gather(*[
        addDocument(
            db_conn = conn, 
            citation = article.bibtex,
            tags = article.tags,
            url = article.link,
            doc_info = { "uuid": article.id, },
            check_duplicate = False
        ) 
        for article in new_articles
    ])
    return
