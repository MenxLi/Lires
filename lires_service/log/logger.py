
from lires.utils import TimeUtils
from typing import Optional
import aiosqlite

LEVEL_NAME = {
    0: "NOTSET",
    10: "DEBUG",
    20: "INFO",
    30: "WARNING",
    40: "ERROR",
    50: "CRITICAL",
}
NAME_LEVEL = {v: k for k, v in LEVEL_NAME.items()}
import aiosqlite
import asyncio

class DatabaseLogger:
    """
    A logger that saves log to a database
    Should be a singleton
    """

    lock = asyncio.Lock()
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.db: aiosqlite.Connection
        self.__is_uptodate = True

        # assure singleton
        assert not hasattr(self.__class__, "_logger_init_done"), "DatabaseLogger should be a singleton"
        setattr(self.__class__, "_logger_init_done", True)

    async def connect(self):
        self.db = await aiosqlite.connect(self.db_path)
    
    def isUpToDate(self):
        return self.__is_uptodate

    async def create_table(self, name: str):
        async with self.db.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {name} (
                time REAL, 
                time_str TEXT,
                level INTEGER,
                level_name TEXT,
                message TEXT
            )
            """
        ):
            pass

    async def log(self, name: str, level: int, level_name: str, message: str, timestamp: Optional[float] = None) -> tuple:
        if timestamp is None:
            timestamp = TimeUtils.nowStamp()
        time_str = TimeUtils.toStr(TimeUtils.stamp2Local(timestamp))
        async with self.lock:
            if self.db is None:
                await self.connect()

        await self.create_table(name)
        async with self.lock:
            await self.db.execute(
                f"""
                INSERT INTO {name} VALUES (?, ?, ?, ?, ?)
                """,
                entry := (timestamp, time_str, level, level_name, message)
            )
        self.__is_uptodate = False
        return entry

    async def commit(self):
        async with self.lock:
            await self.db.commit()
            self.__is_uptodate = True

    async def close(self):
        print("-------- Closing database... --------")
        await self.commit()
        await self.db.close()