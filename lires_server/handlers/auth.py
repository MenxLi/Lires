from ._base import *
import json

class AuthHandler (RequestHandlerBase):
    @authenticate()
    async def post(self):
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(await self.user_info()))
    
    @authenticate()
    async def get(self):
        await self.post()