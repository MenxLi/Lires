
from lires.utils import TimeUtils
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

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.db: aiosqlite.Connection

    async def connect(self):
        self.db = await aiosqlite.connect(self.db_path)

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

    async def log(self, name: str, level: int, level_name: str, message: str):
        if self.db is None:
            await self.connect()

        await self.create_table(name)

        time = TimeUtils.nowStamp()
        time_str = TimeUtils.toStr(TimeUtils.stamp2Local(time))
        await self.db.execute(
            f"""
            INSERT INTO {name} VALUES (?, ?, ?, ?, ?)
            """,
            (time, time_str, level, level_name, message),
        )

    async def commit(self):
        await self.db.commit()

    async def close(self):
        await self.commit()
        await self.db.close()

    def __del__(self):
        asyncio.run(self.close())
