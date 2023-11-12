
import os
from typing import Optional, Sequence

from .object import LiresUser, UsrDBConnection
from ..confReader import USER_DIR
from ..core.customError import *

class UserPool(Sequence[LiresUser]):

    def __init__(self, user_dir: str = USER_DIR) -> None:
        super().__init__()
        self._conn = UsrDBConnection(user_dir)

    @property
    def conn(self) -> UsrDBConnection:
        return self._conn
    
    def __len__(self) -> int:
        return len(self._conn.getAllUserIDs())
    
    def __getitem__(self, index: int) -> LiresUser:
        return LiresUser(self.conn, self.conn.getAllUserIDs()[index])
    
    def __iter__(self):
        for id in self.conn.getAllUserIDs():
            yield LiresUser(self.conn, id)
    
    def __contains__(self, item: LiresUser) -> bool:
        user_id = item.raw['id']
        if user_id in self.conn.getAllUserIDs():
            if item.raw == self.conn.getUser(user_id):
                return True
        return False
    
    def destroy(self):
        self.conn.close()
        del self._conn
        del self

    def getUserByKey(self, key: str) -> Optional[LiresUser]:
        for user in self:
            if user.info()['enc_key'] == key:
                return user
        return None
    
    def getUserByUsername(self, username: str) -> Optional[LiresUser]:
        try:
            user_id = self.conn.getUser(username)['id']
            return LiresUser(self.conn, user_id)
        except LiresUserNotFoundError:
            return None
    
    def getUserById(self, id: int) -> Optional[LiresUser]:
        try:
            self.conn.getUser(id)
            return LiresUser(self.conn, id)
        except LiresUserNotFoundError:
            return None
    
    def deleteUser(self, query: int|str):
        user: Optional[LiresUser] = None
        if isinstance(query, str):
            user = self.getUserByUsername(query)
        elif isinstance(query, int):
            user = self.getUserById(query)
        else:
            raise ValueError("Invalid query type")

        if user is None:
            raise LiresUserNotFoundError(f"User {query} not found")
        
        # remove avatar image
        if user.avatar_image_path:
            for k in user.avatar_image_path:
                if os.path.exists(user.avatar_image_path[k]):
                    os.remove(user.avatar_image_path[k])

        self.conn.deleteUser(query)
