from ._base import *
import json
from lires.version import VERSION_HISTORIES

class ChangelogHandler(RequestHandlerBase):
    def get(self):
        self.write(json.dumps(VERSION_HISTORIES))