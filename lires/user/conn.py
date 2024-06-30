from __future__ import annotations
import aiosqlite
import os, json
from typing import TypedDict, Optional

from ..core.base import LiresBase
from lires.config import getConf

class RawUser(TypedDict):
    id: int
    username: str
    password: str       # should be encrypted
    name: str
    is_admin: bool
    mandatory_tags: list[str]
    time_created: str
    max_storage: int
    last_active: float

class InvitationRecord(TypedDict):
    id: int
    code: str
    created_by: int
    max_uses: int
    uses: int
    accessibility: dict
    time_created: str

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
        await self.__autoUpgrade()
        return self

    async def close(self):
        await self.conn.close()
    
    def setModifiedFlag(self, flag: bool):
        self.__modified = flag
    
    async def __autoUpgrade(self):
        """ Upgrade the database automatically """
        # since v1.7.1, add max_storage column
        # since v1.8.1, add last_active column
        async with self.conn.execute("PRAGMA table_info(users)") as cursor:
            res = await cursor.fetchall()
            if len(res) == 7 and res[-1][1] != "max_storage":   # type: ignore
                print("Upgrading user database to v1.7.1")
                # default to 100MB
                await self.conn.execute("ALTER TABLE users ADD COLUMN max_storage INTEGER NOT NULL DEFAULT 104857600")
                self.setModifiedFlag(True)
            if len(res) == 8 and res[-1][1] != "last_active":   # type: ignore
                print("Upgrading user database to v1.8.1")
                await self.conn.execute("ALTER TABLE users ADD COLUMN last_active FLOAT NOT NULL DEFAULT 0")
                self.setModifiedFlag(True)
    
    async def __maybeCreateTables(self):
        async def createUserTable():
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
                    time_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    max_storage INTEGER NOT NULL DEFAULT 104857600, 
                    last_active FLOAT NOT NULL DEFAULT 0
                );
            """)
            self.setModifiedFlag(True)
        
        async def createInvitationTable():
            async with self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='invitations'") as cursor:
                res = await cursor.fetchone()
            if res is not None:
                return
            await self.conn.execute("""
                CREATE TABLE IF NOT EXISTS invitations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL,
                    created_by INTEGER NOT NULL,
                    max_uses INTEGER NOT NULL,
                    uses INTEGER NOT NULL DEFAULT 0,
                    accessibility STRING NOT NULL DEFAULT '',
                    time_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)
            self.setModifiedFlag(True)
        
        await createUserTable()
        await createInvitationTable()
    
    async def count(self) -> int:
        async with self.conn.execute("SELECT COUNT(*) FROM users") as cursor:
            res = await cursor.fetchone()
        assert res is not None
        return res[0]

    async def insertUser(self, 
                username: str, password: str, name: str,
                is_admin: bool, mandatory_tags: list[str], 
                max_storage: Optional[int] = None,
                ) -> None:
        # check if the user already exists
        async with self.conn.execute("SELECT * FROM users WHERE username = ?", (username,)) as cursor:
            res = await cursor.fetchone()
            if res is not None:
                raise self.Error.LiresUserDuplicationError(f"User {username} already exists")
        # check if limit is reached
        config = getConf()
        max_users = config["max_users"]
        if max_users != 0:
            if (await self.count()) >= max_users:
                raise self.Error.LiresExceedLimitError(f"Exceed maximum number of users: {max_users}")

        if max_storage is None:
            def parseStorage(s: str) -> int:
                if s[-1].lower() == "m":
                    return int(s[:-1]) * 1024 * 1024
                if s[-1].lower() == "g":
                    return int(s[:-1]) * 1024 * 1024 * 1024
                if s[-1].lower() == "t":
                    return int(s[:-1]) * 1024 * 1024 * 1024 * 1024
                return int(s)
            max_storage = parseStorage(config["default_user_max_storage"])
            
        # insert the user
        await self.conn.execute("""
                            INSERT INTO users 
                            (username, password, name, is_admin, mandatory_tags, max_storage, last_active)
                            VALUES (?, ?, ?, ?, ?, ?, 0)
                            """,
                            (username, password, name, is_admin, json.dumps(mandatory_tags), max_storage)
                            )
        self.setModifiedFlag(True)
        await self.logger.debug(f"[UserDBConn] User {username} created")
    
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
            "mandatory_tags": json.loads(res[5]),
            "time_created": res[6],
            "max_storage": res[7], 
            "last_active": res[8]
        }
    
    async def listInvitations(self) -> list[InvitationRecord]:
        async with self.conn.execute("SELECT * FROM invitations") as cursor:
            res = await cursor.fetchall()
        return [{
            "id": i[0],
            "code": i[1],
            "created_by": i[2],
            "max_uses": i[3],
            "uses": i[4],
            "accessibility": json.loads(i[5]),
            "time_created": i[6]
        } for i in res]
    
    async def queryInvitation(self, code: str) -> Optional[InvitationRecord]:
        async with self.conn.execute("SELECT * FROM invitations WHERE code = ?", (code,)) as cursor:
            res = await cursor.fetchone()
        return {
            "id": res[0],
            "code": res[1],
            "created_by": res[2],
            "max_uses": res[3],
            "uses": res[4],
            "accessibility": json.loads(res[5]),
            "time_created": res[6]
        } if res is not None else None
    
    async def createInvitation(self, code: str, created_by: int, max_uses: int, accesibility = {}) -> None:
        async with self.conn.execute("SELECT * FROM invitations WHERE code = ?", (code,)) as cursor:
            res = await cursor.fetchone()
            if res is not None:
                raise self.Error.LiresDuplicateError(f"Invitation {code} already exists")
        await self.conn.execute("INSERT INTO invitations (code, created_by, max_uses, accessibility) VALUES (?, ?, ?, ?)", (code, created_by, max_uses, json.dumps(accesibility)))
        await self.logger.debug("Invitation %s created", code)
        self.setModifiedFlag(True)
    
    async def useInvitation(self, code: str) -> None:
        record = await self.queryInvitation(code)
        if record is None:
            raise self.Error.LiresEntryNotFoundError(f"Invitation {code} not found")
        if record["uses"] >= record["max_uses"]:
            raise self.Error.LiresEntryNotFoundError(f"Invitation {code} has been used up")
        await self.conn.execute("UPDATE invitations SET uses = uses + 1 WHERE code = ?", (code,))
        await self.logger.debug("Invitation %s used", code)
        self.setModifiedFlag(True)
    
    async def deleteInvitation(self, code: str) -> None:
        async with self.conn.execute("SELECT * FROM invitations WHERE code = ?", (code,)) as cursor:
            res = await cursor.fetchone()
            if res is None:
                raise self.Error.LiresEntryNotFoundError(f"Invitation {code} not found")
        await self.conn.execute("DELETE FROM invitations WHERE code = ?", (code,))
        await self.logger.debug("Invitation %s deleted", code)
        self.setModifiedFlag(True)
    
    async def commit(self):
        if not self.__modified:
            return
        await self.conn.commit()
        self.setModifiedFlag(False)
