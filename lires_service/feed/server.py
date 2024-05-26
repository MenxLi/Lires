
from contextlib import asynccontextmanager
from lires.core.base import G
from lires.core.dataClass import DataPoint
from lires.api import RegistryConn
import asyncio
import fastapi
from pydantic import BaseModel
from typing import Optional
from .db import DataBase, initDatabase, collectFeedCycle
from ..entry import startService

async def startCollectionLoop():
    await logger.info("Collecting feed...")
    await collectFeedCycle(feed_db, logger=logger)
    createTaskFn = lambda: asyncio.get_event_loop().create_task(startCollectionLoop())

    # update every 12 hours
    asyncio.get_event_loop().call_later(60*60*12, createTaskFn)

@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    global logger, registry, feed_db
    feed_db = await initDatabase()
    await startCollectionLoop()
    yield
    await feed_db.close()
    await registry.withdraw()

logger = G.loggers.get("feed")
g_warmup = False
app = fastapi.FastAPI(lifespan=lifespan)
registry = RegistryConn()

feed_db: DataBase


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
    uids = (await feed_db.conn.sortKeys(uids, sort_by='time_import', reverse=True))[:req.max_results]
    dps = await feed_db.gets(uids, sort_by='time_import', reverse=True)
    async def withAbstract(dp: DataPoint):
        ret = dp.summary.json()
        ret["abstract"] = await dp.fm.readAbstract()
        return ret
    return await asyncio.gather(*[withAbstract(dp) for dp in dps])

@app.get("/categories")
async def categories():
    global feed_db
    # return await feed_db.tags()
    return [f'arxiv->{cat}' for cat in ["cs.CV", "cs.AI", "cs.LG", "cs.RO", "cs.ET", "cs.GL", "stat.ML", "stat.AP", "physics.med-ph", "eess.IV"]]

async def startServer(
    host: str = "0.0.0.0",
    port: int = -1,
):
    await startService(
        app, logger, host, port, 
        register_settings={
            "registry": registry,
            "name": "feed",
            "description": "LiresFeed server",
        })

if __name__ == "__main__":
    import asyncio
    asyncio.run(startServer())