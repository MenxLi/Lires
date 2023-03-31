from ._base import *
from resbibman.core.dataSearcher import DataSearcher
import json

class SearchHandler(tornado.web.RequestHandler, RequestHandlerBase):
    def post(self):
        self.checkKey()
        self.setDefaultHeader()

        method = self.get_argument("method")
        kwargs = json.loads(self.get_argument("kwargs"))

        searcher = DataSearcher(self.db)
        searcher.setRunConfig(method, kwargs)
        res = searcher.run()
        for k in res.keys():
            # match object is not json serializable, set to None
            res[k] = None
        self.write(json.dumps(res))
