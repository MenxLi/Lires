from ._base import *
import json

class AuthHandler (tornado.web.RequestHandler, RequestHandlerMixin):
    @keyRequired
    async def post(self):
        self.setDefaultHeader()

        require_permission = self.get_argument("require_permission")
        if not require_permission:
            self.write("Success")
        else:
            self.write(json.dumps(self.permission))