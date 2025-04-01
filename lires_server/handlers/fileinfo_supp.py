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
        self.set_header("Content-Type", "text/plain")
        db = await self.db()
        dp = await db.get(uid)
        await self.logger.debug("Get notes of: {}".format(dp))
        self.write(await dp.fm.get_comments())

class NoteUpdateHandler(RequestHandlerBase):
    """
    Update notes of a datapoint
    """
    @authenticate()
    async def post(self, uid:str):
        """
        Args:
            uid (str): uuid of the datapoint
        """
        self.set_header("Content-Type", "text/plain")
        user_info = await self.user_info()
        db = await self.db()
        note = self.get_argument("content")

        dp = await db.get(uid)
        if not user_info["is_admin"]:
            tags = dp.tags
            await self.check_tag_permission(tags, user_info["mandatory_tags"])
        
        await self.logger.info("Update notes of: {}".format(dp))

        await dp.fm.set_comments(note)
        dp = await db.get(uid)
        await self.broadcast_event({
            'type': 'update_note',
            'uuid': uid,
            'datapoint_summary': dp.summary.json(),
            'note': note
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
        self.set_header("Content-Type", "text/plain")
        db = await self.db()
        dp = await db.get(uid)
        await self.logger.debug("Get abstract of: {}".format(dp))
        self.write(await dp.fm.get_abstract())
    

class AbstractUpdateHandler(RequestHandlerBase):
    """
    Update abstract of a datapoint
    """
    @authenticate()
    async def post(self, uid:str):
        """
        Args:
            uid (str): uuid of the datapoint
        """
        self.set_header("Content-Type", "text/plain")
        user_info = await self.user_info()
        abstract = self.get_argument("content")

        db = await self.db()
        dp = await db.get(uid)
        if not user_info["is_admin"]:
            tags = dp.tags
            await self.check_tag_permission(tags, user_info["mandatory_tags"])
        
        await self.logger.info("Update abstract of: {}".format(dp))

        await dp.fm.set_abstract(abstract)
        await self.broadcast_event({
            'type': 'update_entry',
            'uuid': uid,
            'datapoint_summary': dp.summary.json()
        })
        await self.ensure_feature_update(dp)
        self.write("OK")