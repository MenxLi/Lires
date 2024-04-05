from __future__ import annotations
import os
from typing import Optional

from .object import LiresUser, UsrDBConnection
from ..config import USER_DIR
from ..core.base import LiresBase

class UserPool(LiresBase):

    def __init__(self) -> None:
        super().__init__()
    
    async def init(self, user_dir: str = USER_DIR) -> UserPool:
        self._conn = await UsrDBConnection(user_dir).init()
        return self

    @property
    def conn(self) -> UsrDBConnection:
        return self._conn
    
    async def commit(self): await self.conn.commit()
    async def close(self): await self.conn.close()
    
    async def size(self) -> int:
        return len(await self.conn.getAllUserIDs())
    
    async def all(self) -> list[LiresUser]:
        all_ids = await self.conn.getAllUserIDs()
        return [LiresUser(self.conn, user_id) for user_id in all_ids]
    
    async def getUserByKey(self, key: str) -> Optional[LiresUser]:
        all_ids = await self.conn.getAllUserIDs()
        for user_id in all_ids:
            user = await self.getUserById(user_id)
            if user is None:
                continue
            if (await user.info())['enc_key'] == key:
                return user
        return None
    
    async def getUserByUsername(self, username: str) -> Optional[LiresUser]:
        try:
            user_id = (await self.conn.getUser(username))['id']
            return LiresUser(self.conn, user_id)
        except self.Error.LiresUserNotFoundError:
            return None
    
    async def getUserById(self, id: int) -> Optional[LiresUser]:
        try:
            await self.conn.getUser(id)
            return LiresUser(self.conn, id)
        except self.Error.LiresUserNotFoundError:
            return None
    
    async def deleteUserPermanently(self, query: int|str):
        """
        Permanently delete a user from the database.
        Please use with caution!
        """
        user: Optional[LiresUser] = None
        if isinstance(query, str):
            user = await self.getUserByUsername(query)
        elif isinstance(query, int):
            user = await self.getUserById(query)
        else:
            raise ValueError("Invalid query type")

        if user is None:
            raise self.Error.LiresUserNotFoundError(f"User {query} not found")
        
        # remove avatar image
        if user.avatar_image_path:
            __avatar_images = [user.avatar_image_path[k] for k in user.avatar_image_path]
            for pth in __avatar_images:
                if os.path.exists(pth):
                    os.remove(pth)

        await self.conn.deleteUser(query)
