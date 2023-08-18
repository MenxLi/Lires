
"""
Data management / manipulation handlers
This are handlers to (partially) replace the file handlers in lires/server/handlers/file.py
Provides handers for adding, deleting, and modifying files/tags
"""

from ._base import *
import json, os, tempfile
from lires.core.bibReader import checkBibtexValidity
from lires.core.fileTools import addDocument
from lires.core.dataClass import DataTags
from lires.confReader import getConf, TMP_DIR

import pprint
class DataDeleteHandler(RequestHandlerMixin, tornado.web.RequestHandler):
    def post(self):
        if not self.checkKey():
            raise tornado.web.HTTPError(403)
        self.setDefaultHeader()
        uuid = self.get_argument("uuid")
        if self.db.delete(uuid):
            self.logger.info(f"Deleted {uuid}")
        self.write("OK")
        return

class DataUpdateHandler(RequestHandlerMixin, tornado.web.RequestHandler):
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

class DocumentUploadHandler(tornado.web.RequestHandler, RequestHandlerMixin):

    async def post(self, uid: str):
        # permission check
        permission = self.checkKey()
        dp = self.db[uid]
        if not permission["is_admin"]:
            self.checkTagPermission(dp.tags, permission["mandatory_tags"])

        self.setDefaultHeader()
        file_info = self.request.files['file'][0]  # Get the file information
        file_data = file_info['body']  # Get the file data
        
        # Here, you can perform any necessary operations with the file data,
        # such as saving it to disk or processing it further.
        # For this example, we'll just print the file name and size.
        original_filename = file_info['filename']
        file_size = len(file_data)
        self.logger.info(f"Received file: {original_filename} ({file_size} bytes)")

        #check file extension
        ext = os.path.splitext(original_filename)[1]
        if ext not in getConf()["accepted_extensions"]:
            raise tornado.web.HTTPError(400, reason="File extension not allowed")
        
        # save the file to a temporary location
        tmp_file = os.path.join(TMP_DIR, "upload_" + uid + ext)
        with open(tmp_file, "wb") as f:
            f.write(file_data)
        
        # add the file to the document
        if not dp.fm.addFile(tmp_file):
            # remove the temporary file
            os.remove(tmp_file)
            # existing file
            raise tornado.web.HTTPError(409, reason="File already exists")

        dp.loadInfo()
        os.remove(tmp_file)
        
        self.logger.info(f"Document {uid} added")
        self.write(json.dumps(dp.summary))

class DocumentFreeHandler(RequestHandlerMixin, tornado.web.RequestHandler):
    def post(self, uid: str):
        """
        Free a document from a file
        """
        self.setDefaultHeader()
        permission = self.checkKey()
        dp = self.db[uid]
        if not permission["is_admin"]:
            self.checkTagPermission(dp.tags, permission["mandatory_tags"])

        if not dp.fm.deleteDocument():
            raise tornado.web.HTTPError(500, reason="Failed to delete file")
        self.logger.info(f"Document {uid} freed")
        dp.loadInfo()
        self.write(json.dumps(dp.summary))

class TagRenameHandler(RequestHandlerMixin, tornado.web.RequestHandler):
    def post(self):
        """
        Rename a tag
        """
        self.setDefaultHeader()
        permission = self.checkKey()
        old_tag = self.get_argument("oldTag")
        new_tag = self.get_argument("newTag")
        if not permission["is_admin"]:
            # only admin can rename tags
            raise tornado.web.HTTPError(403)
        self.db.renameTag(old_tag, new_tag)
        self.logger.info(f"Tag [{old_tag}] renamed to [{new_tag}] by [{permission['identifier']}]")
        self.write("OK")

class TagDeleteHandler(RequestHandlerMixin, tornado.web.RequestHandler):
    def post(self):
        """
        Delete a tag
        """
        self.setDefaultHeader()
        permission = self.checkKey()
        tag = self.get_argument("tag")
        if not permission["is_admin"]:
            # only admin can delete tags
            raise tornado.web.HTTPError(403)
        self.db.deleteTag(tag)
        self.logger.info(f"Tag [{tag}] deleted by [{permission['identifier']}]")
        self.write("OK")