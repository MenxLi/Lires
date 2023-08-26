"""
Get information about data
"""
from typing import Union, List
import json
import tornado.web

from lires.core.dataClass import DataList, DataTags, DataPoint, DataPointSummary
from ._base import *

class DataListHandler(tornado.web.RequestHandler, RequestHandlerMixin):
    """
    Query information of the entire database
    """
    @keyRequired
    async def get(self):
        """
        Args:
            tags (str): tags should be "%" or split by "&&"
        """
        self.setDefaultHeader()
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
        tags = json.loads(self.get_argument("tags"))
        await self.emitDataList(tags)
    
    async def emitDataList(self, tags):
        data_info = self.getDictDataListByTags(tags)
        if data_info is not None:
            json_data = {
                "data":data_info
            }
            self.write(json.dumps(json_data))
        else:
            self.write("Something wrong with the server.")
        return

    def getDictDataListByTags(self, tags: Union[list, DataTags], sort_by = DataList.SORT_TIMEADDED) -> List[DataPointSummary]:
        dl = self.db.getDataByTags(tags)
        dl.sortBy(sort_by)
        return [d.summary for d in dl]

class DataInfoHandler(tornado.web.RequestHandler, RequestHandlerMixin):
    """
    Query information about a single file
    """
    @keyRequired
    async def get(self, uid:str):
        self.setDefaultHeader()
        dp: DataPoint = self.db[uid]
        self.write(json.dumps(dp.summary))
        return