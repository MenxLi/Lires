
import asyncio
from logging import Logger, getLogger
from uvicorn import Config, Server
from uvicorn.config import LOGGING_CONFIG
from fastapi import FastAPI

async def startService(
    app: FastAPI,
    logger: Logger = getLogger("default"),
    host: str = "127.0.0.1",
    port: int = 0,
):
    # disable default logging
    default_logging_config = LOGGING_CONFIG.copy()
    default_logging_config["loggers"]["uvicorn"]["handlers"] = []

    config = Config(
        app=app, 
        host=host, 
        port=port,
        access_log=False,
        workers=1,
        log_config=default_logging_config,
        )
    server = Server(config=config)

    if asyncio.iscoroutinefunction(logger.info):
        await logger.info(f"Starting service at: {'https' if config.is_ssl else 'http'}://{config.host}:{config.port}")
    else:
        logger.info(f"Starting service at: {'https' if config.is_ssl else 'http'}://{config.host}:{config.port}")

    await server.serve()