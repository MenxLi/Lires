"""
Serve pdfjs files
"""

from ._base import *
from lires.confReader import PDF_VIEWER_DIR
from lires.core.pdfTools import initPDFViewer

initPDFViewer()
class PdfJsHandler(tornado.web.StaticFileHandler, RequestHandlerMixin):
    root_dir = PDF_VIEWER_DIR

    def get(self, *args, **kwargs):
        # to prevent unauthorized access! 
        # otherwise, anyone can access the pdf viewer and this may become a public pdf viewer...?
        if "web/viewer.html" in args:
            self.checkKey()
        return super().get(*args, **kwargs)