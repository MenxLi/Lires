
from ._base import *
from lires.core.dataClass import DataTags
import json


class UserCreateHandler(RequestHandlerBase):

    @keyRequired
    def post(self):
        # only admin access
        if not self.user_info["is_admin"]:
            raise tornado.web.HTTPError(403)
        
        username = self.get_argument("username")
        password = self.get_argument("password")
        name = self.get_argument("name", default="Anonymous")
        mandatory_tags = json.loads(self.get_argument("mandatory_tags", default="[]"))
        is_admin = json.loads(self.get_argument("is_admin", default="false"))

        # check if username exists
        if self.user_pool.getUserByUsername(username) is not None:
            raise tornado.web.HTTPError(409, "Username already exists")
        
        self.user_pool.conn.insertUser(
            username=username,
            password=password,
            name=name,
            is_admin=is_admin,
            mandatory_tags=mandatory_tags,
            )
        
        user = self.user_pool.getUserByUsername(username)
        assert user is not None, "User not found"   # should not happen
        to_send = user.info()
        to_send["enc_key"] = "__HIDDEN__"

        self.broadcastEventMessage({
            'type': 'add_user',
            'username': to_send["username"],
            'user_info': to_send
        })

        self.write(json.dumps(to_send))

class UserDeleteHandler(RequestHandlerBase):

    @keyRequired
    def post(self):
        # only admin access
        if not self.user_info["is_admin"]:
            raise tornado.web.HTTPError(403)
        
        username = self.get_argument("username")
        user = self.user_pool.getUserByUsername(username)
        if user is None:
            raise tornado.web.HTTPError(404, "User not found")
        self.user_pool.deleteUser(user.info()["id"])
        self.broadcastEventMessage({
            'type': 'delete_user',
            'username': username,
            'user_info': None
        })
        self.write("Success")

class UserModifyHandler(RequestHandlerBase):
    @keyRequired
    def post(self):
        # only admin access
        if not self.user_info["is_admin"]:
            raise tornado.web.HTTPError(403)
        
        username = self.get_argument("username")
        user = self.user_pool.getUserByUsername(username)
        if user is None:
            raise tornado.web.HTTPError(404, "User not found")
        
        new_admin_status = json.loads(self.get_argument("is_admin", default='null'))
        if new_admin_status is not None:
            user.conn.updateUser(user.info()["id"], is_admin=new_admin_status)
        
        new_mandatory_tags = json.loads(self.get_argument("mandatory_tags", default='null'))
        if new_mandatory_tags is not None:
            user.conn.updateUser(user.info()["id"], mandatory_tags=DataTags(new_mandatory_tags).toOrderedList())
        
        _user_info_desens = user.info_desensitized()
        self.broadcastEventMessage({
            'type': 'update_user',
            'username': _user_info_desens["username"],
            'user_info': _user_info_desens
        })
        
        self.write(json.dumps(_user_info_desens))