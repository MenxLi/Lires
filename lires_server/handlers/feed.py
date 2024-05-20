
from ._base import *
import json, asyncio
from lires.api.feed import FServerConn

class FeedHandler(RequestHandlerBase):

    __featurize_cache = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fconn = FServerConn()
    
    @authenticate()
    async def post(self):
        self.set_header("Content-Type", "application/json")

        # Get latest articles, datapoint summary json with abstract
        d_info_w_abstract = await self.fconn.query(
            max_results=int(self.get_argument("max_results", "10")),
            category=self.get_argument("category"),
            time_after=float(self.get_argument("time_after", "-1")),
            time_before=float(self.get_argument("time_before", "-1"))
        )

        # Get more content for each article, add feature and other publications
        db = await self.db()
        async def finishOne(d_info):
            async def featurizeFn():
                uid = d_info['uuid']

                # check if cache is too large
                if len(FeedHandler.__featurize_cache) > 5000:
                    await self.logger.debug("Clearing featurize cache...")
                    FeedHandler.__featurize_cache.clear()

                # if already featurized, return
                if uid in FeedHandler.__featurize_cache:
                    return FeedHandler.__featurize_cache[d_info['uuid']]

                _feature_source = d_info["abstract"] if d_info["abstract"] in d_info else d_info["title"]
                try:
                    feat = await self.iconn.featurize(_feature_source)
                    FeedHandler.__featurize_cache[uid] = feat
                except self.Error.LiresConnectionError as e:
                    await self.logger.error(f"Error featurizing {uid}: {e}")
                    feat = None
                return feat

            featurize_task = asyncio.Task(featurizeFn())
            other_pubs = await asyncio.gather(*[
                db.conn.filter(authors=[author])
                for author in d_info["authors"]
                ])
            # add extra keys
            d_info['authors_other_publications'] = other_pubs
            d_info['feature'] = await featurize_task
            return d_info

        d_info_all = await asyncio.gather(*[finishOne(d_info) for d_info in d_info_w_abstract])
        self.write(json.dumps(d_info_all))

class FeedCategoriesHandler(RequestHandlerBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fconn = FServerConn()
    
    @authenticate()
    async def get(self):
        self.set_header("Content-Type", "application/json")
        categories = await self.fconn.categories()
        self.write(json.dumps(categories))