"""
Get information about data
"""
from typing import Union, List
import json

from lires.core.dataClass import DataList, DataTags, DataPoint, DataPointSummary
from ._base import *

class DataListHandler(RequestHandlerBase):
    """
    Query information of the entire database
    """
    @keyRequired
    async def get(self):
        """
        Args:
            tags (str): tags should be "%" or split by "&&"
        """
        self.set_header("totalDataCount", str(len(self.db)))

        # may delete this
        tags = self.get_argument("tags")
        if tags == "":
            tags = []
        else:
            tags = tags.split("&&")

        await self.emitDataList(tags)
    
    @keyRequired
    async def post(self):
        """
        tags are list of strings
        """
        self.set_header("totalDataCount", str(len(self.db)))
        tags = json.loads(self.get_argument("tags"))
        await self.emitDataList(tags)
    
    async def emitDataList(self, tags):
        data_info = self.getDictDataListByTags(tags)
        self.write(json.dumps(data_info))
        return

    def getDictDataListByTags(self, tags: Union[list, DataTags], sort_by = DataList.SORT_TIMEADDED) -> List[DataPointSummary]:
        dl = self.db.getDataByTags(tags)
        dl.sortBy(sort_by)
        return [d.summary for d in dl]

class DataListStreamHandler(DataListHandler):

    async def emitDataList(self, tags):
        data_info = self.getDictDataListByTags(tags)

        # it's a bit tricky to stream json
        # we add a \N at the end of each json string
        async for d in self.wrapAsyncIter(data_info):
            # import time; time.sleep(0.0005)
            self.write(json.dumps(d))
            self.write("\\N")
            self.flush()

class DataInfoHandler(RequestHandlerBase):
    """
    Query information about a single file
    """
    @keyRequired
    async def get(self, uid:str):
        dp: DataPoint = self.db[uid]
        self.write(json.dumps(dp.summary))
        return