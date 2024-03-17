from ._base import *
import json

class DatabaseKeysHandler(RequestHandlerBase):
    """ Get summary of the database """
    @keyRequired
    async def get(self):
        db = await self.db()
        self.write(json.dumps(await db.keys()))
        return
class DatabaseTagsHandler(RequestHandlerBase):
    """ Get summary of the database """
    @keyRequired
    async def get(self):
        db = await self.db()
        self.write(json.dumps(
            (await db.tags()).toOrderedList()
            ))
        return
class DatabaseUsageHandler(RequestHandlerBase):
    """ Get disk usage of the database """
    @keyRequired
    async def get(self):
        db = await self.db()
        self.write(json.dumps({
            "n_entries": await db.count(),
            "disk_usage": await db.diskUsage(),
            "disk_limit": (await self.userInfo())["max_storage"]
        }))
        return
