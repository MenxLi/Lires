import os, asyncio
from .collector import ArticleInfo
from lires.core.dataClass import DataBase
from lires.core.fileTools import addDocument
from lires.config import DATABASE_HOME
from lires.core.logger import LiresLogger

async def initDatabase(db_path = os.path.join(DATABASE_HOME, 'feed')):
    database = DataBase()
    await database.init(db_path)
    return database

async def toDatabase(database: DataBase, articles: list[ArticleInfo], logger: LiresLogger):
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
            check_duplicate = False, 
            remove_abstract = False
        ) 
        for article in new_articles
    ])
    await logger.info(f"Added {len(new_articles)} new articles to feed database")
    return

async def collectFeedCycle(feed_db: DataBase, logger: LiresLogger):
    from .collector import fetchArxiv

    await logger.info("Start collecting arxiv feed...")
    sleep_time = 0
    for cat in ["cs.CV", "cs.AI", "cs.LG", "cs.RO", "cs.ET", "cs.GL", "stat.ML", "stat.AP", "physics.med-ph", "eess.IV"]:
        def createThisFetchTaskFn():
            cat_enclose = cat
            async def _thisFetchFn():
                await logger.info(f"Fetching feed for arxiv:{cat_enclose}")
                try:
                    articles = await fetchArxiv(
                        max_results=50,
                        search_query= f"cat:{cat_enclose}",
                    )
                    await toDatabase(feed_db, articles, logger=logger)
                    await feed_db.commit()
                except Exception as e:
                    await logger.error(f"Error in fetching feed: {e}")
            return lambda: asyncio.get_event_loop().create_task(_thisFetchFn())
        
        # schedule the task later
        asyncio.get_event_loop().call_later(sleep_time, createThisFetchTaskFn())
        # call every 5 minutes, 
        # in order not to be banned by arxiv
        sleep_time += 60*5
    return