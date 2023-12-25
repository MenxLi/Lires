"""
Serve pdfjs files
"""

from ._base import *
import os
from lires.confReader import PDF_VIEWER_DIR

class PdfJsHandler(tornado.web.StaticFileHandler, RequestHandlerMixin):
    root_dir = PDF_VIEWER_DIR
    if not os.path.exists(os.path.join(root_dir, "web/viewer.html")):
        G.logger_lrs.error("Pdf viewer not found: {}".format(root_dir))

    def get(self, *args, **kwargs):
        # to prevent unauthorized access! 
        # otherwise, anyone can access the pdf viewer and this may become a public pdf viewer...?
        if "web/viewer.html" in args:
            self.checkKey()
        self.logger.debug("PdfJsHandler: args:{args} | kwargs:{kwargs} | file: {file}"\
                          .format(args = args, kwargs=kwargs, file = self.get_argument("file", "")))
        return super().get(*args, **kwargs)