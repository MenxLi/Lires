from ._base import *
from typing import TypedDict
from lires.core.vecutils import queryFeatureIndex
import json


class BasicFilterT(TypedDict):
    tags: list[str]
    search_by: str 
    search_content: str

    top_k: int

class BasicFilterHandler(RequestHandlerBase):
    # Get data by a single tag and search filter

    @authenticate()
    async def post(self):
        # url encoded form
        self.set_header("Content-Type", "application/json")
        db = await self.db()

        # Get the tag and search filter from form
        tags = json.loads(self.get_argument("tags"))
        search_by = self.get_argument("search_by")
        search_content = self.get_argument("search_content")
        top_k = int(self.get_argument("top_k"))

        await self.logger.debug(f"tags: {tags}, search_by: {search_by}, search_content: {search_content}, top_k: {top_k}")

        # Get the data
        if (not search_content) and (not tags):
            return self.write(json.dumps({
                'uids': await db.keys(),
                'scores': None
            }))

        if tags:
            cadidate_ids = await db.getIDByTags(tags)
            res = cadidate_ids
        else:
            cadidate_ids = None
            res = await db.keys()
        scores = None

        if not search_content:
            pass

        elif search_by == 'title':
            res = await db.conn.filter(strict=False, ignore_case=True, from_uids=cadidate_ids, title=search_content)
        
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
            res = await db.conn.filter(strict=False, ignore_case=True, from_uids=cadidate_ids, year=q)
        
        elif search_by == 'publication':
            res = await db.conn.filter(strict=False, ignore_case=True, from_uids=cadidate_ids, publication=search_content)
        
        elif search_by == 'note':
            res = await db.conn.filter(strict=False, ignore_case=True, from_uids=cadidate_ids, note=search_content)
        
        elif search_by == 'uuid':
            res = []
            for uid in await db.keys():
                if uid.startswith(search_content):
                    res.append(uid)
        
        elif search_by == 'feature':
            q_res = await queryFeatureIndex(
                iconn=self.iconn,
                query=search_content,
                n_return=top_k,
                vector_collection= await (await self.vec_db()).getCollection("doc_feature")
            )
            res_ = [x["entry"]["uid"] for x in q_res]
            scores_ = [x["score"] for x in q_res]
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
            res = await db.conn.filter(strict=False, ignore_case=True, from_uids=cadidate_ids, authors=[search_content])
        
        else:
            raise tornado.web.HTTPError(400, "Invalid search_by value")
        
        await self.logger.debug(f"returning {len(res)} results.")

        # Sort the result if no scores are provided
        if scores is None:
            res = await db.conn.sortKeys(res)

        self.write(json.dumps({
            'uids': res,
            'scores': scores
        }))
        return
