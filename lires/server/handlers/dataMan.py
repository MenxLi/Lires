
"""
Data management / manipulation handlers
This are handlers to (partially) replace the file handlers in lires/server/handlers/file.py
Provides handers for adding, deleting, and modifying files/tags
"""

from ._base import *
import json
from lires.core.bibReader import checkBibtexValidity, BibConverter
from lires.core.fileTools import addDocument
from lires.core.dataClass import DataTags

class DataDeleteHandler(RequestHandlerBase):

    @keyRequired
    async def post(self):
        uuid = self.get_argument("uuid")
        # check tag permission
        if not self.user_info["is_admin"]:
            self.checkTagPermission(self.db[uuid].tags, self.user_info["mandatory_tags"])

        if self.db.delete(uuid):
            self.logger.info(f"Deleted {uuid}")
        
        self.broadcastEventMessage({
            'type': 'delete_entry',
            'uuid': uuid, 
            'datapoint_summary': None
        })
        self.write("OK")
        return

class DataUpdateHandler(RequestHandlerBase):

    @keyRequired
    async def post(self):
        """
        Update or create a data entry
        arguments:
            uuid: uuid of the data entry (None for new entry)
            tags: list[str], bibtex: str, url: str
        """
        permission = self.user_info

        __info = [] # for logging

        uuid = json.loads(self.get_argument("uuid"))
        assert uuid is None or isinstance(uuid, str)

        # optional arguments (set to None) if uuid is present
        tags = json.loads(self.get_argument("tags", 'null'))
        url = self.get_argument("url", None)
        bibtex = self.get_argument("bibtex", None)
        
        if not permission["is_admin"]:
            if uuid is None:
                # if the uuid is not provided, check tag validity using new tags
                self.checkTagPermission(tags, permission["mandatory_tags"])
            else:
                # if the uuid is provided, check tag validity using old tags
                old_tags = self.db[uuid].tags
                self.checkTagPermission(old_tags, permission["mandatory_tags"])

        if bibtex is not None and not checkBibtexValidity(bibtex, self.logger.error):
            # check if it is other format
            # TODO: find a more elegant way to do this...
            bib_converter = BibConverter()
            __c_bibtex = None
            if not __c_bibtex:
                try:
                    __c_bibtex = bib_converter.fromNBib(bibtex)
                    self.logger.debug("Obtained bibtex from nbib")
                except Exception as e:
                    self.logger.debug(f"Failed to convert from nbib: {e}")
            
            if not __c_bibtex:
                try:
                    __c_bibtex = bib_converter.fromEndNote(bibtex)
                    self.logger.debug("Obtained bibtex from endnote")
                except:
                    self.logger.debug("Failed to convert from endnote")

            if __c_bibtex and checkBibtexValidity(__c_bibtex, self.logger.error):
                # successfully converted from other format
                bibtex = __c_bibtex
            else:
                self.logger.warning("Invalid bibtex")
                raise tornado.web.HTTPError(400)
        
        if uuid is None:
            assert bibtex is not None
            assert tags is not None
            assert url is not None

            uuid = addDocument(self.db.conn, bibtex, check_duplicate=True)
            if uuid is None:
                # most likely a duplicate
                raise tornado.web.HTTPError(409)
            __info.append("new entry created [{}]".format(uuid))
            dp = self.db.add(uuid)
            dp.fm.writeTags(tags)
            dp.fm.setWebUrl(url)

            dp.loadInfo()   # update the cached info
            self.broadcastEventMessage({
                'type': 'add_entry',
                'uuid': uuid, 
                'datapoint_summary': dp.summary
            })
        else:
            dp = self.db[uuid]
            __info.append("update entry [{}]".format(uuid))
            if bibtex is not None and dp.fm.readBib() != bibtex:
                dp.fm.writeBib(bibtex)
                __info.append("bibtex updated")
            if tags is not None and DataTags(dp.tags) != DataTags(tags):
                dp.fm.writeTags(DataTags(tags).toOrderedList())
                __info.append("tags updated")
            if url is not None and dp.fm.getWebUrl() != url:
                dp.fm.setWebUrl(url)
                __info.append("url updated")
            
            dp.loadInfo()   # update the cached info
            self.broadcastEventMessage({
                'type': 'update_entry',
                'uuid': uuid,
                'datapoint_summary': dp.summary
            })

        self.logger.info(", ".join(__info))
        self.write(json.dumps(dp.summary))
        return 

class TagRenameHandler(RequestHandlerBase):
    @keyRequired
    def post(self):
        """
        Rename a tag
        """
        old_tag = self.get_argument("oldTag")
        new_tag = self.get_argument("newTag")
        if not self.user_info["is_admin"]:
            # only admin can rename tags
            raise tornado.web.HTTPError(403)
        self.db.renameTag(old_tag, new_tag)
        self.logger.info(f"Tag [{old_tag}] renamed to [{new_tag}] by [{self.user_info['name']}]")
        self.broadcastEventMessage({
            'type': 'update_tag',
            'src_tag': old_tag,
            'dst_tag': new_tag
        })
        self.write("OK")

class TagDeleteHandler(RequestHandlerBase):
    @keyRequired
    def post(self):
        """
        Delete a tag
        """
        tag = self.get_argument("tag")
        if not self.user_info["is_admin"]:
            # only admin can delete tags
            raise tornado.web.HTTPError(403)
        self.db.deleteTag(tag)
        self.logger.info(f"Tag [{tag}] deleted by [{self.user_info['name']}]")
        self.broadcastEventMessage({
            'type': 'delete_tag',
            'src_tag': tag,
            'dst_tag': None
        })
        self.write("OK")