"""
Get documents: document file / web page / comments
"""
from ._base import *
import base64
import os, json, re
import aiofiles
from lires.config import ACCEPTED_EXTENSIONS
from lires.core import pdfTools

class DocHandler(RequestHandlerBase):
    async def get(self, uuid):
        db = await self.db()
        file_p = await (await db.get(uuid)).fm.filePath()
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
    
    @authenticate()
    async def put(self, uid):
        """
        Upload document file
        """
        self.set_header("Content-Type", "application/json")
        # permission check
        db = await self.db()
        dp = await db.get(uid)
        if not (await self.userInfo())["is_admin"]:
            await self.checkTagPermission(dp.tags, (await self.userInfo())["mandatory_tags"])

        file_info = self.request.files['file'][0]  # Get the file information
        file_data = file_info['body']  # Get the file data
        content_type: str = file_info['content_type']
        
        original_filename = file_info['filename']
        file_size = len(file_data)
        await self.logger.info(f"Received file: {original_filename} ({file_size} bytes)")

        # check if the file is too large
        if file_size + await db.diskUsage() > (await self.userInfo())["max_storage"]:
            raise tornado.web.HTTPError(413, reason="File too large")

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

        dp = await db.get(uid)
        await self.ensureFeatureUpdate(dp)
        d_summary = dp.summary.json()
        await self.logger.info(f"Document {uid} added")
        await self.broadcastEventMessage({
            "type": 'update_entry',
            'uuid': uid,
            'datapoint_summary': d_summary
        })
        self.write(json.dumps(d_summary))
    
    @authenticate()
    async def delete(self, uid):
        """
        Free a document from a file
        """
        self.set_header("Content-Type", "application/json")
        db = await self.db()
        dp = await db.get(uid)
        if not (await self.userInfo())["is_admin"]:
            await self.checkTagPermission(dp.tags, (await self.userInfo())["mandatory_tags"])

        if not await dp.fm.deleteDocument():
            raise tornado.web.HTTPError(500, reason="Failed to delete file")
        await self.logger.info(f"Document {uid} freed")
        dp = await db.get(uid)
        await self.broadcastEventMessage({
            "type": 'update_entry',
            'uuid': uid,
            'datapoint_summary': dp.summary.json()
        })
        self.write(json.dumps(dp.summary.json()))

class DryDocHandler(RequestHandlerBase):
    """
    Return the document file in minimal format, 
    for PDF and HTML, remove all the images and return the text only version
    """
    async def get(self, uuid):
        db = await self.db()
        file_p = await (await db.get(uuid)).fm.filePath()
        if isinstance(file_p, str):
            if file_p.endswith(".pdf"):
                async with pdfTools.PDFAnalyser(file_p) as doc:
                    doc.removeImages()
                    self.set_header("Content-Type", 'application/pdf; charset="utf-8"')
                    self.set_header("Content-Disposition", "inline; filename={}.pdf".format(uuid))
                    self.write(doc.toBytes())
                    return
            if file_p.endswith(".html"):
                async with aiofiles.open(file_p, "r", encoding="utf-8") as f:
                    html = await f.read()
                    self.set_header("Content-Type", 'text/html; charset="utf-8"')
                    html = re.sub(r'<img[^>]*>', '', html)
                    self.write(html)
                    return
        self.write("The file not exist or is not supported.")

class DocTextHandler(RequestHandlerBase):
    """
    Return the text content of the document
    """
    async def get(self, uuid):
        db = await self.db()
        file_p = await (await db.get(uuid)).fm.filePath()
        if isinstance(file_p, str):
            if file_p.endswith(".pdf"):
                async with pdfTools.PDFAnalyser(file_p) as doc:
                    text = doc.getText()
                    self.set_header("Content-Type", 'text/plain; charset="utf-8"')
                    self.write(text)
                    return
            if file_p.endswith(".html"):
                raise tornado.web.HTTPError(400, reason="HTML file is not supported yet")
        self.write("The file not exist or is not supported.")