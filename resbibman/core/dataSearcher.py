"""
Search database by certain criteria
"""

import re, requests, json
import asyncio
from typing import List, Dict, Optional
from . import globalVar as G
from .dataClass import DataCore, DataBase, DataPoint
from .encryptClient import generateHexHash
from ..confReader import getConfV, getServerURL
from ..perf.asynciolib import asyncioLoopRun

# a dictionary of uuid and matchs
StringSearchT = Dict[str, Optional[re.Match]]
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
                results[uid] = res
        return results
    
    def searchTitle(self, pattern: str, ignore_case:bool = True) -> StringSearchT:
        results: StringSearchT = {}
        for uid, dp in self.db.items():
            res = self._searchRegex(pattern, dp.title, ignore_case)
            if not res is None:
                results[uid] = res
        return results

    def searchAuthor(self, pattern: str, ignore_case:bool = True) -> StringSearchT:
        results: StringSearchT = {}
        for uid, dp in self.db.items():
            to_search = ", ".join(dp.authors)
            res = self._searchRegex(pattern, to_search, ignore_case)
            if not res is None:
                results[uid] = res
        return results

    def searchYear(self, pattern: str) -> StringSearchT:
        results: StringSearchT = {}
        for uid, dp in self.db.items():
            year = str(dp.year); pattern = str(pattern)
            if year.startswith(pattern):
                results[uid] = None
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
            for uid, res in zip(uids, all_res):
                if res is not None:
                    results[uid] = res
            return results
        
        async def _searchCommentSingle(dp: DataPoint, pattern_, ignore_case_):
            comments = dp.fm.readComments()
            res = self._searchRegex(pattern, comments, ignore_case)
            return res

        if self.db.offline:
            return asyncioLoopRun(_searchComment(self.db))
        
        else:
            post_args = {
                "key": self.POST_HEX_KEY,
                "method": "searchComment",
                "kwargs": json.dumps({
                    "pattern": pattern,
                    "ignore_case": ignore_case
                })
            }
            res = requests.post(self.POST_URL, params = post_args)
            if not self._checkRes(res):
                self.logger.error("Error connection")
                return {}
            else:
                return json.loads(res.text)
    
    def _searchRegex(self, pattern: str, aim: str, ignore_case: bool):
        if ignore_case:
            res = re.search(pattern, aim, re.IGNORECASE)
        else:
            res = re.search(pattern, aim)
        return res

    @property
    def POST_HEX_KEY(self) -> str:
        return generateHexHash(getConfV("access_key"))
    
    @property
    def POST_URL(self) -> str:
        return getServerURL() + "/search"

    def _checkRes(self, res: requests.Response) -> bool:
        """
        Check if response is valid
        """
        status_code = res.status_code
        if status_code != 200:
            self.logger.debug("Get response {}".format(res.status_code))
        if status_code == 401:
            self.logger.warning("Unauthorized access")
        G.last_status_code = res.status_code
        return res.ok