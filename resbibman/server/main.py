import os, multiprocessing
from typing import Union
from RBMWeb import RBMWEB_SRC_ROOT

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
            # Frontend
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
        ]
        super().__init__(handlers)

def startServer(port: Union[int, str]):
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
