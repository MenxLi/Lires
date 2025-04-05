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

    def set_extra_headers(self, path: str) -> None:
        # file type assurance
        super().set_extra_headers(path)

        if path.endswith(".js") or path.endswith(".mjs"):
            self.set_header("Content-Type", "application/javascript")
        if path.endswith(".pdf"):
            self.set_header("Content-Type", "application/pdf")
        if path.endswith(".svg"):
            self.set_header("Content-Type", "image/svg+xml")

    async def get(self, path: str, *args, **kwargs):
        # to prevent unauthorized access! 
        # otherwise, anyone can access the pdf viewer and this may become a public pdf viewer...?
        if "web/viewer.html" in path:
            await self.check_key()
        return await super().get(path, *args, **kwargs)