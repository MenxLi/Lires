import json, os, multiprocessing, shutil, tempfile, zipfile, tempfile
from typing import List, Union, Callable

from RBMWeb.backend.rbmlibs import DatabaseReader
from RBMWeb.backend.confReader import getRBMWebConf
from RBMWeb.backend.encryptServer import queryHashKey

import tornado.ioloop
import tornado.web

from resbibman.confReader import getConfV, TMP_DIR
from resbibman.core.dataClass import DataPoint
from resbibman.core.compressTools import compressDir, decompressDir

class RequestHandlerBase():
    get_argument: Callable

    def checkKey(self):
        enc_key = self.get_argument("key")
        if not queryHashKey(enc_key):
            # unauthorized
            raise tornado.web.HTTPError(401) 
        return

    def setDefaultHeader(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, PUT, DELETE, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header("Access-Control-Expose-Headers", "*")

class FileListHandler(tornado.web.RequestHandler, RequestHandlerBase):
    def get(self, tags:str):
        """
        Args:
            tags (str): tags should be "%" or split by "&&"
        """
        global db_reader

        # self.checkKey()

        self.setDefaultHeader()
        if tags == "%":
            tags = []
        else:
            tags = tags.split("&&")

        data_info = db_reader.getDictDataListByTags(tags)
        if data_info is not None:
            json_data = {
                "data":data_info
            }
            self.write(json.dumps(json_data))
        else:
            self.write("Something wrong with the server.")
        return

class DocHandler(tornado.web.RequestHandler, RequestHandlerBase):
    def get(self, uuid):
        global db_reader
        self.setDefaultHeader()
        file_p = db_reader.getPDFPathByUUID(uuid)
        if isinstance(file_p, str):
            if file_p.endswith(".pdf"):
                with open(file_p, "rb") as f:
                    self.set_header("Content-Type", 'application/pdf; charset="utf-8"')
                    self.set_header("Content-Disposition", "attachment; filename={}.pdf".format(uuid))
                    # self.set_header("Access-Control-Allow-Origin", "*")
                    self.write(f.read())
                    return
        self.write("The file not exist or is not PDF file.")

class CommentHandler(tornado.web.RequestHandler, RequestHandlerBase):
    def get(self, uuid):
        # Unfinished.
        global db_reader
        self.setDefaultHeader()
        file_p = db_reader.getCommentPathByUUID(uuid)
        if isinstance(file_p, str):
            if file_p.endswith(".md"):
                with open(file_p, "r", encoding="utf-8") as f:
                    self.write("Not implemented.")
                    return
        self.write("The file not exist or is not MD file.")

class CMDHandler(tornado.web.RequestHandler, RequestHandlerBase):
    def _reloadDB(self):
        global db_reader
        self.setDefaultHeader()
        db_reader.loadDB(db_reader.db_path)
        self.write("success")

    def get(self, cmd):
        if cmd == "reloadDB":
            self._reloadDB()

class HDocHandler(tornado.web.StaticFileHandler, RequestHandlerBase):
    # handler for local web pages
    def get(self, path, include_body = True):
        global db_reader
        self.setDefaultHeader()
        psplit = path.split("/")
        uuid = psplit[0]

        if len(path) == 37:
            # uuid + "/"
            html_p = db_reader.getTmpHtmlPathByUUID(uuid)
            # make sure we can find correct directory in subsequent requests
            assert os.path.dirname(html_p) == os.path.join(TMP_DIR, uuid)
            return super().get(path = html_p, include_body=True)

        else:
            tmp_dir = os.path.join(tempfile.gettempdir(), uuid)
            psplit = tmp_dir.split(os.sep) + psplit[1:]
            if psplit[0] == "":
                psplit = psplit[1:]
            path = "/".join(psplit)
            return super().get(path, include_body=True)

class FileHandler(tornado.web.RequestHandler, RequestHandlerBase):
    ZIP_TMP_DIR = os.path.join(TMP_DIR, "zips")
    
    def initialize(self):
        super().initialize()
        self.zip_tmp_dir = self.ZIP_TMP_DIR
        if not os.path.exists(self.zip_tmp_dir):
            os.mkdir(self.zip_tmp_dir)

    def post(self):
        """
         - cmd: <command>-<uuid>
        """
        global db_reader
        db = db_reader.db

        self.checkKey()

        self.setDefaultHeader()
        cmd = self.get_argument("cmd")
        uuid = self.get_argument("uuid")
        print(cmd, uuid)

        if cmd == "download":
            dp: DataPoint = db[uuid]
            tmp_zip = os.path.join(self.zip_tmp_dir, uuid+".zip")
            compressed = compressDir(dp.data_path, tmp_zip)
            with open(compressed, "rb") as f:
                while True:
                    data = f.read(4096)
                    if not data:
                        break
                    self.write(data)
        
        elif cmd == "upload":
            tmp_zip = os.path.join(self.zip_tmp_dir, uuid+".zip")
            req_file = self.request.files
            f_body = req_file["file"][0]["body"]
            f_name = req_file["filename"][0]["body"].decode("utf-8")

            with open(tmp_zip, "wb") as fp:
                fp.write(f_body)

            dest = os.path.join(getConfV("database"), f_name)
            if os.path.exists(dest):
                shutil.rmtree(dest)
            dest = decompressDir(tmp_zip, dest)
            db.add(dest)
        
        elif cmd == "delete":
            if uuid in db:
                db.delete(uuid)


class Application(tornado.web.Application):
    def __init__(self) -> None:
        root = os.path.dirname(__file__)
        frontend_root = os.path.join(root, "frontend")
        handlers = [
            (r"/favicon.ico()", tornado.web.StaticFileHandler, {"path": frontend_root}),
            (r"/main/(.*)", tornado.web.StaticFileHandler, {"path": frontend_root, "default_filename" : "index.html"}),
            (r"/doc/(.*)", DocHandler),
            (r"/hdoc/(.*)", HDocHandler, {"path": "/"}),
            (r"/filelist/(.*)", FileListHandler),
            (r"/file", FileHandler),
            (r"/comment/(.*)", CommentHandler),
            (r"/cmd/(.*)", CMDHandler),
        ]
        super().__init__(handlers)

def startServer(port: Union[int, str, None] = None):
    global db_reader

    db_reader = DatabaseReader(getConfV("database"))
    app = Application()
    conf = getRBMWebConf()
    if port is None:
        port = conf["port"]
    print("Starting server at port: ", port)
    app.listen(str(port))
    tornado.ioloop.IOLoop.current().start()

def startServerProcess(*args) -> multiprocessing.Process:
    p = multiprocessing.Process(target=startServer, args=args)
    p.start()
    return p


if __name__ == "__main__":
    startServer(8080)
