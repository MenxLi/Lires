
from __future__ import annotations
import tornado
from ._base import *
import tornado.websocket
from lires.core.logger import LiresLogger

class WebsocketHandler(tornado.websocket.WebSocketHandler, RequestHandlerMixin):
    """
    This handler mainly deals with user events from frontend
    and broadcast them to other users
    """
    logger: LiresLogger
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # register to global connection pool
        self.connection_pool.append(self)
        self._session_id = self.get_argument("session_id", "")
    
    @property
    def session_id(self):
        return self._session_id

    # def check_origin(self, origin):
    #     # allowing alternate origins
    #     parsed_origin = urllib.parse.urlparse(origin)
    #     await self.logger.debug(f"check origin: {parsed_origin.netloc}")
    #     return True

    @keyRequired
    async def open(self):
        await self.logger.info("WebSocket opened from {} (s: {})".format((await self.userInfo())['username'], self.session_id))
        await self.broadcastEventMessage({
            'type': 'login',
            'username': (await self.userInfo())['username'],
            'user_info': await self.userInfoDesensitized(),
        })

    async def on_close(self):
        await self.logger.info("WebSocket closed from {} (s: {})".format((await self.userInfo())['username'], self.session_id))
        await self.broadcastEventMessage({
            'type': 'logout',
            'username': (await self.userInfo())['username'],
            'user_info': await self.userInfoDesensitized(),
        })
        try:
            # unregister from global connection pool
            self.connection_pool.remove(self)
        except IndexError:
            await self.logger.error("WebSocket connection not found in connection pool, skipped")

    async def on_message(self, message):
        # TODO: to deal with user interactions
        await self.logger.debug(f"WebSocket message: {message}")
        pass

__all__ = ["WebsocketHandler"]