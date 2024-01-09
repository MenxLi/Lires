from __future__ import annotations
from typing import Callable, Optional, List, Awaitable, Generator, AsyncGenerator, TypeVar, Any, TYPE_CHECKING
import tornado.web, tornado.websocket
from tornado.ioloop import IOLoop
import asyncio
import concurrent.futures
import time, json

import http.cookies
from lires.user import UserInfo, UserPool
from lires.confReader import DATABASE_DIR
from lires.core import globalVar as G
from lires.core.dataClass import DataBase, DataTags
from lires.confReader import USER_DIR, VECTOR_DB_PATH, getConf
from lires.core.utils import BCOLORS
from lires.types.eventT import Event
from tiny_vectordb import VectorDatabase, VectorCollection

if TYPE_CHECKING:
    from .websocket import WebsocketHandler

def getLocalDatabasePath():
    return DATABASE_DIR

def loadDataBase(db_path: str):
    G.logger_lrs_server.info("Loading database: {}".format(db_path))
    db = DataBase()
    db.init(db_path)
    return db

T = TypeVar("T")
FuncT = TypeVar("FuncT", bound=Callable)
def keyRequired(func: FuncT) -> FuncT:
    """
    Decorator to check if user is logged in
    """
    async def wrapper(self: RequestHandlerMixin, *args, **kwargs):
        self.checkKey()
        # check async 
        if asyncio.iscoroutinefunction(func):
            return await func(self, *args, **kwargs)
        else:
            return func(self, *args, **kwargs)
    return wrapper  # type: ignore

class RequestHandlerMixin():
    get_argument: Callable
    get_cookie: Callable[[str, Optional[str]], Optional[str]]
    set_header: Callable
    cookies: http.cookies.SimpleCookie
    db_path: str = DATABASE_DIR
    logger = G.logger_lrs_server

    # Set max_workers to larger than 1 will somehow cause blocking 
    # if iserver is running in a container (it's ok if runs on host), 
    # and we are sending offloaded featurize requests from the core server with multiple threads...
    # (Happened on MacOS with Docker version 24.0.5, build ced0996)
    # (Not observed on OpenSUSE-leap 15 with Docker version 23.0.6-ce, build 9dbdbd4b6d76)
    # (More tests needed ... )
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

    def __init__(self, *args, **kwargs) -> None:
        self.logger.debug(f"{BCOLORS.YELLOW} [init] :: {self.__class__.__name__} {BCOLORS.ENDC}")

    @property
    def io_loop(self):
        return IOLoop.current()
    
    def offloadTask(self, func, *args, **kwargs) -> Awaitable:
        """
        Offload a blocking task to a thread pool
        """
        return self.io_loop.run_in_executor(self.executor, func, *args, **kwargs)
    
    async def wrapAsyncIter(self, gen: Generator[T, None, Any] | list[T]) -> AsyncGenerator[T, None]:
        for item in gen:
            await asyncio.sleep(0)  # make the control back to the event loop, tricky
            yield item

    def initdb(
            self, 
            load_db: bool = True,
            load_vec_db: bool = True,
            load_user_pool: bool = True,
            ):
        """
        Initialize / reload the database
        """
        self.logger.debug("Initializing server global database objects")
        if load_db:
            if G.hasGlobalAttr("server_db"):
                db: DataBase = G.getGlobalAttr("server_db")
                db.destroy()
            G.setGlobalAttr("server_db", loadDataBase(DATABASE_DIR))
        if load_vec_db:
            # Set global vector collection compiling config
            VectorCollection.COMPILE_CONFIG = getConf()["tiny_vectordb_compile_config"]

            if G.hasGlobalAttr("vec_db"):
                vec_db: VectorDatabase = G.getGlobalAttr("vec_db")
                vec_db.flush()
                vec_db.commit()
            G.setGlobalAttr(
                "vec_db", 
                VectorDatabase(VECTOR_DB_PATH, [
                    {
                        "name": "doc_feature",
                        "dimension": 768
                    },
                ]))
        if load_user_pool:
            if G.hasGlobalAttr("user_pool"):
                user_pool: UserPool = G.getGlobalAttr("user_pool")
                user_pool.destroy()
            G.setGlobalAttr("user_pool", UserPool(USER_DIR))
    
    # initdb(None)    # type: ignore
    
    @property
    def db(self) -> DataBase:
        if not G.hasGlobalAttr("server_db"):
            self.initdb()
        return G.getGlobalAttr("server_db")
    
    @property
    def vec_db(self) -> VectorDatabase:
        if not G.hasGlobalAttr("vec_db"):
            self.initdb()
        return G.getGlobalAttr("vec_db")
    
    @property
    def user_pool(self) -> UserPool:
        if not G.hasGlobalAttr("user_pool"):
            self.initdb()
        return G.getGlobalAttr("user_pool")
    
    @property
    def connection_pool(self) -> list[WebsocketHandler]:
        if not G.hasGlobalAttr('WSConnections'):
            G.setGlobalAttr('WSConnections', [])
        return G.getGlobalAttr('WSConnections')
    
    @property
    def enc_key(self) -> str:
        try:
            enc_key = self.get_argument("key", "")
        except tornado.web.HTTPError:
            enc_key = ""
            # no key defined in params, try cookies
            for _k in ["LRS_ENC_KEY", "encKey"]:
                enc_key = self.get_cookie(_k, "")
                if enc_key:
                    break
            assert isinstance(enc_key, str), "Not found key in params or cookies"
        return enc_key
    
    @property
    def user_info(self) -> UserInfo:
        try:
            # use cached permission, from checkKey()
            return self.__account_info
        except AttributeError:
            return self.checkKey()
    
    @property
    def user_info_desensitized(self) -> UserInfo:
        info = self.user_info
        info["enc_key"] = "__HIDDEN__"
        return info
    
    def checkKey(self) -> UserInfo:
        """
        Authenticates key from params, then cookies
        Will raise HTTPError if key is invalid
        """
        enc_key = self.enc_key
        self.logger.debug(f"check key: {enc_key}")
        if not enc_key:
            raise tornado.web.HTTPError(403) 

        res = self.user_pool.getUserByKey(enc_key)
        if res is None:
            # unauthorized or user not found
            print("Reject key ({}), abort".format(enc_key))
            raise tornado.web.HTTPError(403) 
        
        # Set a cached permission, requires it via property
        user_info = res.info()
        self.__account_info = user_info
        return user_info
    
    @staticmethod
    def checkTagPermission(_tags: List[str] | DataTags, _mandatory_tags: List[str], raise_error=True) -> bool:
        """
        Check if tags are dominated by mandatory_tags
        """
        tags = DataTags(_tags)
        mandatory_tags = DataTags(_mandatory_tags)
        RequestHandlerMixin.logger.debug(f"check tags: {tags} vs {mandatory_tags}")
        if not mandatory_tags.issubset(tags.withParents()):
            if raise_error:
                raise tornado.web.HTTPError(403)
            else:
                return False
        return True

    def allowCORS(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, PUT, DELETE, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header("Access-Control-Expose-Headers", "*")

    def broadcastEventMessage(self, event: Event):
        """
        Inform all connected clients about an event
        """
        self.logger.debug("Broadcast message - " + str(event))

        # there will somehow exists closed connections in the pool
        # we need to remove them, otherwise they will block the function and slow down the server
        # TODO: find out why...
        __need_remove_idx = []
        for i in range(len(self.connection_pool)):
            conn = self.connection_pool[i]
            if conn is not self:
                try:
                    conn.write_message(json.dumps({
                        "type": "event",
                        "content": event
                    }))
                except tornado.websocket.WebSocketClosedError as e:
                    self.logger.error("Failed to broadcast to closed socket (s: {})".format(conn.session_id))
                    __need_remove_idx.append(i)
        for i in __need_remove_idx[::-1]:
            self.connection_pool.pop(i)

class RequestHandlerBase(tornado.web.RequestHandler, RequestHandlerMixin):
    def set_default_headers(self):
        self.allowCORS()

    def options(self, *args, **kwargs):
        # Handle preflight requests
        self.set_status(204)
        self.finish()

def minResponseInterval(min_interval=0.1):
    """
    Decorator to limit the minimum interval between responses
    """
    last_response_time = 0
    def decorator(func: FuncT) -> FuncT:
        async def wrapper(*args, **kwargs):
            nonlocal last_response_time
            while True:
                now = time.time()
                if now - last_response_time < min_interval:
                    await asyncio.sleep(min_interval - (now - last_response_time))
                else:
                    break
            last_response_time = time.time()
            return await func(*args, **kwargs)
        return wrapper  # type: ignore
    return decorator

__all__ = [
    "tornado",
    "RequestHandlerMixin",
    "RequestHandlerBase",
    "G",
    "minResponseInterval",
    "keyRequired"
    ]