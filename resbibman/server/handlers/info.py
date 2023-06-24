from ._base import *
import json
from resbibman.version import version_histories

class ChangelogHandler(tornado.web.RequestHandler, RequestHandlerBase):
    def get(self):
        self.setDefaultHeader()
        self.write(json.dumps(version_histories))