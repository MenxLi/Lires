import os, logging
from datetime import datetime
from typing import Union, TypedDict
from lires_web import LRSWEB_SRC_ROOT
from lires.version import VERSION
from lires.utils import UseTermColor

import tornado
import tornado.ioloop
import tornado.web
import tornado.autoreload
from tornado.httpserver import HTTPServer

import ssl

from .handlers import *


class DefaultRequestHandler(RequestHandlerBase):
    async def get(self, *args, **kwargs):
        # print path
        await self.logger.debug(f"DEFAULT_HANDLER: {self.request.full_url()} ({self.request.remote_ip})")
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

class StaticFileHandler(tornado.web.StaticFileHandler, RequestHandlerMixin, print_init_info = False):
    async def get(self, *args, **kwargs):
        return await super().get(*args, **kwargs)

def cachedStaticFileHandlerFactory(cache_seconds):
    class _CacheStaticFileHandler(StaticFileHandler, print_init_info = False):
        def get_cache_time(self, path: str, modified: datetime | None, mime_type: str) -> int:
            return cache_seconds
    return _CacheStaticFileHandler

NoCacheStaticFileHandler = cachedStaticFileHandlerFactory(0)
class Application(tornado.web.Application):
    def __init__(self, debug = False) -> None:
        # will use simple storage service protocal (put, get, delete) to store data, when applicable
        handlers = [
            # Frontend
            (r'/()', NoCacheStaticFileHandler, {"path": LRSWEB_SRC_ROOT, "default_filename": "index.html"}),
            (r'/(index.html)', NoCacheStaticFileHandler, {"path": LRSWEB_SRC_ROOT}),
            (r'/(favicon.ico)', NoCacheStaticFileHandler, {"path": LRSWEB_SRC_ROOT}),
            (r'/(assets/.*)', NoCacheStaticFileHandler, {"path": LRSWEB_SRC_ROOT}),
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
            (r"/api/search", SearchHandler),                    # will be deprecated

            (r"/api/filter/basic", BasicFilterHandler),

            (r"/api/database/keys", DatabaseKeysHandler),
            (r"/api/database/tags", DatabaseTagsHandler),
            (r"/api/datainfo-list", DataInfoListHandler),
            (r"/api/datainfo/(.*)", DataInfoHandler),

            (r"/api/filelist", DataListHandler),                # will be deprecated
            (r"/api/filelist-stream", DataListStreamHandler),   # will be deprecated

            # additional information (supplementary data / resources) for each datapoint
            (r"/api/datainfo-supp/note/(.*)", NoteGetHandler),
            (r"/api/datainfo-supp/note-update/(.*)", NoteUpdateHandler),
            (r"/api/datainfo-supp/abstract/(.*)", AbstractGetHandler),
            (r"/api/datainfo-supp/abstract-update/(.*)", AbstractUpdateHandler),
            (r'/api/datafeat/tsne/(.*)', DataFeatureTSNEHandler),

            # iServer proxy
            (r"/api/iserver/(.*)", IServerProxyHandler),

            # data management
            (r"/api/dataman/delete", DataDeleteHandler),
            (r"/api/dataman/update", DataUpdateHandler),
            (r"/api/dataman/tag-rename", TagRenameHandler),
            (r"/api/dataman/tag-delete", TagDeleteHandler),

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
async def __startServer(
        host: str, 
        port: Union[int, str], 
        auto_reload: bool = False,
        ssl_config : _SSL_CONFIGT | None = None):

    app = Application()

    ssl_ctx = None
    if ssl_config is not None:
        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_cert_chain(certfile=ssl_config["certfile"], keyfile=ssl_config["keyfile"])
    server = HTTPServer(app, ssl_options=ssl_ctx)
    server.listen(address = host, port = int(port))

    # print info
    __serve_url = f"{'https' if ssl_config is not None else 'http'}://{host}:{port}"
    logging.getLogger('server').info("Starting server at: {}".format(__serve_url))
    with UseTermColor("lightgreen"):
        print("Visit web interface at: {}".format(__serve_url.replace("0.0.0.0", "127.0.0.1")))

    if auto_reload:
        tornado.autoreload.add_reload_hook(lambda: print("Server reloaded"))
        tornado.autoreload.start()

    async def buildIndex(op_interval: float = 0.05):
        print("Periodically build index")
        from lires.core.textUtils import buildFeatureStorage

        base_request_handler = RequestHandlerMixin()
        await buildFeatureStorage(
            iconn = g_storage.iconn,
            db = base_request_handler.db,
            vector_db = base_request_handler.vec_db,
            use_llm = False,
            operation_interval=op_interval,
        )
    
    tornado.ioloop.PeriodicCallback(buildIndex, 12*60*60*1000).start()  # in milliseconds
    tornado.ioloop.PeriodicCallback(g_storage.flush, 5*1000).start()    # periodically flush the database

    # exit hooks
    import signal
    async def __exitHook():
        await g_storage.finalize()
        await RequestHandlerBase.logger.info("Server shutdown")
        
    shutdown_event = asyncio.Event()
    # catch keyboard interrupt
    async def __signalHandler(*args, **kwargs):
        with UseTermColor("green"):
            print("\nExit gracefully...")
        await __exitHook()
        with UseTermColor("green"):
            print("Hook invoked.")
        # send event to stop the loop, 
        shutdown_event.set()

    # https://stackoverflow.com/questions/23313720/asyncio-how-can-coroutines-be-used-in-signal-handlers
    loop = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame),
                                lambda: asyncio.ensure_future(__signalHandler()))
    await shutdown_event.wait()

# SSL config
_ENV_CERTFILE = os.environ.get("LRS_SSL_CERTFILE", "")
_ENV_KEYFILE = os.environ.get("LRS_SSL_KEYFILE", "")
SSL_CONFIG: _SSL_CONFIGT | None
if bool(_ENV_CERTFILE) != bool(_ENV_KEYFILE):
    # if only one of them is set
    raise ValueError("LRS_SSL_CERTFILE and LRS_SSL_KEYFILE must be both set or both not set")
if _ENV_CERTFILE:
    SSL_CONFIG = {"certfile": _ENV_CERTFILE, "keyfile": _ENV_KEYFILE} # type: ignore
else:
    SSL_CONFIG = None

def startServer(
        host: str, 
        port: int | str, 
        ) -> None:
    asyncio.run(
        __startServer(
            host = host, 
            port = port, 
            ssl_config = SSL_CONFIG, 
            auto_reload = os.environ.get("LRS_DEV", "0") == "1"
        )
    )

if __name__ == "__main__":
    startServer('127.0.0.1', 8080)
