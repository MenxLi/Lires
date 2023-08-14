"""
Serve pdfjs files
"""

from ._base import *
from resbibman.confReader import DEFAULT_PDF_VIEWER_DIR

class PdfJsHandler(RequestHandlerMixin, tornado.web.StaticFileHandler):
    root_dir = DEFAULT_PDF_VIEWER_DIR
    G.logger_rbm.info("Using pdf viewer: {}".format(root_dir))
    def get(self, *args, **kwargs):
        # to prevent unauthorized access! 
        # otherwise, anyone can access the pdf viewer and this may become a public pdf viewer...?
        if "web/viewer.html" in args:
            self.checkKey()
        self.logger.debug("PdfJsHandler: args:{args} | kwargs:{kwargs} | file: {file}"\
                          .format(args = args, kwargs=kwargs, file = self.get_argument("file", "")))
        return super().get(*args, **kwargs)