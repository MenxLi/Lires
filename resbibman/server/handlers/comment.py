from ._base import *
from resbibman.confReader import TMP_WEB_NOTES, ASSETS_PATH
from resbibman.core.dataClass import DataPoint
import os, shutil

class CommentHandler(tornado.web.StaticFileHandler, RequestHandlerBase):
    # Serve comment (Notes) as webpage
    def get(self, path: str):
        print("Get comment request: {}".format(path))
        self.setDefaultHeader()
        psplit = path.split("/")
        uuid = psplit[0]
        tmp_dir = os.path.join(TMP_WEB_NOTES, uuid)
        if len(path) == 37:
            # uuid + "/"
            html_path = self.getTmpNotesPathByUUID(uuid)
            assert tmp_dir == os.path.abspath(os.path.dirname(html_path))
            return super().get(html_path, include_body = True)
        else:
            # is this unsafe??
            psplit = tmp_dir.split(os.sep) + psplit[1:]
            if psplit[0] == "":
                psplit = psplit[1:]
            path = "/".join(psplit)
            return super().get(path, include_body = True)
        # raise tornado.web.HTTPError(418) 

    def getTmpNotesPathByUUID(self, uuid: str):
        dp: DataPoint = self.db[uuid]
        #  htm_str = self.getCommentHTMLByUUID(uuid)
        htm_str = dp.htmlComment(abs_fpath = False)
        tmp_notes_pth = os.path.join(TMP_WEB_NOTES, uuid)
        if os.path.exists(tmp_notes_pth):
            shutil.rmtree(tmp_notes_pth)
        os.mkdir(tmp_notes_pth)
        tmp_notes_html = os.path.join(tmp_notes_pth, "index.html")
        tmp_notes_misc = os.path.join(tmp_notes_pth, "misc")
        with open(tmp_notes_html, "w") as fp:
            fp.write(htm_str)
        if dp.fm.hasMisc():
            os.symlink(dp.fm.getMiscDir(), tmp_notes_misc)

        # For mathjax, not working somehow?
        math_jax_path = os.path.join(ASSETS_PATH, "mathjax")
        for f in os.listdir(math_jax_path):
            mjf_path = os.path.join(math_jax_path, f)
            os.symlink(mjf_path, os.path.join(tmp_notes_pth, f))
        return tmp_notes_html