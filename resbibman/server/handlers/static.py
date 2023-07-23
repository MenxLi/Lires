from ._base import *
import os
from resbibman.confReader import TMP_DIR 

class StaticHandler(RequestHandlerBase, tornado.web.RequestHandler):

    def get(self, path: str):
        if path == "visfeat":
            html_path = os.path.join(TMP_DIR, "hover_glyph.html")
            if not os.path.exists(html_path):
                self.write("File not found")
                return
            with open(html_path, "r") as f:
                self.write(f.read())
        else:
            raise tornado.web.HTTPError(404)
