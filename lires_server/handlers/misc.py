"""
Miscellaneous handlers,
some small handlers that are not worth putting in a separate file
"""

from ._base import *
from lires import VERSION
from lires_server.types import ServerStatus
import json, time

class StatusHandler(RequestHandlerBase):

    _init_time = time.time()

    async def _respond(self):
        self.set_header("Content-Type", "application/json")
        db = await self.db()
        status: ServerStatus = {
            "status": "online",
            "version": VERSION,
            "uptime": time.time() - self._init_time,
            "n_data": await db.count(),
            "n_connections": len(self.connection_pool)
        }
        self.write(json.dumps(status))

    @keyRequired
    async def get(self):
        await self._respond()
    
    @keyRequired
    async def post(self):
        await self._respond()
