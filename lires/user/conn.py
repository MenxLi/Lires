import sqlite3
import os, json, time
from functools import wraps
from threading import Lock, Thread
from typing import TypedDict

from ..core.base import LiresBase

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
    password: str       # should be encrypted
    name: str
    is_admin: bool
    mandatory_tags: list[str]

class UsrDBConnection(LiresBase):
    logger = LiresBase.loggers().core

    def __init__(self, db_dir: str, fname: str = "user.db"):
        self.lock = Lock()
        self.db_path = os.path.join(db_dir, fname)
        if not os.path.exists(db_dir):
            os.mkdir(db_dir)
            self.logger.info("Creating user database directory at: %s", db_dir)
        if not os.path.exists(self.db_path):
            self.logger.info("Creating user database at: %s", self.db_path)

        # when check_same_thread=False, the connection can be used in multiple threads
        # however, we have to ensure that only one thread is doing writing at the same time
        # refer to: https://docs.python.org/3/library/sqlite3.html#sqlite3.connect
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.__modified = False
        self.__maybeCreateTables()

        self.__saving_thread = SavingThread(self, interval=10.0)
        self.__saving_thread.start()
    
    def close(self):
        self.conn.close()
    
    def setModifiedFlag(self, flag: bool):
        self.__modified = flag
    
    @lock_required
    def __maybeCreateTables(self):
        # check if the table exists
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        res = self.cursor.fetchone()
        if res is not None:
            return
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
        self.setModifiedFlag(True)
    
    @lock_required
    def insertUser(self, 
                username: str, password: str, name: str,
                is_admin: bool, mandatory_tags: list[str]
                ) -> None:
        # check if the user already exists
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        res = self.cursor.fetchone()
        if res is not None:
            raise self.Error.LiresUserDuplicationError(f"User {username} already exists")
        # insert the user
        self.cursor.execute("""
                            INSERT INTO users 
                            (username, password, name, is_admin, mandatory_tags)
                            VALUES (?, ?, ?, ?, ?)
                            """, 
                            (username, password, name, is_admin, json.dumps(mandatory_tags)))
        self.setModifiedFlag(True)
    
    @lock_required
    def deleteUser(self, query: str | int) -> None:
        # check if the user exists
        if isinstance(query, str):
            self.cursor.execute("SELECT * FROM users WHERE username = ?", (query,))
        elif isinstance(query, int):
            self.cursor.execute("SELECT * FROM users WHERE id = ?", (query,))
        else: raise ValueError("Invalid query type")
        res = self.cursor.fetchone()
        if res is None:
            raise self.Error.LiresUserNotFoundError(f"User {query} not found")
        # delete the user
        if isinstance(query, int):
            self.cursor.execute("DELETE FROM users WHERE id = ?", (query,))
        else:
            self.cursor.execute("DELETE FROM users WHERE username = ?", (query,))
        self.setModifiedFlag(True)
    
    @lock_required
    def updateUser(self, id_: int, **kwargs) -> None:
        # check if the user exists
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (id_,))
        res = self.cursor.fetchone()
        if res is None:
            raise self.Error.LiresUserNotFoundError(f"User {id_} not found")

        # update the user
        for k, v in kwargs.items():
            assert k in RawUser.__annotations__, f"Invalid user attribute: {k}"
            assert k != "id", "Cannot update user id"
            if k == "mandatory_tags":
                v = json.dumps(v)
            self.cursor.execute(f"UPDATE users SET {k} = ? WHERE id = ?", (v, id_))

        self.setModifiedFlag(True)
    
    def getAllUserIDs(self) -> list[int]:
        self.cursor.execute("SELECT id FROM users")
        return [res[0] for res in self.cursor.fetchall()]
    
    def getUser(self, query: str | int) -> RawUser:
        if isinstance(query, str):
            self.cursor.execute("SELECT * FROM users WHERE username = ?", (query,))
        elif isinstance(query, int):
            self.cursor.execute("SELECT * FROM users WHERE id = ?", (query,))
        else:
            raise ValueError("Invalid query type")
        res = self.cursor.fetchone()
        if res is None:
            raise self.Error.LiresUserNotFoundError(f"User {query} not found")
        return {
            "id": res[0],
            "username": res[1],
            "password": res[2],
            "name": res[3],
            "is_admin": bool(res[4]),
            "mandatory_tags": json.loads(res[5])
        }
    
    @lock_required
    def commit(self):
        if not self.__modified:
            return
        self.conn.commit()
        self.setModifiedFlag(False)
        self.logger.debug("Committed user database")


class SavingThread(Thread):
    def __init__(self, conn: UsrDBConnection, interval: float = 10.):
        super().__init__(daemon=True)
        self.conn = conn
        self.interval = interval
    
    def run(self):
        while True:
            self.conn.commit()
            time.sleep(self.interval)