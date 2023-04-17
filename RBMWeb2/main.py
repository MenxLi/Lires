from . import RBMWEB2_SRC_ROOT
from typing import Union
import multiprocessing
import tornado
import tornado.ioloop
import tornado.web
import tornado.autoreload

class Application(tornado.web.Application):
    def __init__(self) -> None:
        handlers = [
            # Frontend
            (r'/(.*)', tornado.web.StaticFileHandler, {"path": RBMWEB2_SRC_ROOT, "default_filename": "index.html"}),
        ]
        super().__init__(handlers)

def startServer(port: Union[int, str] = 8081):
    app = Application()
    print("Starting RBMWeb server at port: ", port)
    app.listen(int(port))
    tornado.autoreload.add_reload_hook(lambda: print("Server reloaded"))
    tornado.autoreload.start()
    tornado.ioloop.IOLoop.current().start()

def startServerProcess(*args) -> multiprocessing.Process:
    p = multiprocessing.Process(target=startServer, args=args)
    p.start()
    return p


if __name__ == "__main__":
    startServer(8081)
