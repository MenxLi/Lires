from ._base import *
import json

class AuthHandler (tornado.web.RequestHandler, RequestHandlerMixin):
    @keyRequired
    async def post(self):
        self.allowCORS()

        require_user_info = self.get_argument("require_user_info")
        if not require_user_info:
            self.write("Success")
        else:
            self.write(json.dumps(self.user_info))