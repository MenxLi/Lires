"""
Get information about data
"""
import json
from lires.core.dataClass import DataPoint
from lires.config import getConf
from ._base import *

class DataInfoHandler(RequestHandlerBase):
    """ Query information about a single file """
    @authenticate(enabled = not getConf()['allow_public_query'])
    async def get(self, uid:str):
        self.set_header("Content-Type", "application/json")
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
    """ Query information about a list of files """
    @authenticate(enabled = not getConf()['allow_public_query'])
    async def post(self):
        self.set_header("Content-Type", "application/json")
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