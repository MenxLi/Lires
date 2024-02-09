
from ._base import *
from lires.core.dataTags import DataTags
import json


class UserCreateHandler(RequestHandlerBase):

    @keyRequired
    async def post(self):
        # only admin access
        if not (await self.userInfo())["is_admin"]:
            raise tornado.web.HTTPError(403)
        
        username = self.get_argument("username")
        password = self.get_argument("password")
        name = self.get_argument("name", default="Anonymous")
        mandatory_tags = json.loads(self.get_argument("mandatory_tags", default="[]"))
        is_admin = json.loads(self.get_argument("is_admin", default="false"))

        # check if username exists
        if await self.user_pool.getUserByUsername(username) is not None:
            raise tornado.web.HTTPError(409, "Username already exists")
        
        await self.user_pool.conn.insertUser(
            username=username,
            password=password,
            name=name,
            is_admin=is_admin,
            mandatory_tags=mandatory_tags,
            )
        
        user = await self.user_pool.getUserByUsername(username)
        assert user is not None, "User not found"   # should not happen
        to_send = await user.info_desensitized()

        await self.broadcastEventMessage({
            'type': 'add_user',
            'username': to_send["username"],
            'user_info': to_send
        })

        self.write(json.dumps(to_send))

class UserDeleteHandler(RequestHandlerBase):

    @keyRequired
    async def post(self):
        # only admin access
        if not (await self.userInfo())["is_admin"]:
            raise tornado.web.HTTPError(403)
        
        username = self.get_argument("username")
        user = await self.user_pool.getUserByUsername(username)
        if user is None:
            raise tornado.web.HTTPError(404, "User not found")
        await self.user_pool.deleteUser((await user.info())["id"])
        await self.broadcastEventMessage({
            'type': 'delete_user',
            'username': username,
            'user_info': None
        })
        self.write("Success")

class UserModifyHandler(RequestHandlerBase):
    @keyRequired
    async def post(self):
        # only admin access
        if not (await self.userInfo())["is_admin"]:
            raise tornado.web.HTTPError(403)
        
        username = self.get_argument("username")
        user = await self.user_pool.getUserByUsername(username)
        if user is None:
            raise tornado.web.HTTPError(404, "User not found")
        user_info = await user.info()
        
        new_admin_status = json.loads(self.get_argument("is_admin", default='null'))
        if new_admin_status is not None:
            await user.conn.updateUser(user_info["id"], is_admin=new_admin_status)
        
        new_mandatory_tags = json.loads(self.get_argument("mandatory_tags", default='null'))
        if new_mandatory_tags is not None:
            await user.conn.updateUser(user_info["id"], mandatory_tags=DataTags(new_mandatory_tags).toOrderedList())
        
        _user_info_desens = await user.info_desensitized()
        await self.broadcastEventMessage({
            'type': 'update_user',
            'username': _user_info_desens["username"],
            'user_info': _user_info_desens
        })
        
        self.write(json.dumps(_user_info_desens))