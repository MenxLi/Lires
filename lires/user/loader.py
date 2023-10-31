
from .object import LiresUser, UsrDBConnection
from typing import Optional, Sequence
from ..confReader import USER_DIR

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
        for user in self:
            if user.raw['username'] == username:
                return user
        return None
