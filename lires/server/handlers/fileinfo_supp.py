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
        dp = self.db[uid]
        self.logger.debug("Get notes of: {}".format(dp))
        self.write(dp.fm.readComments())

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
        user_info = self.user_info
        note = self.get_argument("content")

        dp = self.db[uid]
        if not user_info["is_admin"]:
            tags = dp.tags
            self.checkTagPermission(tags, user_info["mandatory_tags"])
        
        self.logger.info("Update notes of: {}".format(dp))

        dp.fm.writeComments(note)
        self.broadcastEventMessage({
            'type': 'update_entry',
            'uuid': uid,
            'datapoint_summary': dp.summary
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
        dp = self.db[uid]
        self.logger.debug("Get abstract of: {}".format(dp))
        self.write(dp.fm.readAbstract())
    

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
        user_info = self.user_info
        abstract = self.get_argument("content")

        dp = self.db[uid]
        if not user_info["is_admin"]:
            tags = dp.tags
            self.checkTagPermission(tags, user_info["mandatory_tags"])
        
        self.logger.info("Update abstract of: {}".format(dp))

        dp.fm.writeAbstract(abstract)
        self.broadcastEventMessage({
            'type': 'update_entry',
            'uuid': uid,
            'datapoint_summary': dp.summary
        })
        self.write("OK")