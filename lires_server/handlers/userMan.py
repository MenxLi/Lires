
from ._base import *
from lires.core.dataTags import DataTags
import json

class UserRegisterHandler(RequestHandlerBase):
    """ Create user with invitation code """
    async def post(self):
        invitation_code = self.get_argument("invitation_code")
        username = self.get_argument("username")
        password = self.get_argument("password")
        name = self.get_argument("name", default="Anonymous")

        invitation = await self.user_pool.conn.queryInvitation(invitation_code)
        if invitation is None:
            raise tornado.web.HTTPError(401, "Invitation code not found")
        if invitation["uses"] >= invitation["max_uses"]:
            raise tornado.web.HTTPError(403, "Invitation code has been used up")
        
        # check if username exists
        try:
            await self.user_pool.conn.insertUser(
                username=username,
                password=password,
                name=name,
                is_admin=False,
                mandatory_tags=[],
            )
        except self.Error.LiresUserDuplicationError:
            raise tornado.web.HTTPError(409, "Username already exists")
        except self.Error.LiresExceedLimitError:
            raise tornado.web.HTTPError(507, "Reached maximum user limit")

        await self.user_pool.conn.useInvitation(invitation_code)

        user = await self.user_pool.getUserByUsername(username)
        assert user is not None, "User not found"   # should not happen
        to_send = await user.info_desensitized()

        await self.logger.info("User {} registered with code: {}".format(to_send["username"], invitation_code))

        await self.broadcastEventMessage({
            'type': 'add_user',
            'username': to_send["username"],
            'user_info': to_send
        }, to_all=True)

        self.write(json.dumps(to_send))


class UserCreateHandler(RequestHandlerBase):

    @authenticate(admin_required=True)
    async def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        name = self.get_argument("name", default="Anonymous")
        mandatory_tags = json.loads(self.get_argument("mandatory_tags", default="[]"))
        is_admin = json.loads(self.get_argument("is_admin", default="false"))
        max_storage = json.loads(self.get_argument("max_storage", default="100"))   # in MB

        # check if username exists
        if await self.user_pool.getUserByUsername(username) is not None:
            raise tornado.web.HTTPError(409, "Username already exists")
        
        await self.user_pool.conn.insertUser(
            username=username,
            password=password,
            name=name,
            is_admin=is_admin,
            mandatory_tags=mandatory_tags,
            max_storage=max_storage*1024*1024
            )
        
        user = await self.user_pool.getUserByUsername(username)
        assert user is not None, "User not found"   # should not happen
        to_send = await user.info_desensitized()

        await self.broadcastEventMessage({
            'type': 'add_user',
            'username': to_send["username"],
            'user_info': to_send
        }, to_all=True)

        self.write(json.dumps(to_send))

class UserDeleteHandler(RequestHandlerBase):

    @authenticate(admin_required=True)
    async def post(self):
        username = self.get_argument("username")
        user = await self.user_pool.getUserByUsername(username)
        if user is None:
            raise tornado.web.HTTPError(404, "User not found")
        
        user_id = (await user.info())["id"]
        await self.db_pool.deleteDatabasePermanently(user_id)
        await self.user_pool.deleteUserPermanently(user_id)
        await self.broadcastEventMessage({
            'type': 'delete_user',
            'username': username,
            'user_info': None
        }, to_all=True)
        self.write("Success")

class UserModifyHandler(RequestHandlerBase):
    @authenticate(admin_required=True)
    async def post(self):
        
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
        
        new_max_storage = self.get_argument("max_storage", None)
        if new_max_storage is not None:
            await user.conn.updateUser(user_info['id'], max_storage=int(new_max_storage))
        
        _user_info_desens = await user.info_desensitized()
        await self.logger.info("User {} updated: {}".format(_user_info_desens["username"], _user_info_desens))

        await self.broadcastEventMessage({
            'type': 'update_user',
            'username': _user_info_desens["username"],
            'user_info': _user_info_desens
        }, to_all=True)
        
        self.write(json.dumps(_user_info_desens))