"""
Search database by certain criteria
"""

import re
import asyncio
from . import globalVar as G
from typing import Dict, Optional, TypedDict
from .dataClass import DataCore, DataBase, DataPoint
from .asynciolib import asyncioLoopRun
from .serverConn import ServerConn
from .textUtils import queryFeatureIndex
from tiny_vectordb import VectorDatabase

class _searchResult(TypedDict):
    score: Optional[float]  # sort by score, the higher the better match
    match: Optional[re.Match]

StringSearchT = Dict[str, Optional[_searchResult]]
class DataSearcher(DataCore):

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
    
    def run(self) -> StringSearchT:
        assert self._run_config is not None, "setRunConfig before calling run()"
        method = getattr(self, self._run_config["method"])
        return method(**self._run_config["kwargs"])
    
    def searchStringInfo(self, pattern: str, ignore_case:bool = True) -> StringSearchT:
        results: StringSearchT = {}
        for uid, dp in self.db.items():
            res = self._searchRegex(pattern, dp.stringInfo(), ignore_case)
            if not res is None:
                results[uid] = {"score": None, "match": res}
        return results
    
    def searchTitle(self, pattern: str, ignore_case:bool = True) -> StringSearchT:
        results: StringSearchT = {}
        for uid, dp in self.db.items():
            res = self._searchRegex(pattern, dp.title, ignore_case)
            if not res is None:
                results[uid] = {"score": None, "match": res}
        return results

    def searchAuthor(self, pattern: str, ignore_case:bool = True) -> StringSearchT:
        results: StringSearchT = {}
        for uid, dp in self.db.items():
            to_search = ", ".join(dp.authors)
            res = self._searchRegex(pattern, to_search, ignore_case)
            if not res is None:
                results[uid] = {"score": None, "match": res}
        return results

    def searchYear(self, pattern: str) -> StringSearchT:
        results: StringSearchT = {}
        for uid, dp in self.db.items():
            year = str(dp.year); pattern = str(pattern)
            if year.startswith(pattern):
                results[uid] = None
        return results

    def searchPublication(self, pattern: str, ignore_case:bool = True) -> StringSearchT:
        results: StringSearchT = {}
        for uid, dp in self.db.items():
            res = None
            to_search = dp.publication
            if not to_search is None:
                res = self._searchRegex(pattern, to_search, ignore_case)
            if not res is None:
                results[uid] = {"score": None, "match": res}
        return results
    
    def searchComment(self, pattern: str, ignore_case: bool = True) -> StringSearchT:

        async def _searchComment(db: DataBase):
            results: StringSearchT = {}
            async_tasks = []
            uids = []
            for uid, dp in self.db.items():
                async_tasks.append(_searchCommentSingle(dp, pattern, ignore_case))
                uids.append(uid)
            all_res = await asyncio.gather(*async_tasks)
            for uid, res in zip(uids, all_res): # type: ignore
                if res is not None:
                    results[uid] = {"score": None, "match": res}
            return results
        
        async def _searchCommentSingle(dp: DataPoint, pattern_, ignore_case_):
            comments = dp.fm.readComments()
            res = self._searchRegex(pattern, comments, ignore_case)
            return res

        if self.db.offline:
            return asyncioLoopRun(_searchComment(self.db))
        
        else:
            conn = ServerConn()
            res = conn.search("searchComment", kwargs = {
                "pattern": pattern,
                "ignore_case": ignore_case,
            })
            if res is None:
                return {}
            else:
                return res
    
    def searchFeature(self, pattern: str, n_return = 999, vec_db:Optional[ VectorDatabase ] = None) -> StringSearchT:
        if self.db.offline:
            if pattern.strip() == "":
                return {uid: None for uid in self.db.keys()}
            if vec_db:
                search_res = queryFeatureIndex(pattern, n_return=n_return, vector_collection=vec_db.getCollection("doc_feature"))
            else:
                search_res = queryFeatureIndex(pattern, n_return=n_return)

            if search_res is None:
                self.logger.error("Error connecting to iserver, return empty result")
                return {uid: None for uid in self.db.keys()}

            return {uid: {"score": score, "match": None} for uid, score in zip(search_res["uids"], search_res["scores"])}
        else:
            conn = ServerConn()
            res = conn.search("searchFeature", kwargs = {
                "pattern": pattern,
                "n_return": n_return,
            })
            if res is None:
                return {}
            else:
                return res
    
    def _searchRegex(self, pattern: str, aim: str, ignore_case: bool):
        if ignore_case:
            res = re.search(pattern, aim, re.IGNORECASE)
        else:
            res = re.search(pattern, aim)
        return res