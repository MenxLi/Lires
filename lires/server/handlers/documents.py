"""
Get documents: document file / web page / comments
"""
from ._base import *
import os
from lires.confReader import TMP_WEB
from lires.core.htmlTools import unpackHtmlTmp

class DocHandler(tornado.web.RequestHandler, RequestHandlerMixin):
    def get(self, uuid):
        self.allowCORS()
        file_p = self.db[uuid].fm.file_p
        if isinstance(file_p, str):
            if file_p.endswith(".pdf"):
                with open(file_p, "rb") as f:
                    self.set_header("Content-Type", 'application/pdf; charset="utf-8"')
                    self.set_header("Content-Disposition", "inline; filename={}.pdf".format(uuid))
                    # self.set_header("Access-Control-Allow-Origin", "*")
                    self.write(f.read())
                    return
        self.write("The file not exist or is not PDF file.")

class HDocHandler(tornado.web.StaticFileHandler, RequestHandlerMixin):
    # handler for local web pages
    def get(self, path, include_body = True):
        self.allowCORS()
        psplit = path.split("/")
        uuid = psplit[0]

        if len(path) == 37:
            # uuid + "/"
            html_p = self.getTmpHtmlPathByUUID(uuid)
            # make sure we can find correct directory in subsequent requests
            assert os.path.dirname(html_p) == os.path.join(TMP_WEB, uuid)
            return super().get(path = html_p, include_body=True)

        else:
            # is this unsafe??
            tmp_dir = os.path.join(TMP_WEB, uuid)
            psplit = tmp_dir.split(os.sep) + psplit[1:]
            if psplit[0] == "":
                psplit = psplit[1:]
            path = "/".join(psplit)
            return super().get(path, include_body=True)

    def getTmpHtmlPathByUUID(self, uuid: str):
        dp = self.db[uuid]
        if not dp.fm.file_extension == ".hpack":
            return ""
        file_p = dp.fm.file_p
        assert file_p is not None
        html_p = unpackHtmlTmp(file_p, tmp_dir_name = uuid)
        return html_p