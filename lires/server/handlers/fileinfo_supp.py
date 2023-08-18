"""
Get and modify notes of a datapoint
"""
from ._base import *

class NoteGetHandler(tornado.web.RequestHandler, RequestHandlerMixin):
    """
    Get notes of a datapoint
    """
    def get(self, uid:str):
        """
        Args:
            uid (str): uuid of the datapoint
        """
        self.setDefaultHeader()
        dp = self.db[uid]
        self.logger.debug("Get notes of: {}".format(dp))
        self.write(dp.fm.readComments())

class NoteUpdateHandler(tornado.web.RequestHandler, RequestHandlerMixin):
    """
    Update notes of a datapoint
    """
    def post(self, uid:str):
        """
        Args:
            uid (str): uuid of the datapoint
        """
        permission = self.checkKey()
        note = self.get_argument("content")
        self.setDefaultHeader()

        dp = self.db[uid]
        if not permission["is_admin"]:
            tags = dp.tags
            self.checkTagPermission(tags, permission["mandatory_tags"])
        
        self.logger.info("Update notes of: {}".format(dp))

        dp.fm.writeComments(note)
        self.write("OK")

class AbstractGetHandler(tornado.web.RequestHandler, RequestHandlerMixin):
    """
    Get abstract of a datapoint
    """
    def get(self, uid:str):
        """
        Args:
            uid (str): uuid of the datapoint
        """
        self.setDefaultHeader()
        dp = self.db[uid]
        self.logger.debug("Get abstract of: {}".format(dp))
        self.write(dp.fm.readAbstract())
    

class AbstractUpdateHandler(tornado.web.RequestHandler, RequestHandlerMixin):
    """
    Update abstract of a datapoint
    """
    def post(self, uid:str):
        """
        Args:
            uid (str): uuid of the datapoint
        """
        permission = self.checkKey()
        abstract = self.get_argument("content")
        self.setDefaultHeader()

        dp = self.db[uid]
        if not permission["is_admin"]:
            tags = dp.tags
            self.checkTagPermission(tags, permission["mandatory_tags"])
        
        self.logger.info("Update abstract of: {}".format(dp))

        dp.fm.writeAbstract(abstract)
        self.write("OK")