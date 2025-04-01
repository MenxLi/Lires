"""
Serve pdfjs files
"""

from ._base import *
from ..path_config import PDF_VIEWER_DIR
from lires.core.pdfTools import init_pdf_viewer
import asyncio

asyncio.run(init_pdf_viewer(PDF_VIEWER_DIR))
class PdfJsHandler(tornado.web.StaticFileHandler, RequestHandlerMixin, print_init_info = False):
    root_dir = PDF_VIEWER_DIR

    async def get(self, *args, **kwargs):
        # to prevent unauthorized access! 
        # otherwise, anyone can access the pdf viewer and this may become a public pdf viewer...?
        if "web/viewer.html" in args:
            await self.check_key()
        return await super().get(*args, **kwargs)