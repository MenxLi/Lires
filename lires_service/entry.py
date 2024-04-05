from __future__ import annotations

import asyncio
from logging import Logger, getLogger
from uvicorn import Config, Server
from uvicorn.config import LOGGING_CONFIG
from fastapi import FastAPI

from . import avaliablePort
from typing import TypedDict, Optional, TYPE_CHECKING
import uuid
from lires.config import getConf

if TYPE_CHECKING:
    from .registry.store import ServiceName
    from lires.api import RegistryConn

class RegisterSettings(TypedDict):
    registry: RegistryConn
    name: ServiceName
    description: str

async def startService(
    app: FastAPI,
    logger: Logger = getLogger("default"),
    host: str = "127.0.0.1",
    port: int = 0,
    register_settings: Optional[RegisterSettings] = None,
):
    # disable default logging
    default_logging_config = LOGGING_CONFIG.copy()
    default_logging_config["loggers"]["uvicorn"]["handlers"] = []

    if port <= 0:
        port = avaliablePort()

    config = Config(
        app=app, 
        host=host, 
        port=port,
        access_log=False,
        workers=1,
        log_config=default_logging_config,
        )
    server = Server(config=config)

    if register_settings is not None:
        await register_settings["registry"].register({
            "uid": uuid.uuid4().hex,
            "name": register_settings['name'],
            "endpoint": f"http://{host}:{port}",
            "description": register_settings["description"],
            "group": getConf()["group"],
        })

    if asyncio.iscoroutinefunction(logger.info):
        await logger.info(f"Starting service at: {'https' if config.is_ssl else 'http'}://{config.host}:{config.port}")
    else:
        logger.info(f"Starting service at: {'https' if config.is_ssl else 'http'}://{config.host}:{config.port}")

    await server.serve()