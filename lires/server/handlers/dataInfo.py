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
    def get(self, uid:str):
        """
         - uuid_cmd (str): <uuid>?<cmd> | <uuid>
        """
        self.setDefaultHeader()
        
        try:
            cmd = self.get_argument("type")
        except:
            cmd = None
        dp: DataPoint = self.db[uid]
        if cmd is None:
            d_info = self.db[uid].summary
            self.write(json.dumps(d_info))
            return
        elif cmd == "stringInfo":
            detail = dp.stringInfo()
            self.write(detail)
            return 
        elif cmd == "abstract":
            raise DeprecationWarning("get abstract through this api is deprecated")
            abstract = dp.fm.readAbstract()
            self.write(abstract)
        else:
            # not implemented
            raise tornado.web.HTTPError(404)
