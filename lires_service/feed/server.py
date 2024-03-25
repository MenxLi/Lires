
from lires.core.base import G
from lires.core.dataClass import DataPoint
from lires.api import RegistryConn
import asyncio
import fastapi
from pydantic import BaseModel
from typing import Optional
from .db import DataBase, initDatabase, toDatabase
from ..entry import startService

logger = G.loggers.get("feed")
g_warmup = False
app = fastapi.FastAPI()
registry = RegistryConn()

feed_db: DataBase

async def collectFeedCircle():
    global feed_db
    from .collector import fetchArxiv

    await logger.info("Start collecting feed...")
    sleep_time = 0
    for cat in ["cs.AI", "cs.CV", "cs.LG", "cs.RO", "cs.ET", "cs.GL", "stat.ML", "stat.AP", "physics.med-ph", "eess.IV"]:
        async def _thisFetch():
            try:
                articles = await fetchArxiv(
                    max_results=50,
                    search_query= f"cat:{cat}",
                )
                await toDatabase(feed_db, articles)
                await feed_db.commit()
            except Exception as e:
                await logger.error(f"Error in fetching feed: {e}")
        
        # schedule the task later
        asyncio.get_event_loop().call_later(sleep_time, _thisFetch)
        # call every 5 minutes, 
        # in order not to be banned by arxiv
        sleep_time += 60*5
    return

async def startCollectionLoop():
    await logger.info("Collecting feed...")
    await collectFeedCircle()

    # update every 12 hours
    asyncio.get_event_loop().call_later(60*60*12, startCollectionLoop)

@app.on_event("shutdown")
async def shutdown():
    await feed_db.close()
    await registry.withdraw()

@app.on_event("startup")
async def startup():
    global logger, registry, feed_db
    feed_db = await initDatabase()
    await startCollectionLoop()

@app.get("/status")
def status():
    return {"status": "ok"}

class FeedGetRequest(BaseModel):
    max_results: int = 10
    category: str = "arxiv->cat:cs.AI"
    time_after: Optional[float] = None
    time_before: Optional[float] = None
@app.post("/query")
async def query(req: FeedGetRequest):
    global feed_db
    await logger.info(f"Query: {req}")
    uids = await feed_db.getIDByTags([req.category])
    uids = await feed_db.conn.filter(time_import=(req.time_after, req.time_before), from_uids=uids)
    uids = (await feed_db.conn.sortKeys(uids))[:req.max_results]
    dps = await feed_db.gets(uids)
    async def withAbstract(dp: DataPoint):
        ret = dp.summary.json()
        ret["abstract"] = await dp.fm.readAbstract()
        return ret
    return await asyncio.gather(*[withAbstract(dp) for dp in dps])

@app.get("/categories")
async def categories():
    global feed_db
    return await feed_db.tags()

async def startServer(
    host: str = "0.0.0.0",
    port: int = -1,
):

    from .. import avaliablePort
    if port <= 0:
        port = avaliablePort()

    import uuid
    await registry.register({
        "uid": uuid.uuid4().hex,
        "name": "feed",
        "endpoint": f"http://{host}:{port}",
        "description": "LiresFeed server",
        "group": None
    })

    await startService(app, logger, host, port)

if __name__ == "__main__":
    import asyncio
    asyncio.run(startServer())