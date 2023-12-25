import os, multiprocessing
from typing import Union, TypedDict
from lires_web import LRSWEB_SRC_ROOT
from functools import partial
from lires.core import globalVar as G
from lires.core.utils import BCOLORS
from lires.initLogger import setupLogger
from lires.confReader import LOG_DIR

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
            # websocket
            (r'/ws', WebsocketHandler),

            # # Backend
            (r"/summary", SummaryHandler),
            (r"/status", StatusHandler),
            (r"/reload-db", ReloadDBHandler),
            (r"/doc/(.*)", DocHandler),
            (r"/hdoc/(.*)", HDocHandler, {"path": "/"}),
            (r"/auth", AuthHandler),
            (r"/search", SearchHandler),
            (r"/collect", CollectHandler),

            (r"/filelist", DataListHandler),
            (r"/filelist-stream", DataListStreamHandler),
            (r"/fileinfo/(.*)", DataInfoHandler),

            (r'/datafeat/tsne/(.*)', DataFeatureTSNEHandler),

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

            # user
            (r"/user/list", UserListHandler),
            (r"/user/info/(.*)", UserInfoHandler),
            (r"/user/info-update", UserInfoUpdateHandler),
            (r"/user/avatar/(.*)", UserAvatarHandler),
            (r"/user/avatar-upload", UserAvatarUploadHandler),
            (r"/userman/create", UserCreateHandler),
            (r"/userman/delete", UserDeleteHandler),
            (r"/userman/modify", UserModifyHandler),

            # pdfjs
            (r"/pdfjs/(.*)", PdfJsHandler, {"path": PdfJsHandler.root_dir}),

            # info
            (r"/info/changelog", ChangelogHandler),

            # # Frontend (Static file, non-lires_web)
            (r"/static/(.*)", StaticHandler),

        ]
        super().__init__(handlers)


_SSL_CONFIGT = TypedDict("_SSL_CONFIGT", {"certfile": str, "keyfile": str})
def __startServer(port: Union[int, str], iserver_host: str, iserver_port: Union[int, str], ssl_config : _SSL_CONFIGT | None = None):

    # init loggers
    setupLogger(
        G.logger_lrs_server,
        term_id="server",
        term_id_color=BCOLORS.OKBLUE,
        term_log_level="DEBUG",
        file_path = os.path.join(LOG_DIR, "server.log"),
        file_log_level="INFO",
    )
    setupLogger(
        G.logger_lrs,
        term_id="core",
        term_id_color=BCOLORS.OKGREEN,
        term_log_level="DEBUG",
        file_path = os.path.join(LOG_DIR, "core.log"),
        file_log_level="INFO",
    )

    # set global variables of iServer
    # so that when initializing iServerConn, it can get the correct host and port
    G.iserver_host = iserver_host
    G.iserver_port = iserver_port

    app = Application()
    G.logger_lrs_server.info("Starting server at port: {}".format(port))

    ssl_ctx = None
    if ssl_config is not None:
        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_cert_chain(certfile=ssl_config["certfile"], keyfile=ssl_config["keyfile"])
    server = HTTPServer(app, ssl_options=ssl_ctx)
    server.listen(int(port))

    tornado.autoreload.add_reload_hook(lambda: print("Server reloaded"))
    tornado.autoreload.start()

    async def buildIndex(op_interval = 0.05):
        print("Periodically build index")
        from lires.core.textUtils import buildFeatureStorage

        base_request_handler = RequestHandlerMixin()
        await buildFeatureStorage(
            db = base_request_handler.db,
            vector_db = base_request_handler.vec_db,
            use_llm = False,
            operation_interval=op_interval,
        )

    # tornado.ioloop.IOLoop.current().add_callback(buildIndex)
    pc = tornado.ioloop.PeriodicCallback(buildIndex, 60*60*1000)  # in milliseconds
    pc.start()

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

def startServer(port: Union[int, str], iserver_host: str, iserver_port: Union[int, str]) -> None:
    # add ssl config
    p_startServer = partial(__startServer, ssl_config=SSL_CONFIG)
    p_startServer(port=port, iserver_host=iserver_host, iserver_port=iserver_port)

def startFrontendServer(port: Union[int, str] = 8081) -> None:
    p_startFrontendServer = partial(__startFrontendServer, ssl_config=SSL_CONFIG)
    p_startFrontendServer(port=port)

if __name__ == "__main__":
    __startServer(8080, "127.0.0.1", "8731")
