
"""
Data management / manipulation handlers
This are handlers to (partially) replace the file handlers in resbibman/server/handlers/file.py
Provides handers for adding, deleting, and modifying files/tags
"""

from ._base import *
import json
from resbibman.core.bibReader import checkBibtexValidity
from resbibman.core.fileTools import addDocument
from resbibman.core.dataClass import DataTags

import pprint
class DataDeleteHandler(RequestHandlerBase, tornado.web.RequestHandler):
    def post(self):
        if not self.checkKey():
            raise tornado.web.HTTPError(403)
        self.setDefaultHeader()
        uuid = self.get_argument("uuid")
        if self.db.delete(uuid):
            self.logger.info(f"Deleted {uuid}")
        self.write("OK")
        return

class DataUpdateHandler(RequestHandlerBase, tornado.web.RequestHandler):
    def post(self):
        """
        Update or create a data entry
        arguments:
            uuid: uuid of the data entry (None for new entry)
            tags: list[str], bibtex: str, url: str
        """
        __info = [] # for logging

        self.setDefaultHeader()
        permission = self.checkKey()

        uuid = json.loads(self.get_argument("uuid"))
        assert uuid is None or isinstance(uuid, str)

        tags = json.loads(self.get_argument("tags"))
        url = self.get_argument("url")
        bibtex = self.get_argument("bibtex")
        if not checkBibtexValidity(bibtex):
            raise tornado.web.HTTPError(400)
        
        if not permission["is_admin"]:
            if uuid is None:
                # if the uuid is not provided, check tag validity using new tags
                self.checkTagPermission(tags, permission["mandatory_tags"])
            else:
                # if the uuid is provided, check tag validity using old tags
                old_tags = self.db[uuid].tags
                self.checkTagPermission(old_tags, permission["mandatory_tags"])
        
        if uuid is None:
            uuid = addDocument(self.db.conn, bibtex, check_duplicate=True)
            if uuid is None:
                # most likely a duplicate
                raise tornado.web.HTTPError(409)
            __info.append("new entry created [{}]".format(uuid))
            dp = self.db.add(uuid)
            dp.fm.writeTags(tags)
            dp.fm.setWebUrl(url)
        else:
            dp = self.db[uuid]
            __info.append("update entry [{}]".format(uuid))
            if dp.fm.readBib() != bibtex:
                dp.fm.writeBib(bibtex)
                __info.append("bibtex updated")
            if DataTags(dp.tags) != DataTags(tags):
                dp.fm.writeTags(DataTags(tags).toOrderedList())
                __info.append("tags updated")
            if dp.fm.getWebUrl() != url:
                dp.fm.setWebUrl(url)
                __info.append("url updated")
        self.logger.info(", ".join(__info))

        dp.loadInfo()   # update the cached info
        self.write(json.dumps(dp.summary))
        return 