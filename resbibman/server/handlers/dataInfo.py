"""
Get information about data
"""
from typing import Union, List
import json
import tornado.web

from resbibman.core.dataClass import DataList, DataTags, DataPoint, DataPointSummary
from ._base import RequestHandlerBase

class DataListHandler(tornado.web.RequestHandler, RequestHandlerBase):
    def get(self):
        """
        Args:
            tags (str): tags should be "%" or split by "&&"
        """

        print("receiving file list request")
        # self.checkKey()

        self.setDefaultHeader()
        tags = self.get_argument("tags")
        if tags == "":
            tags = []
        else:
            tags = tags.split("&&")
        self.emitDataList(tags)
    
    def post(self):
        """
        tags are list of strings
        """
        print("posting file list request")
        tags = json.loads(self.get_argument("tags"))
        self.emitDataList(tags)
    
    def emitDataList(self, tags):
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
        return [d.info for d in dl]

class DataInfoHandler(tornado.web.RequestHandler, RequestHandlerBase):
    """
    Query information about a single file
    """
    def get(self, uid:str):
        """
         - uuid_cmd (str): <uuid>?<cmd> | <uuid>
        """
        self.setDefaultHeader()
        
        try:
            cmd = self.get_argument("cmd")
        except:
            cmd = None
        dp: DataPoint = self.db[uid]
        if cmd is None:
            d_info = self.db[uid].info
            self.write(json.dumps(d_info))
            return
        elif cmd == "stringInfo":
            detail = dp.stringInfo()
            self.write(detail)
            return 
        else:
            # not implemented
            raise tornado.web.HTTPError(404)
