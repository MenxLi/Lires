"""
Miscellaneous handlers,
some small handlers that are not worth putting in a separate file
"""

from ._base import *

class ReloadDBHandler(tornado.web.RequestHandler, RequestHandlerMixin):
    def post(self):
        perm = self.checkKey()
        self.setDefaultHeader()

        self.logger.info(f"Reload DB, from {perm['identifier']}({perm['enc_key']})")
        self.initdb()

        self.write("OK")