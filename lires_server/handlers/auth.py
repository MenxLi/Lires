from ._base import *
import json

class AuthHandler (RequestHandlerBase):
    @keyRequired
    async def post(self):
        self.write(json.dumps(self.user_info))