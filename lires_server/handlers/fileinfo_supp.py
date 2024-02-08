"""
Get and modify notes of a datapoint
"""
from ._base import *

class NoteGetHandler(RequestHandlerBase):
    """
    Get notes of a datapoint
    """
    async def get(self, uid:str):
        """
        Args:
            uid (str): uuid of the datapoint
        """
        dp = await self.db.get(uid)
        await self.logger.debug("Get notes of: {}".format(dp))
        self.write(await dp.fm.readComments())

class NoteUpdateHandler(RequestHandlerBase):
    """
    Update notes of a datapoint
    """
    @keyRequired
    async def post(self, uid:str):
        """
        Args:
            uid (str): uuid of the datapoint
        """
        user_info = await self.userInfo()
        note = self.get_argument("content")

        dp = await self.db.get(uid)
        if not user_info["is_admin"]:
            tags = dp.tags
            await self.checkTagPermission(tags, user_info["mandatory_tags"])
        
        await self.logger.info("Update notes of: {}".format(dp))

        await dp.fm.writeComments(note)
        dp = await self.db.get(uid)
        await self.broadcastEventMessage({
            'type': 'update_entry',
            'uuid': uid,
            'datapoint_summary': dp.summary.json()
        })
        self.write("OK")

class AbstractGetHandler(RequestHandlerBase):
    """
    Get abstract of a datapoint
    """
    async def get(self, uid:str):
        """
        Args:
            uid (str): uuid of the datapoint
        """
        dp = await self.db.get(uid)
        await self.logger.debug("Get abstract of: {}".format(dp))
        self.write(await dp.fm.readAbstract())
    

class AbstractUpdateHandler(RequestHandlerBase):
    """
    Update abstract of a datapoint
    """
    @keyRequired
    async def post(self, uid:str):
        """
        Args:
            uid (str): uuid of the datapoint
        """
        user_info = await self.userInfo()
        abstract = self.get_argument("content")

        dp = await self.db.get(uid)
        if not user_info["is_admin"]:
            tags = dp.tags
            await self.checkTagPermission(tags, user_info["mandatory_tags"])
        
        await self.logger.info("Update abstract of: {}".format(dp))

        await dp.fm.writeAbstract(abstract)
        await self.broadcastEventMessage({
            'type': 'update_entry',
            'uuid': uid,
            'datapoint_summary': dp.summary.json()
        })
        self.write("OK")