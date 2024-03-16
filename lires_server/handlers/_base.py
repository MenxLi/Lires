from __future__ import annotations
from typing import Callable, Optional, List, Generator, AsyncGenerator, TypeVar, Any, TYPE_CHECKING
import tornado.web, tornado.websocket
import asyncio
import json

import http.cookies
from ._global_data import GlobalStorage
from lires.user import UserInfo, UserPool
from lires.core.base import LiresBase
from lires.core.dataTags import DataTags
from lires.utils import BCOLORS

from ..types import Event
if TYPE_CHECKING:
    from .websocket import WebsocketHandler

T = TypeVar("T")
FuncT = TypeVar("FuncT", bound=Callable)
def keyRequired(func: FuncT) -> FuncT:
    """
    Decorator to check if user is logged in
    """
    async def wrapper(self: RequestHandlerMixin, *args, **kwargs):
        await self.checkKey()
        # check async 
        if asyncio.iscoroutinefunction(func):
            return await func(self, *args, **kwargs)
        else:
            return func(self, *args, **kwargs)
    return wrapper  # type: ignore

# Server level global storage
def __init_global_storage():
    from lires.api import IServerConn
    from lires.loader import initResources
    user_pool, db_pool = asyncio.run(initResources())
    iconn = IServerConn()
    return GlobalStorage(user_pool=user_pool, database_pool=db_pool, iconn=iconn)

g_storage = __init_global_storage()
_ws_connections: list[WebsocketHandler] = []

class RequestHandlerMixin(LiresBase):
    get_argument: Callable
    get_cookie: Callable[[str, Optional[str]], Optional[str]]
    set_header: Callable
    cookies: http.cookies.SimpleCookie
    logger = LiresBase.loggers().server

    # class settings
    print_init_info = True

    def __init_subclass__(cls, print_init_info: bool = True, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls.print_init_info = print_init_info

    def __init__(self, *args, **kwargs) -> None:
        if self.print_init_info:
            async def _print_init_info():
                await self.logger.debug(f"{BCOLORS.YELLOW} [init] :: {self.__class__.__name__} {BCOLORS.ENDC}")
            self.io_loop.create_task(_print_init_info())

    @property
    def io_loop(self):
        return asyncio.get_event_loop()
    
    async def wrapAsyncIter(self, gen: Generator[T, None, Any] | list[T]) -> AsyncGenerator[T, None]:
        for item in gen:
            await asyncio.sleep(0)  # make the control back to the event loop, tricky
            yield item
    
    async def db(self):
        return ( await g_storage.database_pool.get((await self.userInfo())["id"]) ).database
    
    async def vec_db(self):
        return ( await g_storage.database_pool.get((await self.userInfo())["id"]) ).vector_db

    @property
    def user_pool(self): return g_storage.user_pool
    @property
    def db_pool(self): return g_storage.database_pool
    @property
    def iconn(self): return g_storage.iconn
    
    @property
    def connection_pool(self) -> list[WebsocketHandler]:
        return _ws_connections
    
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
    
    async def userInfo(self) -> UserInfo:
        try:
            # use cached permission, from checkKey()
            return self.__account_info
        except AttributeError:
            return await self.checkKey()
    
    async def userInfoDesensitized(self) -> UserInfo:
        info = await self.userInfo()
        info["enc_key"] = "__HIDDEN__"
        return info
    
    async def checkKey(self) -> UserInfo:
        """
        Authenticates key from params, then cookies
        Will raise HTTPError if key is invalid
        """
        enc_key = self.enc_key
        if not enc_key:
            await self.logger.debug("No key found, abort")
            raise tornado.web.HTTPError(403) 

        res = await self.user_pool.getUserByKey(enc_key)
        if res is None:
            # unauthorized or user not found
            await self.logger.debug("Reject key ({})".format(enc_key))
            raise tornado.web.HTTPError(403) 
        
        # Set a cached permission, requires it via property
        user_info = await res.info()
        self.__account_info = user_info
        return user_info
    
    @staticmethod
    async def checkTagPermission(_tags: List[str] | DataTags, _mandatory_tags: List[str], raise_error=True) -> bool:
        """
        Check if tags are dominated by mandatory_tags
        """
        tags = DataTags(_tags)
        mandatory_tags = DataTags(_mandatory_tags)
        await RequestHandlerMixin.logger.debug(f"check tag permission: {tags} vs {mandatory_tags}")
        if not mandatory_tags.issubset(tags.withParents()):
            await RequestHandlerMixin.logger.debug("Tag permission denied")
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

    async def broadcastEventMessage(self, event: Event, to_all: bool = False):
        """
        Inform all connected clients about an event
        - to_all: if True, the event will be broadcasted to all clients, 
            otherwise, it will be broadcasted to all clients of the same user
        """
        await self.logger.debug("Broadcast message - " + str(event))

        # there will somehow exists closed connections in the pool
        # we need to remove them, otherwise they will block the function and slow down the server
        # TODO: find out why...
        __need_remove_idx = []
        if not to_all:
            __this_user_id = (await self.userInfo())["id"]
        for i in range(len(self.connection_pool)):
            conn = self.connection_pool[i]
            if conn is self:
                # exlude self, currently only applies to login/logout events
                continue
            if not to_all and conn.user_id != __this_user_id:
                # skip if not to all and not the same user
                continue
            try:
                conn.write_message(json.dumps({
                    "type": "event",
                    "content": event
                }))
            except tornado.websocket.WebSocketClosedError as e:
                await self.logger.error("Failed to broadcast to closed socket (s: {})".format(conn.session_id))
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

__all__ = [
    "tornado",
    "RequestHandlerMixin",
    "RequestHandlerBase",
    "keyRequired"
    ]