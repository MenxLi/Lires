from typing import Union
import os, multiprocessing
import tornado.ioloop
import tornado.web

def startWebpageServer(port: Union[int, str] = 8080):
    root = os.path.dirname(__file__)

    application = tornado.web.Application([
        (r"/(.*)", tornado.web.StaticFileHandler, {"path": root, "default_filename": "index.html"})
    ])
    application.listen(port)
    print("Starting webpage server at port:", port)
    tornado.ioloop.IOLoop.instance().start()


def startWebpageServerProcess(*args) -> multiprocessing.Process:
    p = multiprocessing.Process(target = startWebpageServer, args = args)
    p.start()
    return p

if __name__ == '__main__':
    startWebpageServer(8080)
