from __future__ import annotations
from typing import Callable, Optional, List, Generator, AsyncGenerator, TypeVar, Any, TYPE_CHECKING
import tornado.web, tornado.websocket
import asyncio
import json

import http.cookies
from ._global_data import GlobalStorage
from lires.user import UserInfo
from lires.core.base import LiresBase
from lires.core.dataTags import DataTags
from lires.core.vecutils import updateFeture, deleteFeature
from lires.utils import BCOLORS

from abc import abstractmethod

from ..types import Event
if TYPE_CHECKING:
    from .websocket import WebsocketHandler
    from lires.core.dataClass import DataBase, DataPoint
    from lires.vector.database import VectorDatabase

T = TypeVar("T")
FuncT = TypeVar("FuncT", bound=Callable)
def authenticate(
    enabled: bool = True, 
    admin_required: bool = False,
    ) -> Callable[[FuncT], FuncT]:
    if not enabled:
        return lambda x: x

    def _authenticate(func: FuncT) -> FuncT:
        """
        Decorator to check if user is logged in
        """
        async def wrapper(self: RequestHandlerMixin, *args, **kwargs):
            user_info = await self.checkKey()
            if admin_required and not user_info["is_admin"]:
                raise tornado.web.HTTPError(403)

            # check async 
            if asyncio.iscoroutinefunction(func):
                return await func(self, *args, **kwargs)
            else:
                return func(self, *args, **kwargs)
        return wrapper  # type: ignore
    return _authenticate

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
    request: tornado.httputil.HTTPServerRequest
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
        self.__account_info: Optional[UserInfo] = None

    @property
    def io_loop(self):
        return asyncio.get_event_loop()
    
    async def wrapAsyncIter(self, gen: Generator[T, None, Any] | list[T]) -> AsyncGenerator[T, None]:
        for item in gen:
            await asyncio.sleep(0)  # make the control back to the event loop, tricky
            yield item
    
    async def inferUserId(self) -> int:
        """
        Try to identify user id from different sources
        """
        # first check if user id is already recorded
        # this is important, otherwise, 
        # this create a vulnerability that allows users 
        # to access other users' data by changing the url parameters
        if self.__account_info:
            return self.__account_info["id"]
        
        # then try to get user id from params, this is for non-logged-in requests
        for _user_id_candidate in ["_userid", "_u", "u"]:
            user_id = self.get_argument(_user_id_candidate, None)
            if user_id is not None:
                break
        if user_id is not None:
            user = await self.user_pool.getUserById(int(user_id))
            if user is not None: return user.id

        user_name = self.get_argument("_username", None)
        if user_name is not None:
            user = await self.user_pool.getUserByUsername(user_name)
            if user is not None: return user.id
            
        # if not found, get user id from key
        return (await self.userInfo())["id"]
    
    async def db(self) -> DataBase:
        return ( await g_storage.database_pool.get( await self.inferUserId() ) )
    
    async def vec_db(self) -> VectorDatabase:
        return (await self.db()).vector

    @property
    def user_pool(self): return g_storage.user_pool
    @property
    def db_pool(self): return g_storage.database_pool
    @property
    def iconn(self): return g_storage.iconn
    
    @property
    def connection_pool(self) -> list[WebsocketHandler]:
        return _ws_connections
    
    def connectionsByUserID(self, user_id: int) -> list[WebsocketHandler]:
        return [conn for conn in self.connection_pool if conn.user_id == user_id]
    
    def getAuthToken(self) -> str:
        # first try to get key from headers
        # `Authorization` is a common header for key, 
        # use this should be a better practice
        # e.g. when using a reverse proxy, it is easier to set headers
        enc_key = self.request.headers.get("Authorization", "")
        if enc_key:
            # assume the key is in the format of "Bearer <key>"
            enc_key = enc_key.split(" ")[-1]
            return enc_key

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
    def session_id(self) -> str:
        return self.get_argument("session_id", "")
    
    async def userInfo(self) -> UserInfo:
        # use cached permission, from checkKey()
        if self.__account_info:
            return self.__account_info
        return await self.checkKey()
    
    async def userInfoDesensitized(self) -> UserInfo:
        info = await self.userInfo()
        info["enc_key"] = "__HIDDEN__"
        return info
    
    async def checkKey(self) -> UserInfo:
        """
        Authenticates key from headers, params, then cookies
        Will raise HTTPError if key is invalid
        """
        enc_key = self.getAuthToken()
        if not enc_key:
            await self.logger.debug("No key found, abort")
            raise tornado.web.HTTPError(401) 

        res = await self.user_pool.getUserByKey(enc_key)
        if res is None:
            # unauthorized or user not found
            await self.logger.debug("Reject key ({})".format(enc_key))
            raise tornado.web.HTTPError(401) 
        
        # update the last active time
        await res.refreshActiveTime()
        
        # Set a cached permission, requires it via property
        user_info = await res.info()
        self.__account_info = user_info
        return user_info

    async def ensureFeatureUpdate(self, dp: DataPoint):
        """
        Ensure the feature is updated
        """
        vec_db = await self.vec_db()
        asyncio.ensure_future(updateFeture(vec_db, self.iconn, dp))
        await self.logger.debug(f"Feature update for {dp.uuid}")
    
    async def deleteFeature(self, dp: DataPoint):
        """
        Delete the feature
        """
        vec_db = await self.vec_db()
        await deleteFeature(vec_db, dp)
        await self.logger.debug(f"Feature deleted for {dp.uuid}")
    
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
        event["session_id"] = self.session_id
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
        self.set_header('robot', 'noindex, nofollow, noarchive')
        self.allowCORS()

    def options(self, *args, **kwargs):
        # Handle preflight requests
        self.set_status(204)
        self.finish()
    
    def _handle_request_exception(self, e: BaseException) -> None:
        if isinstance(e, self.Error.LiresEntryNotFoundError):
            self.send_error(404, reason="Entry not found")
        elif isinstance(e, self.Error.LiresUserNotFoundError):
            self.send_error(404, reason="User not found")
        else:
            return super()._handle_request_exception(e)

class ReverseProxyHandlerBase(RequestHandlerBase):
    """
    NOT TESTED!
    """
    SUPPORTED_METHODS = ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]

    async def get(self, *args, **kwargs): await self.handle_request()
    async def post(self, *args, **kwargs): await self.handle_request()
    async def put(self, *args, **kwargs): await self.handle_request()
    async def delete(self, *args, **kwargs): await self.handle_request()
    async def head(self, *args, **kwargs): await self.handle_request()
    async def options(self, *args, **kwargs): await self.handle_request()

    @property
    def basePath(self) -> str:   # i.e. /api/v1
        return ''

    @abstractmethod
    async def aimHost(self) -> str:...

    async def handle_request(self):
        http = tornado.httpclient.AsyncHTTPClient()

        if uri:=self.request.uri:
            assert uri.startswith(self.basePath), "uri must start with basePath"
            uri = uri[len(self.basePath):]
            url = await self.aimHost() + uri
        else:
            url = await self.aimHost()
        await self.logger.info(f"Proxying request to {url}")
        response = await http.fetch(url,
                   method=self.request.method,
                   body=self.request.body if self.request.body else None,
                   headers=self.request.headers,
                   follow_redirects=False,
                   allow_nonstandard_methods=True,
                   )
        for header, value in response.headers.get_all():
            if header not in ('Transfer-Encoding', 'Content-Encoding', 'Content-Length', 'Connection'):
                self.set_header(header, value)
        self.write(response.body)
        self.finish()


__all__ = [
    "tornado",
    "RequestHandlerMixin",
    "RequestHandlerBase",
    "authenticate"
    ]