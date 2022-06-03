from __future__ import annotations
import sqlite3
import os
from typing import TypedDict, Dict, List, Optional
from .confReader import DISCUSSION_DB_PATH, logger_rbm

class DiscussLine(TypedDict):
    file_uid: str
    discuss_uid: str
    content: str
    time: str
    access_key_hex: str

DiscussSetInit_T = Dict[str, DiscussLine]   # indexed by file_uuid

class DiscussSet:
    """
    All discussions related to one file
    """
    logger = logger_rbm
    def __init__(self, database: DiscussDatabase, file_uid: str):
        ...

    def addDiscuss(self, content: str, access_key_hex: str):
        ...

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
        self._db_con.execute("""
                             CREATE TABLE IF NOT EXISTS discussion (
                                 file_uid text, 
                                 discuss_uid text PRIMARY KEY, 
                                 content text, 
                                 time float NOT NULL, 
                                 access_key_hex text NOT NULL
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
        ...

    def _delDiscuss(self, discuss_uid: str):
        """
        Will be called by DiscussSet.delDiscuss
        """
        ...
