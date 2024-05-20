
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
        self._user_id = None
    
    @property
    def session_id(self): return self._session_id
    @property
    def user_id(self) -> int:
        if self._user_id is None:
            raise ValueError("User ID not found")
        return self._user_id

    def check_origin(self, _):
        # allowing alternate origins
        # for now, we allow all origins for development, 
        # may change in the future
        return True

    @authenticate()
    async def open(self):
        await self.logger.info("WebSocket opened from {} (s: {})".format((await self.userInfo())['username'], self.session_id))
        self._user_id = (await self.userInfo())['id']
        await self.broadcastEventMessage({
            'type': 'login',
            'username': (await self.userInfo())['username'],
            'user_info': await self.userInfoDesensitized(),
        }, to_all=True)

    def on_close(self):
        # in the current version of tornado, on_close is not called as a coroutine
        async def _on_close():
            await self.logger.info("WebSocket closed from {} (s: {})".format((await self.userInfo())['username'], self.session_id))
            await self.broadcastEventMessage({
                'type': 'logout',
                'username': (await self.userInfo())['username'],
                'user_info': await self.userInfoDesensitized(),
            }, to_all=True)
            try:
                # unregister from global connection pool
                self.connection_pool.remove(self)
            except (IndexError, ValueError):
                await self.logger.error("WebSocket connection not found in connection pool, skipped")
        tornado.ioloop.IOLoop.current().add_callback(_on_close)

    async def on_message(self, message):
        # TODO: to deal with user interactions
        await self.logger.debug(f"WebSocket message: {message}")
        pass

__all__ = ["WebsocketHandler"]