"""
Sqlite server connection interface
"""
import json, os, threading, sqlite3, uuid
import typing
from typing import TypedDict, Optional
import dataclasses
import platform
from functools import wraps

from . import globalVar as G
from .utils import TimeUtils
from ..version import VERSION

@dataclasses.dataclass
class DocInfo:
    """
    This is a intermediate class for storing document information.
    The user is supposed to use FileManipulator to access those informations.
    """
    uuid: str
    time_import: float
    time_modify: float
    version_import: str
    version_modify: str
    device_import: str
    device_modify: str
    tags: list[str]
    url: str

    DocInfoDictT = typing.TypedDict("DocInfoDictT", {
        "uuid": str,            # maybe ommited in the future, duplicate with file key
        "time_import": float,
        "time_modify": float,
        "version_import": str,
        "version_modify": str,
        "device_import": str,
        "device_modify": str,
        "tags": list[str],
        "url": str,
    })

    @classmethod
    def fromString(cls, s: str):
        s_dict = json.loads(s)
        return cls(**s_dict)

    def toString(self) -> str:
        return json.dumps(self.toDict())
    
    def toDict(self) -> DocInfoDictT:
        return dataclasses.asdict(self)     # type: ignore

class DBFileInfo(TypedDict):
    uuid: str           # File uuid, should be unique for each file
    bibtex: str         # Bibtex string, should be valid and remove abstract, at least contains title, year, authors
    abstract: str       # Abstract, markdown
    comments: str       # Note markdown
    info_str: str       # Info string, json serializable string of DocInfo
    doc_ext: str        # Document file type, e.g. '.pdf', '.docx'

# a wrapper that marks an object instance needs lock,
def lock_required(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        assert hasattr(self, "lock"), "The object does not have a lock attribute"
        with self.lock:
            return func(self, *args, **kwargs)
    return wrapper
class DBConnection:
    """
    to manage database connection
    """
    logger = G.logger_rbm
    db_fname = "rbm.db"
    lock = threading.Lock()

    def __init__(self, db_dir: str) -> None:
        # create db if not exist
        db_path = os.path.join(db_dir, self.db_fname)
        if not os.path.exists(db_dir):
            self.logger.info("Created new database directory: {}".format(db_dir))
            os.mkdir(db_dir)
        if not os.path.exists(db_path):
            self.logger.info("Created new database: {}".format(db_path))

        self.db_dir = db_dir
        self.db_path = db_path
        self.init()
    
    def init(self):
        """
        May call this function to re-init the connection after close
        """
        # when check_same_thread=False, the connection can be used in multiple threads
        # however, we have to ensure that only one thread is doing writing at the same time
        # refer to: https://docs.python.org/3/library/sqlite3.html#sqlite3.connect
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.__maybeCreateTable()
    
    def __maybeCreateTable(self):
        """
        Create table if not exist
        """
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            uuid TEXT PRIMARY KEY,
            bibtex TEXT NOT NULL,
            abstract TEXT NOT NULL,
            comments TEXT NOT NULL,
            info_str TEXT NOT NULL,
            doc_ext TEXT NOT NULL,
            misc_dir TEXT
        )
        """)
        self.conn.commit()
    
    def close(self):
        self.conn.close()
    
    @lock_required
    def __getitem__(self, uuid: str) -> Optional[DBFileInfo]:
        """
        Get file info by uuid
        """
        self.cursor.execute("SELECT * FROM files WHERE uuid=?", (uuid,))
        row = self.cursor.fetchone()
        if row is None:
            return None
        return {
            "uuid": row[0],
            "bibtex": row[1],
            "abstract": row[2],
            "comments": row[3],
            "info_str": row[4],
            "doc_ext": row[5],
        }
    
    def insertItem(self, item: DBFileInfo) -> bool:
        """
        Insert item into database, will overwrite if uuid already exists
        """
        if self[item["uuid"]] is not None:
            # if uuid already exists, delete it first
            self.cursor.execute("DELETE FROM files WHERE uuid=?", (item["uuid"],))
        with self.lock:
            self.cursor.execute("INSERT INTO files VALUES (?,?,?,?,?,?,?)", (
                item["uuid"], item["bibtex"], item["abstract"], item["comments"], item["info_str"], item["doc_ext"], None
            ))
            self.conn.commit()
        return True
    
    @lock_required
    def keys(self) -> list[str]:
        """
        Return all uuids
        """
        self.cursor.execute("SELECT uuid FROM files")
        return [row[0] for row in self.cursor.fetchall()]
    
    def _ensureExist(self, uuid: str) -> bool:
        if self[uuid] is None:
            self.logger.error("uuid {} not exists".format(uuid))
            return False
        return True
    
    def addEntry(
            self, bibtex: str, 
            abstract: str = "", 
            comments: str = "", 
            doc_ext: str = "",
            doc_info: Optional[DocInfo] = None
            ) -> Optional[str]:
        """
        Add an entry to the database
        DocInfo will be generated if not provided, should be None for new data generated,
            can be provided for data imported from other sources (e.g. old version)
        return uuid if success, None if failed
        """
        # generate info
        if doc_info is None:
            doc_info = DocInfo(
                uuid = str(uuid.uuid4()),
                time_import = TimeUtils.nowStamp(),
                time_modify = TimeUtils.nowStamp(),
                version_import = VERSION,
                version_modify = VERSION,
                device_import = platform.node(),
                device_modify = platform.node(),
                tags = [],
                url = ""
            )
        uid = doc_info.uuid
        # check if uuid already exists
        if self[uid] is not None:
            self.logger.error("uuid {} already exists".format(uid))
            return None
        # insert
        with self.lock:
            self.cursor.execute("INSERT INTO files VALUES (?,?,?,?,?,?,?)", (
                uid, bibtex, abstract, comments, doc_info.toString(), doc_ext, None
            ))
            self.conn.commit()
        return uid
    
    def removeEntry(self, uuid: str) -> bool:
        if not self._ensureExist(uuid): return False
        with self.lock:
            self.cursor.execute("DELETE FROM files WHERE uuid=?", (uuid,))
            self.conn.commit()
        self.logger.debug("Removed entry {}".format(uuid))
        return True
    
    def setDocExt(self, uuid: str, ext: Optional[str]) -> bool:
        if not self._ensureExist(uuid): return False
        with self.lock:
            self.cursor.execute("UPDATE files SET doc_ext=? WHERE uuid=?", (ext, uuid))
            self.conn.commit()
        return True
    
    def updateInfo(self, uuid: str, info: DocInfo) -> bool:
        if not self._ensureExist(uuid): return False
        with self.lock:
            self.cursor.execute("UPDATE files SET info_str=? WHERE uuid=?", (info.toString(), uuid))
            self.conn.commit()
        return True
    
    def updateBibtex(self, uuid: str, bibtex: str) -> bool:
        if not self._ensureExist(uuid): return False
        with self.lock:
            self.cursor.execute("UPDATE files SET bibtex=? WHERE uuid=?", (bibtex, uuid))
            self.conn.commit()
        return True
    
    def updateComments(self, uuid: str, comments: str) -> bool:
        if not self._ensureExist(uuid): return False
        with self.lock:
            self.cursor.execute("UPDATE files SET comments=? WHERE uuid=?", (comments, uuid))
            self.conn.commit()
        return True
    
    def printData(self, uuid: str):
        if not self._ensureExist(uuid): return False
        with self.lock:
            self.cursor.execute("SELECT * FROM files WHERE uuid=?", (uuid,))
            row = self.cursor.fetchone()
        print(row)

