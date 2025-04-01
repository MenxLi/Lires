from ._base import *
import json

class DatabaseKeysHandler(RequestHandlerBase):
    """ Get summary of the database """
    @authenticate()
    async def get(self):
        self.set_header("Content-Type", "application/json")
        db = await self.db()
        self.write(json.dumps(await db.keys()))
        return
class DatabaseTagsHandler(RequestHandlerBase):
    """ Get summary of the database """
    @authenticate()
    async def get(self):
        self.set_header("Content-Type", "application/json")
        db = await self.db()
        self.write(json.dumps(
            (await db.tags()).to_ordered_list()
            ))
        return
class DatabaseUsageHandler(RequestHandlerBase):
    """ Get disk usage of the database """
    @authenticate()
    async def get(self):
        self.set_header("Content-Type", "application/json")
        db = await self.db()
        self.write(json.dumps({
            "n_entries": await db.count(),
            "disk_usage": await db.disk_usage(),
            "disk_limit": (await self.user_info())["max_storage"]
        }))
        return
