
"""
Data management / manipulation handlers
This are handlers to (partially) replace the file handlers in resbibman/server/handlers/file.py
Provides handers for adding, deleting, and modifying files/tags
"""

from ._base import *

class DataDeleteHandler(RequestHandlerBase, tornado.web.RequestHandler):
    def post(self):
        if not self.checkKey():
            raise tornado.web.HTTPError(403)
        self.setDefaultHeader()
        uuid = self.get_argument("uuid")
        if self.db.delete(uuid):
            self.logger.info(f"Deleted {uuid}")
        self.write("OK")
        return