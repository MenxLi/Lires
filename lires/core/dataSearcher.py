"""
Search database by certain criteria
"""

import re
from typing import Dict, Optional, TypedDict, Literal
from lires.api import IServerConn
from .dataClass import DataCore, DataBase, DataPoint
from .dataTags import DataTagT
from .vector import queryFeatureIndex
from tiny_vectordb import VectorDatabase

class _searchResult(TypedDict):
    score: Optional[float]  # sort by score, the higher the better match
    match: Optional[re.Match]

StringSearchT = Dict[str, Optional[_searchResult]]
class DataSearcher(DataCore):
    # TODO: remove this class, and move the methods to the database class

    def __init__(self, db: Optional[DataBase] = None) -> None:
        super().__init__()
        if db:
            self.setDatabase(db)
        self._run_config = None

    def setDatabase(self, database: DataBase):
        self.db = database
    
    def setRunConfig(self, method: str, kwargs: dict):
        self._run_config = {
            "method": method,
            "kwargs": kwargs
        }
    
    async def run(self) -> StringSearchT:
        assert self._run_config is not None, "setRunConfig before calling run()"
        method = getattr(self, self._run_config["method"])
        return await method(**self._run_config["kwargs"])
    
    async def searchStringInfo(self, pattern: str, ignore_case:bool = True) -> StringSearchT:
        results: StringSearchT = {}
        for dp in await self.db.getAll():
            uid = dp.uuid
            res = self._searchRegex(pattern, await dp.stringInfo(), ignore_case)
            if not res is None:
                results[uid] = {"score": None, "match": res}
        return results
    
    async def searchTitle(self, pattern: str, ignore_case:bool = True) -> StringSearchT:
        results: StringSearchT = {}
        for dp in await self.db.getAll():
            uid = dp.uuid
            res = self._searchRegex(pattern, dp.title, ignore_case)
            if not res is None:
                results[uid] = {"score": None, "match": res}
        return results

    async def searchAuthor(self, pattern: str, ignore_case:bool = True) -> StringSearchT:
        results: StringSearchT = {}
        for dp in await self.db.getAll():
            uid = dp.uuid
            to_search = ", ".join(dp.authors)
            res = self._searchRegex(pattern, to_search, ignore_case)
            if not res is None:
                results[uid] = {"score": None, "match": res}
        return results

    async def searchYear(self, pattern: str) -> StringSearchT:
        results: StringSearchT = {}
        for dp in await self.db.getAll():
            uid = dp.uuid
            year = str(dp.year); pattern = str(pattern)
            if year.startswith(pattern):
                results[uid] = None
        return results

    async def searchPublication(self, pattern: str, ignore_case:bool = True) -> StringSearchT:
        results: StringSearchT = {}
        for dp in await self.db.getAll():
            uid = dp.uuid
            res = None
            to_search = dp.publication
            if not to_search is None:
                res = self._searchRegex(pattern, to_search, ignore_case)
            if not res is None:
                results[uid] = {"score": None, "match": res}
        return results
    
    async def searchNote(self, pattern: str, ignore_case: bool = True) -> StringSearchT:
        # import asyncio
        # results: StringSearchT = {}
        # uids = []
        # all_res = []

        # all_dps = await self.db.getAll()
        # all_comments = await asyncio.gather(*[dp.fm.readComments() for dp in all_dps])
        # for dp, comments in zip(all_dps, all_comments):
        #     if not comments:
        #         continue
        #     uid = dp.uuid
        #     res = self._searchRegex(pattern, comments, ignore_case)
        #     uids.append(uid)
        #     all_res.append(res)
        # for uid, res in zip(uids, all_res):
        #     if res is not None:
        #         results[uid] = {"score": None, "match": res}
        # return results
        uids = await self.db.conn.filter(
            strict=False, 
            ignore_case=ignore_case,
            note=pattern
        )
        return {uid: None for uid in uids}
    
    async def searchFeature(self, iconn: IServerConn, vec_db: VectorDatabase, pattern: str, n_return = 999, ) -> StringSearchT:
        if pattern.strip() == "":
            return {uid: None for uid in await self.db.keys()}
        search_res = await queryFeatureIndex(
            iconn = iconn, 
            query = pattern, 
            n_return=n_return, 
            vector_collection=vec_db.getCollection("doc_feature")
            )

        if search_res is None:
            await self.logger.error("Error connecting to ai server, return empty result")
            return {uid: None for uid in await self.db.keys()}

        return {uid: {"score": score, "match": None} for uid, score in zip(search_res["uids"], search_res["scores"])}
    
    def _searchRegex(self, pattern: str, aim: str, ignore_case: bool):
        res = re.search(pattern, aim, re.IGNORECASE if ignore_case else 0)
        return res


SortType = Literal["DEFAULT", "year", "time_added", "time_modified"]
SearchType = Literal["general", "title", "author", "year", "publication", "Note", "feature"]
_ReleventContextT = TypedDict("_ReleventContextT", {
    "text": str,
    "index": list[tuple[int, int]]
})
class DataFilterResT(TypedDict):
    datapoint: DataPoint
    score: Optional[float]
    relevent_context: list[_ReleventContextT]
class FilterConditionT(TypedDict):
    search_by: SearchType
    search_pattern: str
    tags: DataTagT
def filterData(
        db: DataBase,
        include_conditions: list[FilterConditionT] = [],
        exclude_conditions: list[FilterConditionT] = [],
        sort_by: SortType = "DEFAULT",
    ) -> list[DataFilterResT]:
    """
    A unified way to get data from the database
    """
    # TODO: implement later...
    ...