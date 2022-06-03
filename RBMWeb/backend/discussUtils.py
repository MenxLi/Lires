from __future__ import annotations
import os, time, sqlite3
from typing import TypedDict, Dict, List, Optional
from uuid import uuid4
from .confReader import DISCUSSION_DB_PATH, logger_rbm

class DiscussLine(TypedDict):
    discuss_uid: str            # Uid for this single discussion
    file_uid: str               # File uid
    content: str                # Comment content
    time: float                 # Time added
    usr_name: str               # User name
    access_key_hex: str         # User access key (encrypted)

DiscussSetInit_T = Dict[str, DiscussLine]   # indexed by file_uuid

class DiscussSet:
    """
    All discussions related to one file
    """
    logger = logger_rbm
    def __init__(self, database: DiscussDatabase, file_uid: str):
        self.db = database
        self.file_uid = file_uid

    def addDiscuss(self, usr_name: str, access_key_hex: str, content: str):
        line: DiscussLine = {
            "discuss_uid": str(uuid4()),
            "file_uid": self.file_uid,
            "content": content,
            "time": time.time(),
            "usr_name": usr_name,
            "access_key_hex": access_key_hex
        }
        self.db._addDiscuss(line)

    def delDiscuss(self, discuss_uid: str):
        ...

class DiscussDatabase:
    logger = logger_rbm
    def __init__(self):
        if not os.path.exists(DISCUSSION_DB_PATH):
            self.logger.info("Created new discussion database: {}".format(DISCUSSION_DB_PATH))
        self._db_con = sqlite3.connect(DISCUSSION_DB_PATH)
        self.__createDiscussTable()

    @property
    def db_con(self) -> sqlite3.Connection:
        return self._db_con

    def __createDiscussTable(self):
        self.db_con.execute("""
                             CREATE TABLE IF NOT EXISTS discussion (
                                 discuss_uid TEXT PRIMARY KEY, 
                                 file_uid TEXT NOT NULL, 
                                 content TEXT NOT NULL, 
                                 time FLOAT NOT NULL, 
                                 usr_name TEXT NOT NULL,
                                 access_key_hex TEXT NOT NULL
                             );
                             """)

    def allDiscussion(self, file_uid: str) -> Optional[DiscussSet]:
        """
        Get all discussions related to one file
        """
        ...

    def __getitem__(self, discuss_uid: str) -> Optional[DiscussLine]:
        ...

    def _addDiscuss(self, line: DiscussLine):
        """
        Will be called by DiscussSet.addDiscuss
        """
        self.db_con.execute(
            """
            INSERT INTO discussion (
                discuss_uid, 
                file_uid,
                content,
                time,
                usr_name,
                access_key_hex
                )
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                line["discuss_uid"],
                line["file_uid"],
                line["content"],
                line["time"],
                line["usr_name"],
                line["access_key_hex"],
            ))
        self.db_con.commit()

    def _delDiscuss(self, discuss_uid: str):
        """
        Will be called by DiscussSet.delDiscuss
        """
        ...
