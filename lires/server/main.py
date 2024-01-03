import os
from datetime import datetime
from typing import Union, TypedDict
from lires_web import LRSWEB_SRC_ROOT
from functools import partial
from lires.version import VERSION
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


class DefaultRequestHandler(RequestHandlerBase):
    def get(self, *args, **kwargs):
        # print path
        self.logger.debug(f"DEFAULT_HANDLER: {self.request.full_url()} ({self.request.remote_ip})")
        # trace the source
        html_page = """
        <!DOCTYPE html>
        <html>
        <head> <title>Lires Server (v{version})</title> </head>
        <body>
        <h1>Lires Server</h1>
        <p><b> Current request is not supported. </b></p>
        <p> Have a nice day :) </p>
        </body>
        </html>
        """.format(version = VERSION)
        return self.write(html_page)

class StaticFileHandler(tornado.web.StaticFileHandler, RequestHandlerMixin):
    ...

def cachedStaticFileHandlerFactory(cache_seconds):
    class _CacheStaticFileHandler(StaticFileHandler):
        def get_cache_time(self, path: str, modified: datetime | None, mime_type: str) -> int:
            return cache_seconds
    return _CacheStaticFileHandler

class Application(tornado.web.Application):
    def __init__(self, debug = False) -> None:
        # will use simple storage service protocal (put, get, delete) to store data, when applicable
        handlers = [
            # Frontend
            (r'/()', StaticFileHandler, {"path": LRSWEB_SRC_ROOT, "default_filename": "index.html"}),
            (r'/(index.html)', StaticFileHandler, {"path": LRSWEB_SRC_ROOT}),
            (r'/(favicon.ico)', StaticFileHandler, {"path": LRSWEB_SRC_ROOT}),
            (r'/(assets/.*)', StaticFileHandler, {"path": LRSWEB_SRC_ROOT}),
            (r'/(docs/.*)', cachedStaticFileHandlerFactory(cache_seconds=600), {"path": LRSWEB_SRC_ROOT}),

            # websocket
            (r'/ws', WebsocketHandler),

            # public resources
            (r"/doc/(.*)", DocHandler),
            (r"/img/(.*)", ImageHandler), 
            (r"/pdfjs/(.*)", PdfJsHandler, {"path": PdfJsHandler.root_dir}),
            (r"/user-avatar/(.*)", UserAvatarHandler),

            # APIs =================================================
            (r"/api/summary", SummaryHandler),
            (r"/api/status", StatusHandler),
            (r"/api/reload-db", ReloadDBHandler),
            (r"/api/auth", AuthHandler),
            (r"/api/search", SearchHandler),

            (r"/api/filelist", DataListHandler),
            (r"/api/filelist-stream", DataListStreamHandler),
            (r"/api/fileinfo/(.*)", DataInfoHandler),

            (r'/api/datafeat/tsne/(.*)', DataFeatureTSNEHandler),

            # iServer proxy
            (r"/api/iserver/(.*)", IServerProxyHandler),

            # data management
            (r"/api/dataman/delete", DataDeleteHandler),
            (r"/api/dataman/update", DataUpdateHandler),
            (r"/api/dataman/tag-rename", TagRenameHandler),
            (r"/api/dataman/tag-delete", TagDeleteHandler),

            # additional information (supplementary data / resources) for each datapoint
            (r"/api/fileinfo-supp/note/(.*)", NoteGetHandler),
            (r"/api/fileinfo-supp/note-update/(.*)", NoteUpdateHandler),
            (r"/api/fileinfo-supp/abstract/(.*)", AbstractGetHandler),
            (r"/api/fileinfo-supp/abstract-update/(.*)", AbstractUpdateHandler),

            # user
            (r"/api/user/list", UserListHandler),
            (r"/api/user/info/(.*)", UserInfoHandler),
            (r"/api/user/info-update", UserInfoUpdateHandler),
            (r"/api/userman/create", UserCreateHandler),
            (r"/api/userman/delete", UserDeleteHandler),
            (r"/api/userman/modify", UserModifyHandler),

            # info
            (r"/api/info/changelog", ChangelogHandler),
        ]
        # https://www.tornadoweb.org/en/stable/web.html#tornado.web.Application.settings
        settings = {
            "debug": debug,
            "websocket_ping_interval": 30,
            "websocket_ping_timeout": 60,
            "websocket_max_message_size": 100*1024*1024,
            "default_handler_class": DefaultRequestHandler,
        }
        super().__init__(handlers, **settings)


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
    pc = tornado.ioloop.PeriodicCallback(buildIndex, 12*60*60*1000)  # in milliseconds
    pc.start()

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

if __name__ == "__main__":
    __startServer(8080, "127.0.0.1", "8731")
