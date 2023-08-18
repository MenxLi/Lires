from ._base import *
import json

class AuthHandler (tornado.web.RequestHandler, RequestHandlerMixin):
    def post(self):
        self.setDefaultHeader()
        self.logger.debug(f"get auth request")
        permission = self.checkKey()

        require_permission = self.get_argument("require_permission")
        if not require_permission:
            self.write("Success")
        else:
            self.write(json.dumps(permission))