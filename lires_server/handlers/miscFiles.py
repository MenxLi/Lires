
"""
To access and modify images under the misc folder of each datapoint
"""
from ._base import *
import os, uuid, json
import aiofiles

class MiscFileListHandler(RequestHandlerBase):
    """
    Get list of files in the misc folder
    """
    @authenticate()
    async def get(self, uid:str):
        """
        Args:
            uid (str): uuid of the datapoint
        """
        self.set_header("Content-Type", "application/json")
        db = await self.db()
        dp = await db.get(uid)
        self.write(json.dumps(dp.fm.listMiscFiles()))

class MiscFileHandler(RequestHandlerBase):
    """
    Get image from misc folder
    """
    async def get(self, uid:str):
        """
        Args:
            uid (str): uuid of the datapoint
        """

        # self.setDefaultHeader()
        fname = self.get_argument("fname")
        await self.emitFile(uid, fname)
    
    async def emitFile(self, uid: str, fname: str):
        """
        Args:
            uid (str): uuid of the datapoint
            fname (str): filename of the image
        """
        db = await self.db()
        dp = await db.get(uid)
        misc_dir = dp.fm.getMiscDir()
        fpath = os.path.join(misc_dir, fname)
        if not os.path.exists(fpath):
            raise tornado.web.HTTPError(404, reason="File not found")

        if (not os.path.isfile(fpath)):
            raise tornado.web.HTTPError(404, reason="File not found")

        # set appropriate header
        if fpath.endswith(".png"):
            self.set_header("Content-Type", "image/png")
        elif fpath.endswith(".jpg") or fpath.endswith(".jpeg"):
            self.set_header("Content-Type", "image/jpeg")
        elif fpath.endswith(".svg"):
            self.set_header("Content-Type", "image/svg+xml")
        elif fpath.endswith(".pdf"):
            self.set_header("Content-Type", "application/pdf")
        elif fpath.endswith(".json"):
            self.set_header("Content-Type", "application/json")
        elif fpath.endswith(".txt"):
            self.set_header("Content-Type", "text/plain")
        elif fpath.endswith(".csv"):
            self.set_header("Content-Type", "text/csv")
        else:
            self.set_header("Content-Type", "application/octet-stream")
            
        async with aiofiles.open(fpath, "rb") as f:
            self.write(await f.read())

    @authenticate()
    async def put(self, uid: str):
        # permission check
        db = await self.db()
        dp = await db.get(uid)
        if not (await self.userInfo())["is_admin"]:
            await self.checkTagPermission(dp.tags, (await self.userInfo())["mandatory_tags"])

        file_info = self.request.files['file'][0]  # Get the file information
        original_filename = file_info['filename']

        file_data = file_info['body']  # Get the file data
        file_size = len(file_data)
        await self.logger.info(f"Received file: {original_filename} ({file_size} bytes)")

        # check if the file is too large
        if file_size + await db.diskUsage() > (await self.userInfo())["max_storage"]:
            raise tornado.web.HTTPError(413, reason="File too large")

        # Generate a unique filename for the uploaded file
        filename = str(uuid.uuid4())[:8] + os.path.splitext(original_filename)[1]

        fpath = os.path.join(dp.fm.getMiscDir(create=True), filename)
        async with aiofiles.open(fpath, "wb") as f:
            await f.write(file_data)
        await self.logger.info(f"Saved misc file to {fpath}")
        
        self.write({
            "status": "OK",
            "file_name": filename,
        })
    
    @authenticate()
    async def post(self, uid: str):
        # permission check
        db = await self.db()
        dp = await db.get(uid)
        if not (await self.userInfo())["is_admin"]:
            await self.checkTagPermission(dp.tags, (await self.userInfo())["mandatory_tags"])

        fname = self.get_argument("fname")
        new_fname = self.get_argument("dst_fname")
        fpath = os.path.join(dp.fm.getMiscDir(), fname)
        if not os.path.exists(fpath):
            raise tornado.web.HTTPError(404, reason="File not found")
        new_fpath = os.path.join(dp.fm.getMiscDir(), new_fname)
        if os.path.exists(new_fpath):
            raise tornado.web.HTTPError(409, reason="File already exists")
        
        os.rename(fpath, new_fpath)
        await self.logger.info(f"Renamed misc file {fpath} to {new_fpath}")
        self.write({ "status": "OK" })
    
    @authenticate()
    async def delete(self, uid: str):
        # permission check
        db = await self.db()
        dp = await db.get(uid)
        if not (await self.userInfo())["is_admin"]:
            await self.checkTagPermission(dp.tags, (await self.userInfo())["mandatory_tags"])

        fname = self.get_argument("fname")
        fpath = os.path.join(dp.fm.getMiscDir(), fname)
        if os.path.exists(fpath):
            os.remove(fpath)
            if not os.listdir(dp.fm.getMiscDir()):
                os.rmdir(dp.fm.getMiscDir())
            await self.logger.info(f"Deleted misc file {fpath}")
            self.write({ "status": "OK" })
        else:
            raise tornado.web.HTTPError(404, reason="File not found")