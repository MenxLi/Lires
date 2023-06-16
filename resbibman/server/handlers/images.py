"""
To access and modify images under the misc folder of each datapoint
"""
from ._base import *
import os


class ImageGetHandler(tornado.web.RequestHandler, RequestHandlerBase):
    """
    Get image from misc folder
    """
    def get(self, uid:str):
        """
        Args:
            uid (str): uuid of the datapoint
        """

        # self.setDefaultHeader()
        fname = self.get_argument("fname")
        self.emitImage(uid, fname)

    def emitImage(self, uid: str, fname: str):
        """
        Args:
            uid (str): uuid of the datapoint
            fname (str): filename of the image
        """
        dp = self.db[uid]
        misc_dir = dp.fm.getMiscDir()
        fpath = os.path.join(misc_dir, fname)
        if not os.path.exists(fpath):
            raise tornado.web.HTTPError(404)

        if (not os.path.isfile(fpath)):
            raise tornado.web.HTTPError(404)

        allowed_ext = [".png", ".jpg", ".jpeg"]
        if not any([fpath.endswith(ext) for ext in allowed_ext]):
            raise tornado.web.HTTPError(404)
        
        with open(fpath, "rb") as f:
            # set header to be image
            if fpath.endswith(".png"):
                self.set_header("Content-Type", "image/png")
            elif fpath.endswith(".jpg") or fpath.endswith(".jpeg"):
                self.set_header("Content-Type", "image/jpeg")

            self.write(f.read())


## Not tested!
class ImageUploadHandler(tornado.web.RequestHandler, RequestHandlerBase):
    """
    Upload image to misc folder
    """
    def post(self, uid:str):
        """
        Args:
            uid (str): uuid of the datapoint
        """
        # self.setDefaultHeader()
        fname = self.get_argument("fname")
        self.uploadImage(uid, fname)

    def uploadImage(self, uid: str, fname: str):
        """
        Args:
            uid (str): uuid of the datapoint
            fname (str): filename of the image
        """
        dp = self.db[uid]
        misc_dir = dp.fm.getMiscDir(create=True)
        fpath = os.path.join(misc_dir, fname)
        if os.path.exists(fpath):
            raise tornado.web.HTTPError(409)

        with open(fpath, "wb") as f:
            f.write(self.request.body)