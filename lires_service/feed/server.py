
from lires.core.base import G
from lires.core.dataClass import DataPoint
from lires.api import RegistryConn
import asyncio
import fastapi
from pydantic import BaseModel
from .db import DataBase, initDatabase, toDatabase
from ..entry import startService

logger = G.loggers.get("feed")
g_warmup = False
app = fastapi.FastAPI()
registry = RegistryConn()

feed_db: DataBase

async def collectFeed():
    global feed_db
    from .collector import fetchArxiv
    articles = await fetchArxiv(
        max_results=100,
        search_query= "cat:cs.AI OR cat:cs.CV OR cat:stat.ML OR cat:cs.LG",
    )
    await toDatabase(feed_db, articles)
    await feed_db.commit()
    return

async def startCollectionLoop():
    await logger.info("Collecting feed...")
    try:
        await collectFeed()
        await logger.debug("Feed collected.")
    except Exception as e:
        await logger.error(f"Error in collecting feed: {e}")
    asyncio.get_event_loop().call_later(60*60*24, startCollectionLoop)

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

class FeesGetRequest(BaseModel):
    max_results: int = 10
    category: str = "arxiv->cat:cs.AI"
@app.post("/latest")
async def latest(req: FeesGetRequest):
    global feed_db
    uids = await feed_db.getIDByTags([req.category])
    uids = (await feed_db.conn.sortKeys(uids))[:req.max_results]
    dps = await feed_db.gets(uids)
    async def withAbstract(dp: DataPoint):
        ret = dp.summary.json()
        ret["abstract"] = await dp.fm.readAbstract()
        return ret
    return await asyncio.gather(*[withAbstract(dp) for dp in dps])

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