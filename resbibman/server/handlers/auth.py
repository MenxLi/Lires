from ._base import *

class AuthHandler (tornado.web.RequestHandler, RequestHandlerBase):
    def post(self):
        self.setDefaultHeader()
        if self.checkKey():
            self.write("Success")