"""
Search database by certain criteria
"""

import re
from typing import List, Dict, Optional
from .dataClass import DataCore, DataBase, DataPoint

# a dictionary of uuid and matchs
StringSearchT = Dict[str, re.Match]
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
    
    def _searchRegex(self, pattern: str, aim: str, ignore_case: bool):
        if ignore_case:
            res = re.search(pattern, aim, re.IGNORECASE)
        else:
            res = re.search(pattern, aim)
        return res
