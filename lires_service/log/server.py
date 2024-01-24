from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

import asyncio
from lires.api import RegistryConn
from .logger import DatabaseLogger, NAME_LEVEL

app = FastAPI()
logger: DatabaseLogger

class LogRequest(BaseModel):
    level: str
    message: str
@app.post("/log/{logger_path}")
async def log(logger_path, request: LogRequest):
    global logger
    logger_name = logger_path
    assert logger_name != "__log_server__", "logger name cannot be __log_server__"

    try:
        data = request.dict()
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
    return 

@app.get("/status")
async def status():
    return {"status": "ok"}

DATABASE_COMMIT_INTERVAL = 10
async def periodicCommit():
    global logger
    if not logger.isUpToDate():
        print("-------- Commit --------")
        asyncio.create_task(logger.commit())
    asyncio.get_event_loop().call_later(DATABASE_COMMIT_INTERVAL, asyncio.create_task, periodicCommit())

@app.on_event("startup")
async def startup():
    global logger
    await logger.connect()
    await periodicCommit()

@app.on_event("shutdown")
async def shutdown():
    global logger
    await logger.close()
    
def startLoggerServer(file: str, host: str, port: int):
    global logger
    if not file:
        import os, time
        from lires.config import LOG_DIR
        file = os.path.join(LOG_DIR, "lires-log_{}.sqlite".format(time.strftime("%Y-%m-%d_%H-%M-%S")))
    
    if port <= 0:
        from lires.utils import getLocalIP
        _, spare_port = getLocalIP()
        port = spare_port

    # initialize the logger
    logger = DatabaseLogger(file)
    print("Logging to {}".format(file))

    import uuid
    RegistryConn().register_sync({
        "uid": uuid.uuid4().hex,
        "name": "log",
        "endpoint": f"http://{host}:{port}",
        "description": "Log server",
        "group": None,
    })

    uvicorn.run(
        app,
        host=host,
        port=port,
        workers=1,
        access_log=False,
    )