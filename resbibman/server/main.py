import os, multiprocessing, logging
from typing import Union, TypedDict
from RBMWeb import RBMWEB_SRC_ROOT
from RBMWeb2 import RBMWEB2_SRC_ROOT
from functools import partial
from resbibman.core import globalVar as G
from resbibman.core.utils import BCOLORS

import tornado
import tornado.ioloop
import tornado.web
import tornado.autoreload
from tornado.httpserver import HTTPServer

import ssl

from .handlers import *

class FrontendApplication(tornado.web.Application):
    def __init__(self) -> None:
        handlers = [
            # Frontend
            (r'/(.*)', tornado.web.StaticFileHandler, {"path": RBMWEB2_SRC_ROOT, "default_filename": "index.html"}),
        ]
        super().__init__(handlers)      # type: ignore

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
            (r"/dataman/tag-rename", TagRenameHandler),
            (r"/dataman/tag-delete", TagDeleteHandler),

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

            # info
            (r"/info/changelog", ChangelogHandler),

        ]
        super().__init__(handlers)


_SSL_CONFIGT = TypedDict("_SSL_CONFIGT", {"certfile": str, "keyfile": str})
def startServer(port: Union[int, str], iserver_host: str, iserver_port: Union[int, str], ssl_config : _SSL_CONFIGT | None = None):

    # initialize G.logger_rbm_server to print to stdout
    G.logger_rbm_server.setLevel(logging.DEBUG)
    _ch = logging.StreamHandler()
    _ch.setLevel(logging.DEBUG)
    _ch.setFormatter(logging.Formatter(BCOLORS.OKBLUE+'[server]'+BCOLORS.OKCYAN + \
                                       ' %(asctime)s - %(levelname)s - ' + BCOLORS.ENDC + ' %(message)s'))
    G.logger_rbm_server.addHandler(_ch)

    # initialize G.logger_rbm to print to stdout
    G.logger_rbm.setLevel(logging.INFO)
    _ch = logging.StreamHandler()
    _ch.setLevel(logging.INFO)
    _ch.setFormatter(logging.Formatter(BCOLORS.OKGREEN+'[ core ]'+ BCOLORS.OKCYAN + \
                                       ' %(asctime)s - %(levelname)s - ' + BCOLORS.ENDC + ' %(message)s'))
    G.logger_rbm.addHandler(_ch)

    # set global variables of iServer
    # so that when initializing iServerConn, it can get the correct host and port
    G.iserver_host = iserver_host
    G.iserver_port = iserver_port

    app = Application()
    G.logger_rbm_server.info("Starting server at port: {}".format(port))

    ssl_ctx = None
    if ssl_config is not None:
        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_cert_chain(certfile=ssl_config["certfile"], keyfile=ssl_config["keyfile"])
    server = HTTPServer(app, ssl_options=ssl_ctx)
    server.listen(int(port))

    tornado.autoreload.add_reload_hook(lambda: print("Server reloaded"))
    tornado.autoreload.start()
    tornado.ioloop.IOLoop.current().start()

def startFrontendServer(port: Union[int, str] = 8081, ssl_config : _SSL_CONFIGT | None = None):
    app = FrontendApplication()
    ssl_ctx = None
    if ssl_config is not None:
        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_cert_chain(certfile=ssl_config["certfile"], keyfile=ssl_config["keyfile"])
    server = HTTPServer(app, ssl_options=ssl_ctx)
    print("Starting RBMWeb server at port: ", port)
    server.listen(int(port))

    tornado.autoreload.add_reload_hook(lambda: print("Server reloaded"))
    tornado.autoreload.start()
    tornado.ioloop.IOLoop.current().start()


# SSL config
_ENV_CERTFILE = os.environ.get("RBM_SSL_CERTFILE")
_ENV_KEYFILE = os.environ.get("RBM_SSL_KEYFILE")
SSL_CONFIG: _SSL_CONFIGT | None
if bool(_ENV_CERTFILE) != bool(_ENV_KEYFILE):
    # if only one of them is set
    raise ValueError("RBM_SSL_CERTFILE and RBM_SSL_KEYFILE must be both set or both not set")
if _ENV_CERTFILE is not None:
    SSL_CONFIG = {"certfile": _ENV_CERTFILE, "keyfile": _ENV_KEYFILE} # type: ignore
else:
    SSL_CONFIG = None

def startServerProcess(*args) -> multiprocessing.Process:
    # add ssl config
    _startServer = partial(startServer, ssl_config=SSL_CONFIG)
    p = multiprocessing.Process(target=_startServer, args=args)
    p.start()
    return p

def startFrontendServerProcess(*args) -> multiprocessing.Process:
    _startFrontendServer = partial(startFrontendServer, ssl_config=SSL_CONFIG)
    p = multiprocessing.Process(target=_startFrontendServer, args=args)
    p.start()
    return p

if __name__ == "__main__":
    startServer(8080, "127.0.0.1", "8731")
