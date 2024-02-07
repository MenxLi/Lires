"""
To access and modify images under the misc folder of each datapoint
"""
from ._base import *
import os, uuid
import aiofiles

class ImageHandler(RequestHandlerBase):
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
        await self.emitImage(uid, fname)

    async def emitImage(self, uid: str, fname: str):
        """
        Args:
            uid (str): uuid of the datapoint
            fname (str): filename of the image
        """
        dp = await self.db.get(uid)
        misc_dir = dp.fm.getMiscDir()
        fpath = os.path.join(misc_dir, fname)
        if not os.path.exists(fpath):
            raise tornado.web.HTTPError(404)

        if (not os.path.isfile(fpath)):
            raise tornado.web.HTTPError(404)

        allowed_ext = [".png", ".jpg", ".jpeg"]
        if not any([fpath.endswith(ext) for ext in allowed_ext]):
            raise tornado.web.HTTPError(404)
        
        async with aiofiles.open(fpath, "rb") as f:
            # set header to be image
            if fpath.endswith(".png"):
                self.set_header("Content-Type", "image/png")
            elif fpath.endswith(".jpg") or fpath.endswith(".jpeg"):
                self.set_header("Content-Type", "image/jpeg")
            self.write(await f.read())

    @keyRequired
    async def put(self, uid: str):
        # permission check
        dp = await self.db.get(uid)
        if not (await self.userInfo())["is_admin"]:
            await self.checkTagPermission(dp.tags, (await self.userInfo())["mandatory_tags"])

        file_info = self.request.files['file'][0]  # Get the file information
        original_filename = file_info['filename']

        file_data = file_info['body']  # Get the file data
        file_size = len(file_data)
        await self.logger.info(f"Received file: {original_filename} ({file_size} bytes)")

        # Generate a unique filename for the uploaded file
        filename = str(uuid.uuid4()) + os.path.splitext(original_filename)[1]

        fpath = os.path.join(dp.fm.getMiscDir(create=True), filename)
        async with aiofiles.open(fpath, "wb") as f:
            await f.write(file_data)
        
        self.write({
            "status": "OK",
            "file_name": filename,
        })