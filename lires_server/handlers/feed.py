
from ._base import *
import json
from lires.api.feed import FServerConn

class FeedHandler(RequestHandlerBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fconn = FServerConn()
    
    @keyRequired
    async def post(self):
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(await self.fconn.getLatest(
            max_results=int(self.get_argument("max_results", "10")),
            category=self.get_argument("category")
        )))
