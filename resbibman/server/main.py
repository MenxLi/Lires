import os, multiprocessing, logging
from typing import Union
from RBMWeb import RBMWEB_SRC_ROOT
from resbibman.core import globalVar as G

import tornado
import tornado.ioloop
import tornado.web
import tornado.autoreload

from .handlers import *

class Application(tornado.web.Application):
    def __init__(self) -> None:
        frontend_root = os.path.join(RBMWEB_SRC_ROOT, "frontend")
        frontend_root_old = os.path.join(RBMWEB_SRC_ROOT, "frontendV0")
        handlers = [
            # Frontend, deprecated
            (r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path": frontend_root}),
            (r"/frontend/(.*)", tornado.web.StaticFileHandler, {"path": frontend_root, "default_filename" : "index.html"}),
            (r"/main/(.*)", tornado.web.StaticFileHandler, {"path": frontend_root_old, "default_filename" : "index.html"}),
            # # Backend
            (r"/doc/(.*)", DocHandler),
            (r"/hdoc/(.*)", HDocHandler, {"path": "/"}),
            (r"/filelist", DataListHandler),
            (r"/fileinfo/(.*)", DataInfoHandler),
            (r"/file", FileHandler),
            (r"/comment/(.*)", CommentHandler, {"path": "/"}),
            (r"/cmd/(.*)", CMDHandler),
            (r"/cmdA", CMDArgHandler),
            (r"/discussions/(.*)", DiscussionHandler),
            (r"/discussion_mod", DiscussionModHandler),
            (r"/auth", AuthHandler),
            (r"/search", SearchHandler),
            (r"/summary", SummaryHandler),
            (r"/summary-post", SummaryPostHandler),
            (r"/collect", CollectHandler),

            # iServer proxy
            (r"/iserver/(.*)", IServerProxyHandler),

            # data management
            (r"/dataman/delete", DataDeleteHandler),
            (r"/dataman/update", DataUpdateHandler),
            (r"/dataman/doc-upload/(.*)", DocumentUploadHandler),
            (r"/dataman/doc-free/(.*)", DocumentFreeHandler),

            # deal with images under misc folder of each datapoint
            (r"/img/(.*)", ImageGetHandler),
            (r"/img-upload/(.*)", ImageUploadHandler),

            # additional information (supplementary data / resources) for each datapoint
            (r"/fileinfo-supp/note/(.*)", NoteGetHandler),
            (r"/fileinfo-supp/note-update/(.*)", NoteUpdateHandler),
            (r"/fileinfo-supp/abstract/(.*)", AbstractGetHandler),
            (r"/fileinfo-supp/abstract-update/(.*)", AbstractUpdateHandler),

            # pdfjs
            (r"/pdfjs/(.*)", PdfJsHandler, {"path": PdfJsHandler.root_dir}),

        ]
        super().__init__(handlers)

def startServer(port: Union[int, str], iserver_host: str, iserver_port: Union[int, str]):

    # initialize G.logger_rbm_server to print to stdout
    G.logger_rbm_server.setLevel(logging.DEBUG)
    _ch = logging.StreamHandler()
    _ch.setLevel(logging.DEBUG)
    _ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    G.logger_rbm_server.addHandler(_ch)

    # set global variables of iServer
    # so that when initializing iServerConn, it can get the correct host and port
    G.iserver_host = iserver_host
    G.iserver_port = iserver_port

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
    startServer(8080, "127.0.0.1", "8731")
