from ._base import *
from typing import TypedDict
from lires.core.dataSearcher import DataSearcher
import json


class BasicFilterT(TypedDict):
    tags: list[str]
    search_by: str 
    search_content: str

    top_k: int

class BasicFilterHandler(RequestHandlerBase):
    # Get data by a single tag and search filter

    @keyRequired
    async def post(self):
        # url encoded form
        self.set_header("Content-Type", "application/json")

        # Get the tag and search filter from form
        tags = json.loads(self.get_argument("tags"))
        search_by = self.get_argument("search_by")
        search_content = self.get_argument("search_content")
        top_k = int(self.get_argument("top_k"))

        await self.logger.debug(f"tags: {tags}, search_by: {search_by}, search_content: {search_content}, top_k: {top_k}")

        # Get the data
        if (not search_content) and (not tags):
            return self.write(json.dumps({
                'uids': await self.db.keys(),
                'scores': None
            }))

        if tags:
            cadidate_ids = await self.db.getIDByTags(tags)
            res = cadidate_ids
        else:
            cadidate_ids = None
            res = await self.db.keys()
        scores = None

        if not search_content:
            pass

        elif search_by == 'title':
            res = await self.db.conn.filter(strict=False, ignore_case=True, from_uids=cadidate_ids, title=search_content)
        
        elif search_by == 'year':
            q = None
            if search_content.isnumeric():
                q = int(search_content)
            else:
                for sep in ['-', 'to', ',']:
                    if sep in search_content:
                        q = tuple([int(x.strip()) for x in search_content.split(sep)])
                        if not len(q) == 2: q = q[0]
                        break
            if q is None:
                raise tornado.web.HTTPError(400, "Invalid search year value")
            res = await self.db.conn.filter(strict=False, ignore_case=True, from_uids=cadidate_ids, year=q)
        
        elif search_by == 'publication':
            res = await self.db.conn.filter(strict=False, ignore_case=True, from_uids=cadidate_ids, publication=search_content)
        
        elif search_by == 'note':
            res = await self.db.conn.filter(strict=False, ignore_case=True, from_uids=cadidate_ids, note=search_content)
        
        elif search_by == 'uuid':
            res = []
            for uid in await self.db.keys():
                if uid.startswith(search_content):
                    res.append(uid)
        
        elif search_by == 'feature':
            res_, scores_ = await searchByFeature(self.iconn, self.vec_db, search_content, top_k=top_k)
            if cadidate_ids is not None:
                candidate_set = set(cadidate_ids)    # convert to set may be faster?
                res = []
                scores = []
                for uid, score in zip(res_, scores_):
                    if uid in candidate_set:
                        res.append(uid)
                        scores.append(score)
            else:
                res = res_
                scores = scores_
        
        elif search_by == 'author':
            # TODO: Optimize this to unify the author name
            res = await self.db.conn.filter(strict=False, ignore_case=True, from_uids=cadidate_ids, authors=[search_content])
        
        else:
            raise tornado.web.HTTPError(400, "Invalid search_by value")
        
        await self.logger.debug(f"returning {len(res)} results.")
        self.write(json.dumps({
            'uids': res,
            'scores': scores
        }))
        return

async def searchByFeature(iconn, vec_db, feature, top_k=10):
    searcher = DataSearcher()
    result = await searcher.searchFeature(iconn, vec_db, feature, top_k)

    uids = []
    scores = []
    for uid, c in result.items():
        assert c is not None
        uids.append(uid)
        scores.append(c["score"])
    return uids, scores
    

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
