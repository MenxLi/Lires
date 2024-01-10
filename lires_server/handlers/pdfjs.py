"""
Serve pdfjs files
"""

from ._base import *
from ..config import PDF_VIEWER_DIR
from lires.core.pdfTools import initPDFViewer

initPDFViewer(PDF_VIEWER_DIR)
class PdfJsHandler(tornado.web.StaticFileHandler, RequestHandlerMixin, print_init_info = False):
    root_dir = PDF_VIEWER_DIR

    def get(self, *args, **kwargs):
        # to prevent unauthorized access! 
        # otherwise, anyone can access the pdf viewer and this may become a public pdf viewer...?
        if "web/viewer.html" in args:
            self.checkKey()
        return super().get(*args, **kwargs)