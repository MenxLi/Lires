import asyncio
import tornado.web
    
from resbibman.server.handlers._base import *


class MainHandler(RequestHandlerBase):
    def get(self):
        ...
    
    def post(self):
        ...

def main():
    app = tornado.web.Application([
        (r"/", MainHandler),
    ])
    app.listen(8888)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()