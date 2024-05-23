
"""
Data management / manipulation handlers
This are handlers to (partially) replace the file handlers in lires/server/handlers/file.py
Provides handers for adding, deleting, and modifying files/tags
"""

from ._base import *
import json, asyncio
from lires.core.bibReader import checkBibtexValidity, BibConverter
from lires.core.fileTools import addDocument
from lires.core.dataTags import DataTags

class DataDeleteHandler(RequestHandlerBase):

    @authenticate()
    async def post(self):
        uuid = self.get_argument("uuid")
        db = await self.db()
        # check tag permission
        if not (await self.userInfo())["is_admin"]:
            await self.checkTagPermission(
                (await db.get(uuid)).tags, (await self.userInfo())["mandatory_tags"]
                )
        
        await self.deleteFeature(await db.get(uuid))
        if await db.delete(uuid):
            await self.logger.info(f"Deleted {uuid}")
        
        await self.broadcastEventMessage({
            'type': 'delete_entry',
            'uuid': uuid, 
            'datapoint_summary': None
        })
        self.write("OK")
        return

class DataUpdateHandler(RequestHandlerBase):

    @authenticate()
    async def post(self):
        """
        Update or create a data entry
        arguments:
            uuid: uuid of the data entry (None for new entry)
            tags: list[str], bibtex: str, url: str
        return:
            summary of the data entry
        """
        self.set_header("Content-Type", "application/json")
        permission = await self.userInfo()
        db = await self.db()

        __info = [] # for logging

        # uuid = json.loads(self.get_argument("uuid", 'null'))
        uuid = self.get_argument("uuid", "null")
        if uuid == "null" or uuid == "":
            uuid = None

        if uuid is not None and uuid.startswith('"') and uuid.endswith('"'):
            # backward compatibility to old api copies, since 1.7.5
            uuid = uuid[1:-1]   # remove the quotes, if the uid is json encoded

        assert uuid is None or isinstance(uuid, str)

        # optional arguments (set to None) if uuid is present
        tags = json.loads(self.get_argument("tags", 'null'))
        url = self.get_argument("url", None)
        if url == "null": url = None
        bibtex = self.get_argument("bibtex", None)
        if bibtex == "null": bibtex = None
        
        if not permission["is_admin"]:
            if uuid is None:
                # if the uuid is not provided, check tag validity using new tags
                await self.checkTagPermission(tags, permission["mandatory_tags"])
            else:
                # if the uuid is provided, check tag validity using old tags
                old_tags = (await db.get(uuid)).tags
                await self.checkTagPermission(old_tags, permission["mandatory_tags"])

        if bibtex is not None and not await checkBibtexValidity(bibtex, self.logger.error):
            # check if it is other format
            # TODO: find a more elegant way to do this...
            bib_converter = BibConverter()
            __c_bibtex = None
            if not __c_bibtex:
                try:
                    __c_bibtex = await bib_converter.fromNBib(bibtex)
                    await self.logger.debug("Obtained bibtex from nbib")
                except Exception as e:
                    await self.logger.debug(f"Failed to convert from nbib: {e}")
            
            if not __c_bibtex:
                try:
                    __c_bibtex = bib_converter.fromEndNote(bibtex)
                    await self.logger.debug("Obtained bibtex from endnote")
                except:
                    await self.logger.debug("Failed to convert from endnote")

            if __c_bibtex and checkBibtexValidity(__c_bibtex, self.logger.error):
                # successfully converted from other format
                bibtex = __c_bibtex
            else:
                await self.logger.warning("Invalid bibtex")
                raise tornado.web.HTTPError(400)
        
        if uuid is None:
            assert bibtex is not None
            assert tags is not None
            assert url is not None

            # check disk usage
            if await db.diskUsage()+128 > permission["max_storage"]:
                raise tornado.web.HTTPError(413, reason="File too large")

            uuid = await addDocument(
                db.conn, bibtex, 
                url = url,
                tags = DataTags(tags).toOrderedList(),
                check_duplicate = True
                )
            if uuid is None:
                # most likely a duplicate
                raise tornado.web.HTTPError(409)
            __info.append("new entry created [{}]".format(uuid))

            dp = await db.get(uuid)   # update the cached info
            await self.broadcastEventMessage({
                'type': 'add_entry',
                'uuid': uuid, 
                'datapoint_summary': dp.summary.json()
            })
        else:
            dp = await db.get(uuid)
            __info.append("update entry [{}]".format(uuid))
            if bibtex is not None and await dp.fm.readBib() != bibtex:
                await dp.fm.writeBib(bibtex, format=True)
                __info.append("bibtex updated")
            if tags is not None and DataTags(dp.tags) != DataTags(tags):
                await dp.fm.writeTags(DataTags(tags))
                __info.append("tags updated")
            if url is not None and await dp.fm.getWebUrl() != url:
                await dp.fm.setWebUrl(url)
                __info.append("url updated")
            
            dp = await db.get(uuid)   # update the cached info
            await self.broadcastEventMessage({
                'type': 'update_entry',
                'uuid': uuid,
                'datapoint_summary': dp.summary.json()
            })

        await self.logger.info(", ".join(__info))

        self.write(json.dumps(dp.summary.json()))
        await self.ensureFeatureUpdate(dp)

        return 

class TagRenameHandler(RequestHandlerBase):
    @authenticate()
    async def post(self):
        """
        Rename a tag
        """
        db = await self.db()
        old_tag = self.get_argument("oldTag")
        new_tag = self.get_argument("newTag")
        await db.renameTag(old_tag, new_tag)
        await self.logger.info(f"Tag [{old_tag}] renamed to [{new_tag}] by [{(await self.userInfo())['name']}]")
        await self.broadcastEventMessage({
            'type': 'update_tag',
            'src_tag': old_tag,
            'dst_tag': new_tag
        })
        self.write("OK")

class TagDeleteHandler(RequestHandlerBase):
    @authenticate()
    async def post(self):
        """
        Delete a tag
        """
        db = await self.db()
        tag = self.get_argument("tag")
        await db.deleteTag(tag)
        await self.logger.info(f"Tag [{tag}] deleted by [{(await self.userInfo())['name']}]")
        await self.broadcastEventMessage({
            'type': 'delete_tag',
            'src_tag': tag,
            'dst_tag': None
        })
        self.write("OK")