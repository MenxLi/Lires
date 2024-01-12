"""
Miscellaneous handlers,
some small handlers that are not worth putting in a separate file
"""

from ._base import *
from lires import VERSION
from lires_server.types import ServerStatus
import json, time

class ReloadDBHandler(RequestHandlerBase):
    @keyRequired
    async def post(self):
        self.logger.warn("Reload database is deprecated.")
        self.write("OK")

class StatusHandler(RequestHandlerBase):

    _init_time = time.time()

    async def _respond(self):
        self.set_header("Content-Type", "application/json")
        status: ServerStatus = {
            "status": "online",
            "version": VERSION,
            "uptime": time.time() - self._init_time,
            "n_data": len(self.db),
            "n_connections": len(self.connection_pool)
        }
        self.write(json.dumps(status))

    @keyRequired
    async def get(self):
        await self._respond()
    
    @keyRequired
    async def post(self):
        await self._respond()