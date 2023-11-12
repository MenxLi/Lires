from ._base import *
import json
from lires.version import VERSION_HISTORIES

class ChangelogHandler(tornado.web.RequestHandler, RequestHandlerMixin):
    def get(self):
        self.allowCORS()
        self.write(json.dumps(VERSION_HISTORIES))