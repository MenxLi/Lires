from __future__ import annotations

import asyncio
import signal
from logging import Logger, getLogger
from uvicorn import Config, Server
from uvicorn.config import LOGGING_CONFIG
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from . import avaliablePort
from typing import TypedDict, Optional, TYPE_CHECKING, Coroutine, Callable
import uuid
from lires.config import getConf, LRS_KEY

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

    def makeCoro(func: Callable) -> Callable[..., Coroutine]:
        if asyncio.iscoroutinefunction(func):
            return func
        else:
            async def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper

    if LRS_KEY:
        @app.middleware("http")
        async def interserviceVerification(request: Request, call_next):
            if request.method == "OPTIONS":
                return await call_next(request)
            if (auth_header:=request.headers.get("Authorization")) != f'Bearer {LRS_KEY}':
                await makeCoro(logger.debug)(f'Reject unauthorized access: {auth_header}')
                return JSONResponse(content={"detail": "Invalid authorization"}, status_code=401)
            return await call_next(request)

    if register_settings is not None:
        await register_settings["registry"].register({
            "uid": uuid.uuid4().hex,
            "name": register_settings['name'],
            "endpoint": f"http://{host}:{port}",
            "description": register_settings["description"],
            "group": getConf()["group"],
        })

    await makeCoro(logger.info)(f"Starting service at: {'https' if config.is_ssl else 'http'}://{config.host}:{config.port}")

    async def shutdown():
        await server.shutdown()
    signal.signal(signal.SIGINT, lambda sig, frame: shutdown)
    await server.serve()