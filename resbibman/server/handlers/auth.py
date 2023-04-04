from ._base import *
import json

class AuthHandler (tornado.web.RequestHandler, RequestHandlerBase):
    def post(self):
        print("Get auth request")
        self.setDefaultHeader()
        permission = self.checkKey()

        require_permission = self.get_argument("require_permission", default = False)
        if not require_permission:
            self.write("Success")
        else:
            self.write(json.dumps(permission))