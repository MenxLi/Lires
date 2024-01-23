import aiohttp.web
import aiohttp.web_exceptions
import asyncio
from .logger import DatabaseLogger, NAME_LEVEL

logger: DatabaseLogger

async def log(request: aiohttp.web.Request):
    global logger, __is_database_uptodate
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

DATABASE_COMMIT_INTERVAL = 10
def periodicCommit():
    global logger
    if not logger.isUpToDate():
        print("-------- Commit --------")
        asyncio.create_task(logger.commit())
    asyncio.get_event_loop().call_later(DATABASE_COMMIT_INTERVAL, periodicCommit)
    
async def startLoggerServer(file: str, host: str, port: int):
    global logger

    # the logger
    logger = DatabaseLogger(file)
    await logger.connect()

    app = aiohttp.web.Application()
    app.add_routes([aiohttp.web.post("/log/{logger}", log)])
    # aiohttp.web.run_app( app, host=host, port=port,)

    asyncio.get_event_loop().call_later(3, periodicCommit)
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, host, port)
    await site.start()
    print("======== Logger server started at {}========".format(site.name))
    print("Database file: {}".format(file))
    await asyncio.Event().wait()