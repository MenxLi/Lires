"""
Miscellaneous handlers,
some small handlers that are not worth putting in a separate file
"""

from ._base import *
from lires import VERSION
from lires_server.types import ServerStatus
from lires.user import UserInfo
import json, time

class StatusHandler(RequestHandlerBase):

    _init_time = time.time()

    async def _respond(self, user_info: UserInfo):
        self.set_header("Content-Type", "application/json")
        db = await self.db()
        status: ServerStatus = {
            "status": "online",
            "version": VERSION,
            "uptime": time.time() - self._init_time,
            "n_data": await db.count(),
            "n_connections": len(self.connectionsByUserID(user_info["id"])),
            "n_connections_all": len(self.connection_pool),
        }
        self.write(json.dumps(status))

    @keyRequired
    async def get(self):
        await self._respond(await self.userInfo())
    
    @keyRequired
    async def post(self):
        await self._respond(await self.userInfo())

class DatabaseDownloadHandler(RequestHandlerBase):

    @keyRequired
    async def get(self):
        user_info = await self.userInfo()
        db = await self.db()
        self.set_header("Content-Type", "application/octet-stream")
        self.set_header("Content-Disposition", f"attachment; filename=\"{user_info['username']}.lires.sqlite\"")
        self.write(await db.dump())