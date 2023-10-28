import os
import sqlite3
import json
from functools import wraps
from threading import Lock

from typing import TypedDict, Optional

from ..core import globalVar as G
from ..confReader import USER_DIR

# a wrapper that marks an object instance needs lock,
def lock_required(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        assert hasattr(self, "lock"), "The object does not have a lock attribute"
        with self.lock:
            return func(self, *args, **kwargs)
    return wrapper

class RawUser(TypedDict):
    id: int
    username: str
    password: str
    name: str
    is_admin: bool
    mandatory_tags: list[str]

class UsrDBConnection:
    logger = G.logger_lrs

    def __init__(self, db_dir: str = USER_DIR, fname: str = "user.db"):
        self.lock = Lock()
        self.db_path = os.path.join(db_dir, fname)
        if not os.path.exists(self.db_path):
            self.logger.info("Creating user database at: %s", self.db_path)

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.__maybeCreateTables()
    
    def close(self):
        self.conn.close()
    
    @lock_required
    def __maybeCreateTables(self):
        self.cursor.execute("""
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
        self.conn.commit()
    
    @lock_required
    def insertUser(self, 
                username: str, password: str, name: str,
                is_admin: bool, mandatory_tags: list[str]
                ) -> bool:
        # check if the user already exists
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        res = self.cursor.fetchone()
        if res is not None:
            return False
        # insert the user
        self.cursor.execute("""
                            INSERT INTO users 
                            (username, password, name, is_admin, mandatory_tags)
                            VALUES (?, ?, ?, ?, ?)
                            """, 
                            (username, password, name, is_admin, json.dumps(mandatory_tags)))
        self.conn.commit()
        return True
    
    @lock_required
    def deleteUser(self, query: str | int) -> bool:
        # check if the user exists
        if isinstance(query, str):
            self.cursor.execute("SELECT * FROM users WHERE username = ?", (query,))
        elif isinstance(query, int):
            self.cursor.execute("SELECT * FROM users WHERE id = ?", (query,))
        else: raise ValueError("Invalid query type")
        res = self.cursor.fetchone()
        if res is None:
            return False
        # delete the user
        if isinstance(query, int):
            self.cursor.execute("DELETE FROM users WHERE id = ?", (query,))
        else:
            self.cursor.execute("DELETE FROM users WHERE username = ?", (query,))
        self.conn.commit()
        return True
    
    @lock_required
    def updateUser(self, id_: int, **kwargs) -> bool:
        # check if the user exists
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (id_,))
        res = self.cursor.fetchone()
        if res is None:
            return False

        # update the user
        for k, v in kwargs.items():
            assert k in RawUser.__annotations__, f"Invalid user attribute: {k}"
            assert k != "id", "Cannot update user id"
            if k == "mandatory_tags":
                v = json.dumps(v)
            self.cursor.execute(f"UPDATE users SET {k} = ? WHERE id = ?", (v, id_))

        self.conn.commit()
        return True
    
    def getAllUserIDs(self) -> list[int]:
        self.cursor.execute("SELECT id FROM users")
        return [res[0] for res in self.cursor.fetchall()]
    
    def getUser(self, query: str | int) -> Optional[RawUser]:
        if isinstance(query, str):
            self.cursor.execute("SELECT * FROM users WHERE username = ?", (query,))
        elif isinstance(query, int):
            self.cursor.execute("SELECT * FROM users WHERE id = ?", (query,))
        else:
            raise ValueError("Invalid query type")
        res = self.cursor.fetchone()
        if res is None:
            return None
        return {
            "id": res[0],
            "username": res[1],
            "password": res[2],
            "name": res[3],
            "is_admin": bool(res[4]),
            "mandatory_tags": json.loads(res[5])
        }
