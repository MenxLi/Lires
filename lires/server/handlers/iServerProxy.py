
from ._base import *
import json
from lires.core.serverConn import IServerConn


class IServerProxyHandler(tornado.web.RequestHandler, RequestHandlerMixin):
    def post(self, key):
        self.setDefaultHeader()

        if key == "textFeature":
            self.checkKey()
            text = self.get_argument("text")

            self.logger.debug("textFeature request")
            ret = IServerConn().featurize(text)
            if ret is None:
                raise tornado.web.HTTPError(500, "iServer error")
            else:
                self.write(json.dumps(ret))
        
        else:
            raise tornado.web.HTTPError(404, "Unknown key")

