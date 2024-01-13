from ._base import *
import json

class AuthHandler (RequestHandlerBase):
    @keyRequired
    async def post(self):
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(self.user_info))
    
    @keyRequired
    async def get(self):
        await self.post()