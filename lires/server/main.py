import os, multiprocessing, logging
from typing import Union, TypedDict
from rbmweb import LRSWEB_SRC_ROOT
from functools import partial
from lires.core import globalVar as G
from lires.core.utils import BCOLORS
from lires.initLogger import setupLogger
from lires.confReader import LRS_HOME

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
            (r'/(.*)', tornado.web.StaticFileHandler, {"path": LRSWEB_SRC_ROOT, "default_filename": "index.html"}),
        ]
        super().__init__(handlers)      # type: ignore

class Application(tornado.web.Application):
    def __init__(self) -> None:
        handlers = [
            # # Backend

            ## For Qt client and online filemanipulator only
            (r"/file", FileHandler),
            (r"/comment/(.*)", CommentHandler, {"path": "/"}),

            ## For both clients
            (r"/discussions/(.*)", DiscussionHandler),
            (r"/discussion_mod", DiscussionModHandler),
            (r"/summary", SummaryHandler),              # may deprecate
            (r"/summary-post", SummaryPostHandler),     # may rename

            (r"/reload-db", ReloadDBHandler),
            (r"/doc/(.*)", DocHandler),
            (r"/hdoc/(.*)", HDocHandler, {"path": "/"}),
            (r"/auth", AuthHandler),
            (r"/search", SearchHandler),
            (r"/collect", CollectHandler),
            (r"/filelist", DataListHandler),            # may change
            (r"/fileinfo/(.*)", DataInfoHandler),       # may change

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

            # # Frontend (Static file, non-rbmweb)
            (r"/static/(.*)", StaticHandler),

        ]
        super().__init__(handlers)


_SSL_CONFIGT = TypedDict("_SSL_CONFIGT", {"certfile": str, "keyfile": str})
def __startServer(port: Union[int, str], iserver_host: str, iserver_port: Union[int, str], ssl_config : _SSL_CONFIGT | None = None):

    # init loggers
    setupLogger(
        G.logger_rbm_server,
        term_id="server",
        term_id_color=BCOLORS.OKBLUE,
        term_log_level="DEBUG",
        file_path = os.path.join(LRS_HOME, "server.log"),
        file_log_level="INFO",
    )
    setupLogger(
        G.logger_rbm,
        term_id="core",
        term_id_color=BCOLORS.OKGREEN,
        term_log_level="DEBUG",
        file_path = os.path.join(LRS_HOME, "core.log"),
        file_log_level="INFO",
    )

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

def __startFrontendServer(port: Union[int, str] = 8081, ssl_config : _SSL_CONFIGT | None = None):
    app = FrontendApplication()
    ssl_ctx = None
    logger = setupLogger("frontend")
    if ssl_config is not None:
        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_cert_chain(certfile=ssl_config["certfile"], keyfile=ssl_config["keyfile"])
    server = HTTPServer(app, ssl_options=ssl_ctx)
    logger.info(f"Starting LiresWeb server at port: {port}")
    server.listen(int(port))

    tornado.autoreload.add_reload_hook(lambda: print("Server reloaded"))
    tornado.autoreload.start()
    tornado.ioloop.IOLoop.current().start()


# SSL config
_ENV_CERTFILE = os.environ.get("LRS_SSL_CERTFILE")
_ENV_KEYFILE = os.environ.get("LRS_SSL_KEYFILE")
SSL_CONFIG: _SSL_CONFIGT | None
if bool(_ENV_CERTFILE) != bool(_ENV_KEYFILE):
    # if only one of them is set
    raise ValueError("LRS_SSL_CERTFILE and LRS_SSL_KEYFILE must be both set or both not set")
if _ENV_CERTFILE is not None:
    SSL_CONFIG = {"certfile": _ENV_CERTFILE, "keyfile": _ENV_KEYFILE} # type: ignore
else:
    SSL_CONFIG = None

def startServerProcess(*args) -> multiprocessing.Process:
    # add ssl config
    p_startServer = partial(__startServer, ssl_config=SSL_CONFIG)
    p = multiprocessing.Process(target=p_startServer, args=args)
    p.start()
    return p

def startFrontendServerProcess(*args) -> multiprocessing.Process:
    p_startFrontendServer = partial(__startFrontendServer, ssl_config=SSL_CONFIG)
    p = multiprocessing.Process(target=p_startFrontendServer, args=args)
    p.start()
    return p

if __name__ == "__main__":
    __startServer(8080, "127.0.0.1", "8731")
