"""
Get information about data
"""
from typing import Union, List
import json

from lires.core.dataClass import DataPoint, sortDataList, SortType
from lires.core.dataTags import DataTags
from ._base import *

class DataInfoHandler(RequestHandlerBase):
    """
    Query information about a single file
    """
    @keyRequired
    async def get(self, uid:str):
        db = await self.db()
        try:
            dp: DataPoint = await db.get(uid)
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
        db = await self.db()
        try:
            all_dp = await db.gets(uids)
        except self.Error.LiresEntryNotFoundError:
            await self.logger.error("Some data points are not found: {}".format(
                non_exist_uids := await db.conn.checkNoneExist(uids)
            ))
            self.set_status(404)
            self.write("Some data points are not found: {}".format(non_exist_uids))
            return

        await self.logger.debug("emit data info list of size: {}".format(len(all_dp)))
        self.write(json.dumps([dp.summary.json() for dp in all_dp]))
        return