"""
Get documents: document file / web page / comments
"""
from ._base import *
import base64
import os, json
import aiofiles
from lires.config import ACCEPTED_EXTENSIONS

class DocHandler(RequestHandlerBase):
    async def get(self, uuid):
        file_p = await (await self.db.get(uuid)).fm.filePath()
        if isinstance(file_p, str):
            if file_p.endswith(".pdf"):
                async with aiofiles.open(file_p, "rb") as f:
                    self.set_header("Content-Type", 'application/pdf; charset="utf-8"')
                    self.set_header("Content-Disposition", "inline; filename={}.pdf".format(uuid))
                    self.write(await f.read())
                    return
            if file_p.endswith(".html"):
                async with aiofiles.open(file_p, "r", encoding="utf-8") as f:
                    self.set_header("Content-Type", 'text/html; charset="utf-8"')
                    self.write(await f.read())
                    return
        self.write("The file not exist or is not supported.")
    
    @keyRequired
    async def put(self, uid):
        """
        Upload document file
        """
        # permission check
        dp = await self.db.get(uid)
        if not (await self.userInfo())["is_admin"]:
            await self.checkTagPermission(dp.tags, (await self.userInfo())["mandatory_tags"])

        file_info = self.request.files['file'][0]  # Get the file information
        file_data = file_info['body']  # Get the file data
        content_type: str = file_info['content_type']
        
        original_filename = file_info['filename']
        file_size = len(file_data)
        await self.logger.info(f"Received file: {original_filename} ({file_size} bytes)")

        #check file extension
        ext = os.path.splitext(original_filename)[1]

        if content_type.startswith("image/"):
            # embed as html
            b64_im = "data:{};base64,{}".format(content_type, base64.b64encode(file_data).decode())
            html = '<!DOCTYPE html><html><head><title>{}</title></head><body style="display: flex; justify-content: center; align-items: center">'.format(uid) + \
                f'<img src="{b64_im}" alt="{uid}" style="max-width: 100%; max-height: 100%;" />' + \
                '</body></html>'
            ext = ".html"
            file_data = html.encode("utf-8")

        else:
            if ext not in ACCEPTED_EXTENSIONS:
                # this may be a security issue... as we only check the extension
                # TODO: check the file type
                raise tornado.web.HTTPError(400, reason="File extension not allowed")
        
        # add the file to the document
        if not await dp.fm.addFileBlob(file_data, ext):
            raise tornado.web.HTTPError(409, reason="File already exists")

        dp = await self.db.get(uid)
        d_summary = dp.summary.json()
        await self.logger.info(f"Document {uid} added")
        await self.broadcastEventMessage({
            "type": 'update_entry',
            'uuid': uid,
            'datapoint_summary': d_summary
        })
        self.write(json.dumps(d_summary))
    
    @keyRequired
    async def delete(self, uid):
        """
        Free a document from a file
        """
        dp = await self.db.get(uid)
        if not (await self.userInfo())["is_admin"]:
            await self.checkTagPermission(dp.tags, (await self.userInfo())["mandatory_tags"])

        if not await dp.fm.deleteDocument():
            raise tornado.web.HTTPError(500, reason="Failed to delete file")
        await self.logger.info(f"Document {uid} freed")
        dp = await self.db.get(uid)
        await self.broadcastEventMessage({
            "type": 'update_entry',
            'uuid': uid,
            'datapoint_summary': dp.summary.json()
        })
        self.write(json.dumps(dp.summary.json()))