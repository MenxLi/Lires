"""
Miscellaneous handlers,
some small handlers that are not worth putting in a separate file
"""

from ._base import *
from lires import VERSION
import json, time

class ReloadDBHandler(tornado.web.RequestHandler, RequestHandlerMixin):

    @keyRequired
    async def post(self):
        user_info = self.user_info
        self.allowCORS()

        self.logger.info(f"Reload DB, from {user_info['name']}({user_info['enc_key']})")
        self.initdb()

        self.write("OK")

class StatusHandler(tornado.web.RequestHandler, RequestHandlerMixin):

    _init_time = time.time()

    async def _respond(self):
        self.allowCORS()
        self.write(json.dumps({
            "status": "OK",
            "version": VERSION,
            "uptime": time.time() - self._init_time,
            "n_data": len(self.db),
            "n_connections": len(self.connection_pool)
        }))

    @keyRequired
    async def get(self):
        await self._respond()
    
    @keyRequired
    async def post(self):
        await self._respond()