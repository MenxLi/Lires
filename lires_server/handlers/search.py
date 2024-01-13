from ._base import *
from lires.core.dataSearcher import DataSearcher
import json

class SearchHandler(RequestHandlerBase):

    @keyRequired
    async def post(self):

        method = self.get_argument("method")
        kwargs = json.loads(self.get_argument("kwargs"))

        searcher = DataSearcher(self.db)
        if method == "searchFeature":
            kwargs["iconn"] = self.iconn
            kwargs["vec_db"] = self.vec_db
        searcher.setRunConfig(method, kwargs)
        res = await searcher.run()
        for k in res.keys():
            this_res = res[k]
            if this_res is not None:
                # Make sure the result is serializable
                this_res["match"] = None
        self.write(json.dumps(res))
