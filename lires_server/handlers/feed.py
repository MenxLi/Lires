
from ._base import *
import json, asyncio
from lires.api.feed import FServerConn

class FeedHandler(RequestHandlerBase):

    __featurize_cache = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fconn = FServerConn()
    
    @keyRequired
    async def post(self):
        self.set_header("Content-Type", "application/json")

        # Get latest articles, datapoint summary json with abstract
        d_info_w_abstract = await self.fconn.getLatest(
            max_results=int(self.get_argument("max_results", "10")),
            category=self.get_argument("category")
        )

        # Get more content for each article, add feature and other publications
        db = await self.db()
        async def finishOne(d_info):
            _feature_source = d_info["abstract"] if d_info["abstract"] in d_info else d_info["title"]
            feature_task = asyncio.Task(self.iconn.featurize(_feature_source))
            other_pubs = await asyncio.gather(*[
                db.conn.filter(authors=[author])
                for author in d_info["authors"]
                ])
            # add extra keys
            d_info['authors_other_publications'] = other_pubs
            d_info['feature'] = await feature_task
            return d_info
        d_info_all = await asyncio.gather(*[finishOne(d_info) for d_info in d_info_w_abstract])

        self.write(json.dumps(d_info_all))
