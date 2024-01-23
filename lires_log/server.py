import aiohttp.web
import asyncio
import argparse
from .logger import DatabaseLogger, NAME_LEVEL

logger: DatabaseLogger

async def log(request: aiohttp.web.Request):
    global logger
    logger_name = request.match_info["logger"]

    if logger is None:
        return aiohttp.web.Response(status=404)
    else:
        data = await request.json()

        level_name = data["level"].upper()
        level = NAME_LEVEL[level_name]

        await logger.log(
            name = logger_name, 
            level = level, 
            level_name=level_name,
            message = data["message"]
            )
        await logger.commit()
        print(f"[{logger_name}] {level_name}: {data['message']}")
        return aiohttp.web.Response(status=200)
    
def startLoggerServer(file: str, host: str, port: int):
    global logger
    logger = DatabaseLogger(file)
    asyncio.run(logger.connect())

    app = aiohttp.web.Application()
    app.add_routes([aiohttp.web.post("/log/{logger}", log)])

    aiohttp.web.run_app(
        app, 
        host=host, 
        port=port,
        )