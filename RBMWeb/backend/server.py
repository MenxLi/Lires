import json, os, multiprocessing
from typing import Union

from RBMWeb.backend.rbmlibs import DatabaseReader
from RBMWeb.backend.confReader import getRBMWebConf

import tornado.ioloop
import tornado.web

from resbibman.confReader import getConf, getConfV

pdf_file_path = "/home/monsoon/Downloads/Coursera_5QWUXAASSWXN.pdf"

class Application(tornado.web.Application):
    def __init__(self) -> None:
        handlers = [
            (r"/file/(.*)", FileHandler),
            (r"/main/(.*)", FileListHandler),
            (r"/comment/(.*)", CommentHandler),
        ]
        super().__init__(handlers)

class FileListHandler(tornado.web.RequestHandler):
    def get(self, tags:str):
        """
        Args:
            tags (str): tags should be "%" or split by "&&"
        """
        global db_reader
        self.set_header("Access-Control-Allow-Origin", "*")
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

class FileHandler(tornado.web.RequestHandler):
    def get(self, uuid):
        global db_reader
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

class CommentHandler(tornado.web.RequestHandler):
    def get(self, uuid):
        # Unfinished.
        global db_reader
        file_p = db_reader.getCommentPathByUUID(uuid)
        if isinstance(file_p, str):
            if file_p.endswith(".md"):
                with open(file_p, "r", encoding="utf-8") as f:
                    self.write("Not implemented.")
                    return
        self.write("The file not exist or is not MD file.")

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
    startServer()