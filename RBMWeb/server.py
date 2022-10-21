from __future__ import annotations
import json, os, multiprocessing, shutil, tempfile, zipfile, tempfile, string
from typing import List, Union, Callable, Optional
import markdown

from RBMWeb.backend.rbmlibs import DatabaseReader
from RBMWeb.backend.encryptServer import queryHashKey
from RBMWeb.backend.discussUtils import DiscussDatabase, DiscussLine

import tornado.autoreload
import tornado.ioloop
import tornado.web
import http.cookies

from resbibman.confReader import getConfV, TMP_DIR, TMP_WEB, TMP_WEB_NOTES
from resbibman.core.dataClass import DataPoint, FileManipulatorVirtual
from resbibman.core.compressTools import compressDir, decompressDir

class RequestHandlerBase():
    get_argument: Callable
    get_cookie: Callable[[str, Optional[str]], Optional[str]]
    set_header: Callable
    cookies: http.cookies.SimpleCookie

    def checkCookieKey(self):
        """
        Authenticates key from cookies
        """
        #  cookies = self.cookies
        enc_key = self.get_cookie("RBM_ENC_KEY", "")
        return self._checkKey(enc_key)

    def checkKey(self):
        """
        Authenticates key from params
        """
        enc_key = self.get_argument("key")
        return self._checkKey(enc_key)

    def _checkKey(self, enc_key):
        if not enc_key:
            raise tornado.web.HTTPError(401) 

        if not queryHashKey(enc_key):
            # unauthorized
            print("Reject key ({}), abort".format(enc_key))
            raise tornado.web.HTTPError(401) 
        self.enc_key = enc_key
        return True

    def setDefaultHeader(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, PUT, DELETE, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header("Access-Control-Expose-Headers", "*")

class FileListHandler(tornado.web.RequestHandler, RequestHandlerBase):
    def get(self):
        """
        Args:
            tags (str): tags should be "%" or split by "&&"
        """
        global db_reader

        print("receiving file list request")
        # self.checkKey()

        self.setDefaultHeader()
        tags = self.get_argument("tags")
        if tags == "":
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

class FileInfoHandler(tornado.web.RequestHandler, RequestHandlerBase):
    """
    Query information about single file
    """
    def get(self, uid:str):
        """
         - uuid_cmd (str): <uuid>?<cmd> | <uuid>
        """
        global db_reader
        self.setDefaultHeader()
        
        try:
            cmd = self.get_argument("cmd")
        except:
            cmd = None
        dp: DataPoint = db_reader.db[uid]
        if cmd is None:
            d_info = db_reader.getDataInfo(uid)
            self.write(json.dumps(d_info))
            return
        elif cmd == "stringInfo":
            detail = dp.stringInfo()
            self.write(detail)
            return 
        else:
            # not implemented
            raise tornado.web.HTTPError(404)

class DocHandler(tornado.web.RequestHandler, RequestHandlerBase):
    def get(self, uuid):
        global db_reader
        self.setDefaultHeader()
        file_p = db_reader.getPDFPathByUUID(uuid)
        if isinstance(file_p, str):
            if file_p.endswith(".pdf"):
                with open(file_p, "rb") as f:
                    self.set_header("Content-Type", 'application/pdf; charset="utf-8"')
                    self.set_header("Content-Disposition", "inline; filename={}.pdf".format(uuid))
                    # self.set_header("Access-Control-Allow-Origin", "*")
                    self.write(f.read())
                    return
        self.write("The file not exist or is not PDF file.")

class CommentHandler(tornado.web.StaticFileHandler, RequestHandlerBase):
    # Serve comment (Notes) as webpage
    def get(self, path):
        global db_reader
        print("Get comment request: {}".format(path))
        self.setDefaultHeader()
        psplit = path.split("/")
        uuid = psplit[0]
        tmp_dir = os.path.join(TMP_WEB_NOTES, uuid)
        if len(path) == 37:
            # uuid + "/"
            html_path = db_reader.getTmpNotesPathByUUID(uuid)
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

class CMDHandler(tornado.web.RequestHandler, RequestHandlerBase):
    def _reloadDB(self):
        global db_reader
        self.setDefaultHeader()
        db_reader.loadDB(db_reader.db_path)
        self.write("success")

    def get(self, cmd):
        if cmd == "reloadDB":
            print("receiving reload Database command")
            self._reloadDB()

class CMDArgHandler(tornado.web.RequestHandler, RequestHandlerBase):
    """Command with arguments"""
    def post(self):
        global db_reader
        db = db_reader.db

        self.setDefaultHeader()
        cmd = self.get_argument("cmd")
        uuid = self.get_argument("uuid")
        args = json.loads(self.get_argument("args"))
        kwargs = json.loads(self.get_argument("kwargs"))
        print("Receiving argument command: ", cmd, uuid, args, kwargs)

        if not self.checkKey():
            return 

        if cmd == "renameTagAll":
            db.renameTag(args[0], args[1])
        if cmd == "deleteTagAll":
            db.deleteTag(args[0])
        if cmd == "rbm-collect":
            from resbibman.cmdTools.rbmCollect import exec as exec_rbmCollect
            d_path = exec_rbmCollect(args[0], **kwargs)
            if d_path:
                db.add(d_path)
            else:
                raise tornado.web.HTTPError(418) 

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

class FileHandler(tornado.web.RequestHandler, RequestHandlerBase):
    ZIP_TMP_DIR = os.path.join(TMP_DIR, "server_zips")
    
    def initialize(self):
        super().initialize()
        self.zip_tmp_dir = self.ZIP_TMP_DIR
        if not os.path.exists(self.zip_tmp_dir):
            os.mkdir(self.zip_tmp_dir)

    def post(self):
        global db_reader
        db = db_reader.db

        self.setDefaultHeader()
        cmd = self.get_argument("cmd")
        uuid = self.get_argument("uuid")
        print("Receiving file request: ", cmd, uuid)

        if not self.checkKey():
            return 

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
            else:
                print(f"{uuid} not in database, thus not being deleted")

class DiscussionHandler(tornado.web.RequestHandler, RequestHandlerBase):
    def get(self, file_uid: str):
        global discussion_db
        self.checkCookieKey()
        self.setDefaultHeader()
        discussions = discussion_db.discussions(file_uid)
        base_html = string.Template(
        """
        <html>
        <head>
        <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no">
        <title>Comments</title>
        <style>
            img {
                max-width: 100%;
            }
            hr {
                color: #dddddd
            }
            .usr_name {
                color: #888888
            }
            .hint {
                color: #888888;
                text-align: center
            }
            .discuss_uid {
                color: #bbbbbb;
                position: relative;
                font-size: 10px;
                float: right
            }
        </style>
        </head>
        <body>
        ${content}
        </body>
        </html>
        """)

        contents = []
        if not discussions:
            contents.append(
                "<p class=\"hint\">{}</p>".format("let us discuss this paper!"))
        for line in discussions:
            comment = markdown.markdown(line["content"])
            comment = "<div class=\"comment\">{}<div>".format(comment)

            content_ = "<p class=\"discuss_uid\">{}</p>".format(line["discuss_uid"])
            content_ += "<p class=\"usr_name\">{}: </p>".format(line["usr_name"])
            content_ += comment

            contents.append("<div class=\"discuss_line\">{}</div>".format(content_))
        rendered = base_html.substitute(content = "<hr>".join(contents))
        self.write(rendered)

class DiscussionModHandler (tornado.web.RequestHandler, RequestHandlerBase):
    """
    Modify discussions
    """
    def post(self):
        global discussion_db
        self.setDefaultHeader()
        print("Receiving discussion modify request")

        if not self.checkKey() and self.checkCookieKey():
            return

        cmd = self.get_argument("cmd")
        file_uid = self.get_argument("file_uid")
        content = self.get_argument("content")
        usr_name = self.get_argument("usr_name")

        if cmd == "add":
            print("Adding discussion...")
            discussion_db.addDiscuss(
                file_uid = file_uid, 
                usr_name = usr_name, 
                content = content, 
                access_key_hex = self.enc_key,
            )

class AuthHandler (tornado.web.RequestHandler, RequestHandlerBase):
    def post(self):
        self.setDefaultHeader()
        if self.checkKey():
            self.write("Success")
        

class Application(tornado.web.Application):
    def __init__(self) -> None:
        root = os.path.dirname(__file__)
        frontend_root = os.path.join(root, "frontend")
        frontend_root_old = os.path.join(root, "frontendV0")
        handlers = [
            # Frontend
            (r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path": frontend_root}),
            (r"/frontend/(.*)", tornado.web.StaticFileHandler, {"path": frontend_root, "default_filename" : "index.html"}),
            (r"/main/(.*)", tornado.web.StaticFileHandler, {"path": frontend_root_old, "default_filename" : "index.html"}),
            # Backend
            (r"/doc/(.*)", DocHandler),
            (r"/hdoc/(.*)", HDocHandler, {"path": "/"}),
            (r"/filelist", FileListHandler),
            (r"/fileinfo/(.*)", FileInfoHandler),
            (r"/file", FileHandler),
            (r"/comment/(.*)", CommentHandler, {"path": "/"}),
            (r"/cmd/(.*)", CMDHandler),
            (r"/cmdA", CMDArgHandler),
            (r"/discussions/(.*)", DiscussionHandler),
            (r"/discussion_mod", DiscussionModHandler),
            (r"/auth", AuthHandler),
        ]
        super().__init__(handlers)

def startServer(port: Union[int, str]):
    global db_reader
    global discussion_db 

    discussion_db = DiscussDatabase()
    db_reader = DatabaseReader(getConfV("database"))
    app = Application()
    print("Starting server at port: ", port)
    app.listen(int(port))
    tornado.autoreload.add_reload_hook(lambda: print("Server reloaded"))
    tornado.autoreload.start()
    tornado.ioloop.IOLoop.current().start()

def startServerProcess(*args) -> multiprocessing.Process:
    p = multiprocessing.Process(target=startServer, args=args)
    p.start()
    return p


if __name__ == "__main__":
    startServer(8080)
