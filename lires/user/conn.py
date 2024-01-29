from __future__ import annotations
import aiosqlite
import os, json
from typing import TypedDict

from ..core.base import LiresBase

class RawUser(TypedDict):
    id: int
    username: str
    password: str       # should be encrypted
    name: str
    is_admin: bool
    mandatory_tags: list[str]

class UsrDBConnection(LiresBase):
    logger = LiresBase.loggers().core

    def __init__(self, db_dir: str, fname: str = "user.db"):
        self.db_path = os.path.join(db_dir, fname)
        if not os.path.exists(db_dir):
            os.mkdir(db_dir)
        if not os.path.exists(self.db_path):
            ...
    
    async def init(self) -> UsrDBConnection:
        self.conn = await aiosqlite.connect(self.db_path)
        self.__modified = False
        await self.__maybeCreateTables()
        return self

    async def close(self):
        await self.conn.close()
    
    def setModifiedFlag(self, flag: bool):
        self.__modified = flag
    
    async def __maybeCreateTables(self):
        # check if the table exists
        async with self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'") as cursor:
            res = await cursor.fetchone()
        if res is not None:
            return
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                is_admin BOOLEAN NOT NULL,
                mandatory_tags TEXT NOT NULL, 
                time_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        # TODO: Add more user-related tables
        # ...
        self.setModifiedFlag(True)
    
    async def insertUser(self, 
                username: str, password: str, name: str,
                is_admin: bool, mandatory_tags: list[str]
                ) -> None:
        # check if the user already exists
        async with self.conn.execute("SELECT * FROM users WHERE username = ?", (username,)) as cursor:
            res = await cursor.fetchone()
            if res is not None:
                raise self.Error.LiresUserDuplicationError(f"User {username} already exists")
        # insert the user
        await self.conn.execute("""
                            INSERT INTO users 
                            (username, password, name, is_admin, mandatory_tags)
                            VALUES (?, ?, ?, ?, ?)
                            """, 
                            (username, password, name, is_admin, json.dumps(mandatory_tags)))
        self.setModifiedFlag(True)
    
    async def __ensureUserExists(self, query: str | int) -> aiosqlite.Row:
        if isinstance(query, str):
            async with self.conn.execute("SELECT * FROM users WHERE username = ?", (query,)) as cursor:
                res = await cursor.fetchone()
        elif isinstance(query, int):
            async with self.conn.execute("SELECT * FROM users WHERE id = ?", (query,)) as cursor:
                res = await cursor.fetchone()
        else: raise ValueError("Invalid query type")
        if res is None:
            raise self.Error.LiresUserNotFoundError(f"User {query} not found")
        return res
    
    async def deleteUser(self, query: str | int) -> None:
        await self.__ensureUserExists(query)
        # delete the user
        if isinstance(query, int):
            await self.conn.execute("DELETE FROM users WHERE id = ?", (query,))
        else:
            await self.conn.execute("DELETE FROM users WHERE username = ?", (query,))
        self.setModifiedFlag(True)
    
    async def updateUser(self, id_: int, **kwargs) -> None:
        # check if the user exists
        async with self.conn.execute("SELECT * FROM users WHERE id = ?", (id_,)) as cursor:
            res = await cursor.fetchone()
            if res is None:
                raise self.Error.LiresUserNotFoundError(f"User {id_} not found")

        # update the user
        for k, v in kwargs.items():
            assert k in RawUser.__annotations__, f"Invalid user attribute: {k}"
            assert k != "id", "Cannot update user id"
            if k == "mandatory_tags":
                v = json.dumps(v)
            await self.conn.execute(f"UPDATE users SET {k} = ? WHERE id = ?", (v, id_))

        self.setModifiedFlag(True)
    
    async def getAllUserIDs(self) -> list[int]:
        async with self.conn.execute("SELECT id FROM users") as cursor:
            res = await cursor.fetchall()
        return [i[0] for i in res]
    
    async def getUser(self, query: str | int) -> RawUser:
        res = await self.__ensureUserExists(query)
        return {
            "id": res[0],
            "username": res[1],
            "password": res[2],
            "name": res[3],
            "is_admin": bool(res[4]),
            "mandatory_tags": json.loads(res[5])
        }
    
    async def commit(self):
        if not self.__modified:
            return
        await self.conn.commit()
        self.setModifiedFlag(False)
        print("User database saved")
