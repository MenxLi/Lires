import aiohttp.web
import aiohttp.web_exceptions
import asyncio
from lires.api import RegistryConn
from .logger import DatabaseLogger, NAME_LEVEL

logger: DatabaseLogger

async def log(request: aiohttp.web.Request):
    global logger
    logger_name = request.match_info["logger"]
    assert logger_name != "__log_server__", "logger name cannot be __log_server__"

    try:
        data = await request.json()
    except Exception as _excp:
        # connection reset by peer, maybe
        logger_name = "__log_server__"
        data = {
            "level": "ERROR",
            "message": "Failed to parse json: " + str(_excp),
        }

    level_name = data["level"].upper()
    level = NAME_LEVEL[level_name]
    await logger.log(
        name = logger_name, 
        level = level, 
        level_name=level_name,
        message = data["message"]
        )
    print(f"[{logger_name}] {level_name}: {data['message']}")
    return aiohttp.web.Response(status=200)

async def status(_: aiohttp.web.Request):
    return aiohttp.web.Response(status=200)

DATABASE_COMMIT_INTERVAL = 10
def periodicCommit():
    global logger
    if not logger.isUpToDate():
        print("-------- Commit --------")
        asyncio.create_task(logger.commit())
    asyncio.get_event_loop().call_later(DATABASE_COMMIT_INTERVAL, periodicCommit)
    
async def startLoggerServer(file: str, host: str, port: int):
    global logger
    if not file:
        import os, time
        from lires.config import LOG_DIR
        file = os.path.join(LOG_DIR, "lires-log_{}.sqlite".format(time.strftime("%Y-%m-%d_%H-%M-%S")))
    
    if port <= 0:
        from lires.utils import getLocalIP
        _, spare_port = getLocalIP()
        port = spare_port

    # the logger
    logger = DatabaseLogger(file)
    await logger.connect()

    app = aiohttp.web.Application()
    app.add_routes([aiohttp.web.post("/log/{logger}", log)])
    app.add_routes([aiohttp.web.get("/status", status)])
    # aiohttp.web.run_app( app, host=host, port=port,)

    asyncio.get_event_loop().call_later(3, periodicCommit)
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, host, port)
    await site.start()
    print("======== Logger server started at {}========".format(site.name))
    print("Database file: {}".format(file))

    await RegistryConn().register({
        "name": "log",
        "endpoint": f"http://{host}:{port}",
        "description": "Log server",
        "group": None,
    })
    await asyncio.Event().wait()