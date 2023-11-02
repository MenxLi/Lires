
import json
from io import BytesIO
from PIL import Image
from ._base import *

class UserInfoHandler(tornado.web.RequestHandler, RequestHandlerMixin):

    # @keyRequired
    def post(self, username):
        self.setDefaultHeader()

        user = self.user_pool.getUserByUsername(username)
        if user is None:
            raise tornado.web.HTTPError(404, "User not found")
        
        to_send = user.info()
        to_send["enc_key"] = "__HIDDEN__"
        
        self.write(json.dumps(to_send))

class UserInfoUpdateHandler(tornado.web.RequestHandler, RequestHandlerMixin):
    @keyRequired
    def post(self):
        user = self.user_pool.getUserByKey(self.user_info["enc_key"])
        assert user is not None, "User not found"   # should not happen
        id_ = user.info()["id"]

        self.setDefaultHeader()

        new_name = self.get_argument("name", None)
        if new_name is not None:
            user.conn.updateUser(id_, name=new_name)

        new_password = self.get_argument("password", None)
        if new_password is not None:
            user.conn.updateUser(id_, password=new_password)
        
        self.write(json.dumps(user.info()))


class UserListHandler(tornado.web.RequestHandler, RequestHandlerMixin):

    # @keyRequired
    def post(self):
        self.setDefaultHeader()

        to_send = []
        for user in self.user_pool:
            u_info = user.info()
            u_info["enc_key"] = "__HIDDEN__"
            to_send.append(u_info)
        
        self.write(json.dumps(to_send))

class UserAvatarHandler(tornado.web.RequestHandler, RequestHandlerMixin):

    def get(self, username: str):
        im_size = int(self.get_argument("size", "512"))
        if im_size > 512 or im_size < 1:
            raise tornado.web.HTTPError(400, "Invalid size, must be [1, 512]")

        user = self.user_pool.getUserByUsername(username)
        if user is None or user.avatar_image_path is None:
            self.set_header("Content-Type", "image/png")
            self.set_header("Content-Disposition", "inline")    
            self.set_header("Cache-Control", "no-cache")
            # raise tornado.web.HTTPError(404, "User has no avatar")
            gray_image = Image.new("RGB", (im_size, im_size), (128, 128, 128))
            with BytesIO() as output:
                gray_image.save(output, format="PNG")
                contents = output.getvalue()
            self.write(contents)
            return 

        else:
            avatar_path = user.avatar_image_path
            
            self.set_header("Content-Type", "image/png")

            # the content should be displayed within the browser window rather than being downloaded
            self.set_header("Content-Disposition", "inline")    

            # the response can be cached by the client or intermediate caches for a maximum of 86400 seconds (24 hours)
            self.set_header("Cache-Control", "max-age=86400")

            img = Image.open(avatar_path["square"])
            img.thumbnail((im_size, im_size))
            with BytesIO() as output:
                img.save(output, format="PNG")
                contents = output.getvalue()
            self.write(contents)
        

class UserAvatarUploadHandler(tornado.web.RequestHandler, RequestHandlerMixin):

    @keyRequired
    def post(self):
        self.setDefaultHeader()
        user = self.user_pool.getUserByKey(self.user_info["enc_key"])
        assert user is not None, "User not found"   # should not happen
        
        if not self.request.files:
            raise tornado.web.HTTPError(400, "No file uploaded")
        
        file = self.request.files["file"][0]
        if file["content_type"] != "image/png" and file["content_type"] != "image/jpeg":
            self.logger.debug("File type not supported: {}".format(file["content_type"]))
            raise tornado.web.HTTPError(400, "File type not supported")
        
        im = Image.open(BytesIO(file["body"]))
        user.setAvatar(im)
        self.write(json.dumps(user.info()))