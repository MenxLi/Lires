
from __future__ import annotations
import tornado
from ._base import *
import logging
import tornado.websocket
import urllib.parse

class WebsocketHandler(tornado.websocket.WebSocketHandler, RequestHandlerMixin):
    """
    This handler mainly deals with user events from frontend
    and broadcast them to other users
    """

    # type hints
    logger: logging.Logger

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # register to global connection pool
        self.connection_pool.append(self)
        self._session_id = self.get_argument("session_id", "")
    
    @property
    def session_id(self):
        return self._session_id

    def check_origin(self, origin):
        # allowing alternate origins
        parsed_origin = urllib.parse.urlparse(origin)
        self.logger.debug(f"check origin: {parsed_origin.netloc}")
        return True

    @keyRequired
    def open(self):
        self.logger.info("WebSocket opened from {} (s: {})".format(self.user_info['username'], self.session_id))
        self.broadcastEventMessage({
            'type': 'login',
            'username': self.user_info['username'],
            'user_info': self.user_info_desensitized,
        })

    def on_close(self):
        self.logger.info("WebSocket closed from {} (s: {})".format(self.user_info['username'], self.session_id))
        self.broadcastEventMessage({
            'type': 'logout',
            'username': self.user_info['username'],
            'user_info': self.user_info_desensitized,
        })
        try:
            # unregister from global connection pool
            self.connection_pool.remove(self)
        except IndexError:
            self.logger.error("WebSocket connection not found in connection pool, skipped")

    def on_message(self, message):
        # TODO: to deal with user interactions
        self.logger.debug(f"WebSocket message: {message}")
        pass

__all__ = ["WebsocketHandler"]