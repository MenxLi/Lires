from ._base import *
import json

class AuthHandler (tornado.web.RequestHandler, RequestHandlerMixin):
    @keyRequired
    async def post(self):
        self.allowCORS()
        self.write(json.dumps(self.user_info))