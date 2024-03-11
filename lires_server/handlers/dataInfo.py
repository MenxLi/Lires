"""
Get information about data
"""
from typing import Union, List
import json

from lires.core.dataClass import DataPoint, sortDataList, SortType
from lires.core.dataTags import DataTags
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
        self.set_header("totalDataCount", str(await self.db.count()))

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
        self.set_header("totalDataCount", str(await self.db.count()))
        tags = json.loads(self.get_argument("tags"))
        await self.emitDataList(tags)
    
    async def emitDataList(self, tags):
        data_info = await self.getDictDataListByTags(tags)
        self.write(json.dumps(data_info))
        return

    async def getDictDataListByTags(self, tags: Union[list, DataTags], sort_by:SortType = "time_added") -> List[dict]:
        dl = await self.db.getDataByTags(tags)
        dl = sortDataList(dl, sort_by = sort_by)
        return [d.summary.json() for d in dl]

class DataListStreamHandler(DataListHandler):

    async def emitDataList(self, tags):
        data_info = await self.getDictDataListByTags(tags)

        # it's a bit tricky to stream json
        # we add a \N at the end of each json string
        async for d in self.wrapAsyncIter(data_info):
            # import time; time.sleep(0.0005)
            self.write(json.dumps(d))
            self.write("\\N")
            self.flush()

class DatabaseKeysHandler(RequestHandlerBase):
    """ Get summary of the database """
    @keyRequired
    async def get(self):
        self.write(json.dumps(await self.db.keys()))
        return
class DatabaseTagsHandler(RequestHandlerBase):
    """ Get summary of the database """
    @keyRequired
    async def get(self):
        self.write(json.dumps(
            (await self.db.tags()).toOrderedList()
            ))
        return

class DataInfoHandler(RequestHandlerBase):
    """
    Query information about a single file
    """
    @keyRequired
    async def get(self, uid:str):
        try:
            dp: DataPoint = await self.db.get(uid)
        except self.Error.LiresEntryNotFoundError:
            await self.logger.error("Data point not found (uid: {})".format(uid))
            self.set_status(404)
            self.write("Data point not found")
            return
        self.write(json.dumps(dp.summary.json()))
        return

class DataInfoListHandler(RequestHandlerBase):
    """
    Query information about a single file
    """
    @keyRequired
    async def post(self):
        uids: list[str] = json.loads(self.get_argument("uids"))
        try:
            all_dp = await self.db.gets(uids)
        except self.Error.LiresEntryNotFoundError:
            await self.logger.error("Some data points are not found: {}".format(
                non_exist_uids := await self.db.conn.checkNoneExist(uids)
            ))
            self.set_status(404)
            self.write("Some data points are not found: {}".format(non_exist_uids))
            return

        await self.logger.debug("emit data info list of size: {}".format(len(all_dp)))
        self.write(json.dumps([dp.summary.json() for dp in all_dp]))
        return