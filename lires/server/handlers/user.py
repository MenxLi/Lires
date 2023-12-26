
import json, os
from io import BytesIO
from PIL import Image
from ._base import *

class UserInfoHandler(RequestHandlerBase):

    # @keyRequired
    def post(self, username):

        user = self.user_pool.getUserByUsername(username)
        if user is None:
            raise tornado.web.HTTPError(404, "User not found")
        
        to_send = user.info()
        to_send["enc_key"] = "__HIDDEN__"
        
        self.write(json.dumps(to_send))

class UserInfoUpdateHandler(RequestHandlerBase):
    """
    To update a user's own settings.
    Admin should update any user's settings using handers in userMan.py
    """
    @keyRequired
    def post(self):
        user = self.user_pool.getUserByKey(self.user_info["enc_key"])
        assert user is not None, "User not found"   # should not happen
        id_ = user.info()["id"]

        new_name = self.get_argument("name", None)
        if new_name is not None:
            user.conn.updateUser(id_, name=new_name)

        new_password = self.get_argument("password", None)
        if new_password is not None:
            user.conn.updateUser(id_, password=new_password)
        
        _user_info = user.info()
        self.broadcastEventMessage({
            'type': 'update_user',
            'username': _user_info["username"],
            'user_info': user.info_desensitized()
        })
        
        self.write(json.dumps(_user_info))


class UserListHandler(RequestHandlerBase):

    # @keyRequired
    def post(self):
        to_send = []
        for user in self.user_pool:
            u_info = user.info()
            u_info["enc_key"] = "__HIDDEN__"
            to_send.append(u_info)
        
        self.write(json.dumps(to_send))

class UserAvatarHandler(RequestHandlerBase):

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
            # self.set_header("Cache-Control", "max-age=86400")
            self.set_header("Cache-Control", "max-age=60")

            img = Image.open(avatar_path["square"])
            img.thumbnail((im_size, im_size))
            with BytesIO() as output:
                img.save(output, format="PNG")
                contents = output.getvalue()
            self.write(contents)
        
    @keyRequired
    def put(self):
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
    
    @keyRequired
    def delete(self):
        user = self.user_pool.getUserByKey(self.user_info["enc_key"])
        assert user is not None, "User not found"

        avatar_image_path = user.avatar_image_path
        if avatar_image_path is None:
            raise tornado.web.HTTPError(404, "User has no avatar")
        else:
            for k in avatar_image_path:
                os.remove(avatar_image_path[k])
            self.write(json.dumps(user.info()))