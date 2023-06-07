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
        print(res)
        for k in res.keys():
            this_res = res[k]
            print(this_res)
            if this_res is not None:
                # Make sure the result is serializable
                print(this_res["match"])
                this_res["match"] = None
        self.write(json.dumps(res))
