from __future__ import annotations
import os, time, sqlite3
from typing import TypedDict, Dict, List, Optional
from uuid import uuid4
from lires.core.utils import TimeUtils
from ._config import DISCUSSION_DB_PATH, logger_rbm

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
        self.discuss_lines: List[DiscussLine] = self.db.discussions(file_uid)

    def addDiscuss(self, usr_name: str, access_key_hex: str, content: str):
        line: DiscussLine = {
            "discuss_uid": str(uuid4()),
            "file_uid": self.file_uid,
            "content": content,
            "time": TimeUtils.nowStamp(),
            "usr_name": usr_name,
            "access_key_hex": access_key_hex
        }
        self.db._addDiscuss(line)
        self.discuss_lines.append(line)

    def delDiscuss(self, discuss_uid: str):
        for i in range(len(self.discuss_lines)):
            line = self.discuss_lines[i]
            if line["discuss_uid"] == discuss_uid:
                self.db.delDiscuss(discuss_uid)
                self.discuss_lines.pop(i)
                break
        return

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

    def discussions(self, file_uid: str) -> List[DiscussLine]:
        """
        Get all discussions related to one file
        """
        lines = self.db_con.execute(
            """
            SELECT 
                discuss_uid, 
                file_uid, 
                content, 
                time, 
                usr_name, 
                access_key_hex
            FROM discussion WHERE file_uid=?
            """, (file_uid, )
        ).fetchall()

        out = []
        for l_ in lines:
            line: DiscussLine = {
                "discuss_uid": l_[0],
                "file_uid": l_[1],
                "content": l_[2],
                "time": l_[3],
                "usr_name": l_[4],
                "access_key_hex": l_[5],
            }
            out.append(line)
        return out

    def __getitem__(self, discuss_uid: str) -> Optional[DiscussLine]:
        selection = self.db_con.execute(
            """
            SELECT 
                discuss_uid, 
                file_uid, 
                content, 
                time, 
                usr_name, 
                access_key_hex
            FROM discussion WHERE discuss_uid=?
            """, (discuss_uid, )
        ).fetchall()
        if not selection:    # []
            return None
        line_raw = selection[0]
        line: DiscussLine = {
            "discuss_uid": line_raw[0],
            "file_uid": line_raw[1],
            "content": line_raw[2],
            "time": line_raw[3],
            "usr_name": line_raw[4],
            "access_key_hex": line_raw[5],
        }
        return line

    def addDiscuss(self, 
                   file_uid: str, 
                   usr_name: str, 
                   access_key_hex: str, 
                   content: str):
        line: DiscussLine = {
            "discuss_uid": str(uuid4()),
            "file_uid": file_uid,
            "content": content,
            "time": TimeUtils.nowStamp(),
            "usr_name": usr_name,
            "access_key_hex": access_key_hex
        }
        self._addDiscuss(line)
        self.logger.info("Add new discussion comment: {}".format(line["discuss_uid"]))

    def _addDiscuss(self, line: DiscussLine):
        """
        Will be called by self.addDiscuss
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

    def delDiscuss(self, discuss_uid: str):
        """
        Will be called by DiscussSet.delDiscuss
        """
        self.db_con.execute(
            """
            DELETE FROM discussion WHERE discuss_uid=?
            """, (discuss_uid, ))
        self.db_con.commit()

    def delDiscussAll(self, file_uid: str):
        """
        Delete all discussions for a file
        Should be called by the server when delete DataPoint
        """
        self.db_con.execute(
            """
            DELETE FROM discussion WHERE file_uid=?
            """, (file_uid, ))
        self.db_con.commit()

def showDiscuss(line: DiscussLine):
    """
    String representation of a line
    """
    time_ = TimeUtils.stamp2Local(line["time"])
    s = "{} ({}): {} \n [d:{}|f:{}]".format(
            line["usr_name"], time_, line["content"], line["discuss_uid"], line["file_uid"]
    )
    return s
