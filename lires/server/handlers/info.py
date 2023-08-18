from ._base import *
import json
from lires.version import version_histories

class ChangelogHandler(tornado.web.RequestHandler, RequestHandlerMixin):
    def get(self):
        self.setDefaultHeader()
        self.write(json.dumps(version_histories))