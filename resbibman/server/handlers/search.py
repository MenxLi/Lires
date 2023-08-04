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
        if method == "searchFeature":
            kwargs["vec_db"] = self.vec_db
        searcher.setRunConfig(method, kwargs)
        res = searcher.run()
        for k in res.keys():
            this_res = res[k]
            if this_res is not None:
                # Make sure the result is serializable
                this_res["match"] = None
        self.write(json.dumps(res))
