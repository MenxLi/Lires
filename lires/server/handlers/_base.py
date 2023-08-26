from __future__ import annotations
from typing import Callable, Optional, List, Awaitable, Generator, AsyncGenerator, TypeVar
import tornado.web
from tornado.ioloop import IOLoop
import asyncio
import concurrent.futures
import time

import http.cookies
from ..auth.account import AccountPermission
from ..auth.encryptServer import queryAccount
from ..discussUtils import DiscussDatabase
from lires.core import globalVar as G
from lires.core.dataClass import DataBase, DataTags
from lires.confReader import getConf, VECTOR_DB_PATH
from lires.core.utils import BCOLORS
from tiny_vectordb import VectorDatabase

G.init()
def getLocalDatabasePath():
    return getConf()['database']

def loadDataBase(db_path: str):
    G.logger_lrs_server.info("Loading database: {}".format(db_path))
    db = DataBase()
    db.init(db_path, force_offline=True)
    return db

FuncT = TypeVar("FuncT", bound=Callable[..., Awaitable])
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
    return wrapper

class RequestHandlerMixin():
    get_argument: Callable
    get_cookie: Callable[[str, Optional[str]], Optional[str]]
    set_header: Callable
    cookies: http.cookies.SimpleCookie
    db_path: str = getLocalDatabasePath()
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
    
    async def wrapAsyncIter(self, gen: Generator) -> AsyncGenerator:
        for item in gen:
            await asyncio.sleep(0)  # make the control back to the event loop, tricky
            yield item

    def initdb(self):
        """
        Initialize / reload the database
        """
        self.logger.debug("Initializing server global database objects")
        if G.hasGlobalAttr("server_db"):
            db: DataBase = G.getGlobalAttr("server_db")
            db.destroy()
        G.setGlobalAttr("server_db", loadDataBase(getLocalDatabasePath()))
        G.setGlobalAttr("server_discussion_db", DiscussDatabase())
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
    def discussion_db(self) -> DiscussDatabase:
        return G.getGlobalAttr("server_discussion_db")
    
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
        return enc_key
    
    @property
    def permission(self) -> AccountPermission:
        try:
            # use cached permission, from checkKey()
            return self.__account_perm
        except AttributeError:
            return self.checkKey()
    
    def checkKey(self) -> AccountPermission:
        """
        Authenticates key from params, then cookies
        Will raise HTTPError if key is invalid
        """
        enc_key = self.enc_key
        self.logger.debug(f"check key: {enc_key}")
        if not enc_key:
            raise tornado.web.HTTPError(403) 

        res = queryAccount(enc_key)
        if res is None:
            # unauthorized
            print("Reject key ({}), abort".format(enc_key))
            raise tornado.web.HTTPError(403) 
        
        # Set a cached permission, requires it via property
        self.__account_perm = res
        return res
    
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

    def setDefaultHeader(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, PUT, DELETE, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header("Access-Control-Expose-Headers", "*")

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
        return wrapper
    return decorator

__all__ = [
    "tornado",
    "RequestHandlerMixin",
    "G",
    "minResponseInterval",
    "keyRequired"
    ]