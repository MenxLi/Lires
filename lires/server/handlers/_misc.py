"""
Miscellaneous handlers,
some small handlers that are not worth putting in a separate file
"""

from ._base import *
import json, time

class ReloadDBHandler(tornado.web.RequestHandler, RequestHandlerMixin):

    @keyRequired
    async def post(self):
        perm = self.permission
        self.setDefaultHeader()

        self.logger.info(f"Reload DB, from {perm['identifier']}({perm['enc_key']})")
        self.initdb()

        self.write("OK")

class StatusHandler(tornado.web.RequestHandler, RequestHandlerMixin):

    _init_time = time.time()

    async def _respond(self):
        self.setDefaultHeader()
        self.write(json.dumps({
            "status": "OK",
            "uptime": time.time() - self._init_time,
            "n_data": len(self.db),
        }))

    @keyRequired
    async def get(self):
        await self._respond()
    
    @keyRequired
    async def post(self):
        await self._respond()