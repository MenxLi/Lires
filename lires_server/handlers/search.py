from ._base import *
from typing import TypedDict, Optional
import functools
from lires.core.vecutils import query_feature_index
import json


class BasicFilterT(TypedDict):
    tags: list[str]
    search_by: str 
    search_content: str
    sort_by: str

    top_k: int

class BasicFilterHandler(RequestHandlerBase):
    # Get data by a single tag and search filter

    @authenticate()
    async def post(self):
        self.set_header("Content-Type", "application/json")
        db = await self.db()

        # Get the tag and search filter from form
        tags = json.loads(self.get_argument("tags"))
        search_by = self.get_argument("search_by")
        search_content = self.get_argument("search_content")
        top_k = int(self.get_argument("top_k"))
        sort_by: Optional[str] = self.get_argument("sort_by", "time_import")

        await self.logger.debug(f"filter: tags: {tags}, search_by: {search_by}, search_content: {search_content}, top_k: {top_k}, sort_by: {sort_by}")

        DEFAULT_SEC_SORT = 'time_import'

        # Get the data
        if (not search_content) and (not tags):
            uids = await db.keys()
            if sort_by:
                uids = await db.conn.sort_keys(uids, sort_by=sort_by, sec_sort_by=DEFAULT_SEC_SORT)
            return self.write(json.dumps({
                'uids': uids,
                'scores': None
            }))

        if tags:
            cadidate_ids = await db.ids_from_tags(tags)
            res = cadidate_ids
        else:
            cadidate_ids = None
            res = await db.keys()
        scores = None

        if not search_content:
            pass

        filter_fn = functools.partial(db.conn.filter, 
            strict=False, 
            ignore_case=True, 
            from_uids=cadidate_ids
        )
        match search_by:
            case 'title':
                res = await filter_fn(title=search_content)

            case 'publication':
                res = await filter_fn(publication=search_content)
            
            case 'note':
                res = await filter_fn(note=search_content)
            
            case 'author':
                res = await filter_fn(authors=[search_content])
            
            case 'year':
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
                res = await filter_fn(year=q)
            
            case 'uuid':
                res = []
                for uid in await db.keys():
                    if uid.startswith(search_content):
                        res.append(uid)
            
            case 'feature':
                q_res = await query_feature_index(
                    iconn=self.iconn,
                    query=search_content,
                    n_return=top_k,
                    vector_collection= await (await self.vec_db()).get_collection("doc_feature")
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
            
            case _:
                raise tornado.web.HTTPError(400, "Invalid search_by value")
        
        await self.logger.debug(f"returning {len(res)} results.")

        # Sort the result if no scores are provided
        if scores is None and sort_by:
            res = await db.conn.sort_keys(res, sort_by=sort_by, sec_sort_by=DEFAULT_SEC_SORT)

        self.write(json.dumps({
            'uids': res,
            'scores': scores
        }))
        return
