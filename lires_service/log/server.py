from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager

import asyncio
from lires.api import RegistryConn
from lires.utils import BCOLORS
from .logger import DatabaseLogger, NAME_LEVEL
from ..entry import start_service

DATABASE_COMMIT_INTERVAL = 10
def schedule_next_commit():
    global logger
    if not logger.is_uptodate():
        # print("-------- Commit --------")
        asyncio.ensure_future(logger.commit())
    asyncio.get_event_loop().call_later(DATABASE_COMMIT_INTERVAL, schedule_next_commit)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global logger, registry
    await logger.connect()
    schedule_next_commit()
    yield
    await logger.close()
    await registry.withdraw()
    
app = FastAPI(lifespan=lifespan)
registry = RegistryConn()
logger: DatabaseLogger

ERROR_COLOR_MAP = {
    "DEBUG": BCOLORS.CYAN,
    "INFO": BCOLORS.GREEN,
    "WARNING": BCOLORS.YELLOW,
    "ERROR": BCOLORS.RED,
    "CRITICAL": BCOLORS.RED,
}

class LogRequest(BaseModel):
    level: str
    message: str
    timestamp: float
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
            "timestamp": None,
        }

    level_name = data["level"].upper()
    level = NAME_LEVEL[level_name]
    res = await logger.log(
        name = logger_name, 
        level = level, 
        level_name=level_name,
        message = data["message"],
        timestamp = data["timestamp"],
        )
    time = res[1]
    name_fmt = \
    f"{BCOLORS.BOLD}{BCOLORS.BLUE}{time}{BCOLORS.ENDC} {ERROR_COLOR_MAP.get(level_name, BCOLORS.WHITE)}{level_name}{BCOLORS.ENDC} " + \
    f"[{BCOLORS.DARKGRAY}{logger_name[:20].ljust(20)}{BCOLORS.ENDC}]"
    print(f"{name_fmt}: {data['message']}")
    return 

@app.get("/status")
async def status():
    return {"status": "ok"}

async def start_logger_server(file: str, host: str, port: int):
    global logger
    if not file:
        import os, time
        from lires.config import LOG_DIR
        # default to "lires-log_2024-12-31_23-59-59.sqlite[.<a-z>]"
        file = os.path.join(LOG_DIR, "lires-log_{}.sqlite".format(time.strftime("%Y-%m-%d_%H-%M-%S")))
        while True:
            if not os.path.exists(file):
                # touch file in advance, so less resource compete
                open(file, "w").close()
                break

            if file.endswith(".sqlite"):
                file += ".a"
            else:
                if file[-1] == "z":
                    file = file[:-1] + "a"
                else:
                    file = file[:-1] + chr(ord(file[-1]) + 1)
    
    # initialize the logger
    logger = DatabaseLogger(file)
    print("Logging to {}".format(file))
    
    # start the server
    await start_service(
        app = app,
        host = host,
        port = port,
        register_settings={
            "registry": registry,
            "name": "log",
            "description": "Log server",
        }
    )
