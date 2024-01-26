"""
Sqlite connection interface
"""
from __future__ import annotations
import json, os, threading, sqlite3, uuid, asyncio
import typing
from typing import TypedDict, Optional
import dataclasses
import platform

from .base import LiresBase
from ..utils import TimeUtils
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

class DBConnection(LiresBase):
    """
    to manage database connection
    """
    logger = LiresBase.loggers().core
    lock = threading.Lock()

    def __init__(self, db_dir: str, fname: str = "lrs.db") -> None:
        # create db if not exist
        self.db_fname = fname
        db_path = os.path.join(db_dir, self.db_fname)
        if not os.path.exists(db_dir):
            os.mkdir(db_dir)
        if not os.path.exists(db_path):
            ...

        self.db_dir = db_dir
        self.db_path = db_path

        self.__modified = False
        self.__saving_thread = SavingThread(self, save_interval=10.0)
    
    async def init(self) -> DBConnection:
        """
        May call this function to re-init the connection after close
        """
        # when check_same_thread=False, the connection can be used in multiple threads
        # however, we have to ensure that only one thread is doing writing at the same time
        # refer to: https://docs.python.org/3/library/sqlite3.html#sqlite3.connect
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.__maybeCreateTable()
        self.__saving_thread.start()
        return self
    
    def isInitialized(self) -> bool:
        try:
            if self.conn is None:
                return False
            return True
        except AttributeError:
            return False
    
    def setModifiedFlag(self, modified: bool):
        self.__modified = modified
    
    def __maybeCreateTable(self):
        """
        Create table if not exist
        """
        # check if table exists
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='files'")
        if not self.cursor.fetchone():
            with self.lock:
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
                self.setModifiedFlag(True)
    
    async def close(self):
        await self.commit()
        self.conn.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()
    
    def __formatRow(self, row: tuple) -> DBFileInfo:
        return {
            "uuid": row[0],
            "bibtex": row[1],
            "abstract": row[2],
            "comments": row[3],
            "info_str": row[4],
            "doc_ext": row[5],
        }
    
    async def get(self, uuid: str) -> Optional[DBFileInfo]:
        """
        Get file info by uuid
        """
        self.cursor.execute("SELECT * FROM files WHERE uuid=?", (uuid,))
        row = self.cursor.fetchone()
        if row is None:
            return None
        return self.__formatRow(row)
    
    async def getMany(self, uuids: list[str]) -> list[DBFileInfo]:
        """
        Get file info by uuid
        """
        self.cursor.execute("SELECT * FROM files WHERE uuid IN ({})".format(",".join(["?"]*len(uuids))), uuids)
        rows = self.cursor.fetchall()
        if len(rows) != len(uuids):
            raise ValueError("Some uuids not found")
        ret = [self.__formatRow(row) for row in rows]
        return ret
    
    async def insertItem(self, item: DBFileInfo) -> bool:
        """
        Insert item into database, will overwrite if uuid already exists
        """
        await self.logger.debug("(db_conn) Inserting item {}".format(item["uuid"]))
        if await self.get(item["uuid"]) is not None:
            # if uuid already exists, delete it first
            self.cursor.execute("DELETE FROM files WHERE uuid=?", (item["uuid"],))
        with self.lock:
            self.cursor.execute("INSERT INTO files VALUES (?,?,?,?,?,?,?)", (
                item["uuid"], item["bibtex"], item["abstract"], item["comments"], item["info_str"], item["doc_ext"], None
            ))
            self.setModifiedFlag(True)
        return True
    
    async def keys(self) -> list[str]:
        """
        Return all uuids
        """
        self.cursor.execute("SELECT uuid FROM files")
        return [row[0] for row in self.cursor.fetchall()]
    
    async def _ensureExist(self, uuid: str) -> bool:
        if await self.get(uuid) is None:
            await self.logger.error("uuid {} not exists".format(uuid))
            return False
        return True
    
    async def addEntry(
            self, bibtex: str, 
            abstract: str = "", 
            comments: str = "", 
            doc_ext: str = "",
            doc_info: Optional[DocInfo | dict] = None
            ) -> Optional[str]:
        """
        Add an entry to the database
        DocInfo will be generated if not provided, should be None for new data generated,
            can be provided for data imported from other sources (e.g. old version),
            or a dict that contains partial information (will be merged with generated default info)
        return uuid if success, None if failed
        """
        # generate info
        doc_info_default = DocInfo(
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
        if doc_info is None:
            doc_info = doc_info_default
        elif isinstance(doc_info, dict):
            docinfo_dict = doc_info_default.toDict()
            docinfo_dict.update(doc_info)   # type: ignore
            # check if all keys are valid
            for key in docinfo_dict.keys():
                if key not in doc_info_default.__annotations__:
                    await self.logger.error("Invalid key {} in doc_info".format(key))
                    return None
            doc_info = DocInfo(**docinfo_dict)
        else:
            assert isinstance(doc_info, DocInfo)
            
        uid = doc_info.uuid
        # check if uuid already exists
        if await self.get(uid) is not None:
            await self.logger.error("uuid {} already exists".format(uid))
            return None
        # insert
        await self.logger.debug("(db_conn) Adding entry {}".format(uid))
        with self.lock:
            self.cursor.execute("INSERT INTO files VALUES (?,?,?,?,?,?,?)", (
                uid, bibtex, abstract, comments, doc_info.toString(), doc_ext, None
            ))
            self.setModifiedFlag(True)
        return uid
    
    async def removeEntry(self, uuid: str) -> bool:
        if not await self._ensureExist(uuid): return False
        await self.logger.debug("(db_conn) Removing entry {}".format(uuid))
        with self.lock:
            self.cursor.execute("DELETE FROM files WHERE uuid=?", (uuid,))
            self.setModifiedFlag(True)
        await self.logger.debug("Removed entry {}".format(uuid))
        return True
    
    async def setDocExt(self, uuid: str, ext: Optional[str]) -> bool:
        if not await self._ensureExist(uuid): return False
        await self.logger.debug("(db_conn) Setting doc_ext for {} to {}".format(uuid, ext))
        with self.lock:
            self.cursor.execute("UPDATE files SET doc_ext=? WHERE uuid=?", (ext, uuid))
            self.setModifiedFlag(True)
        return True
    
    async def updateInfo(self, uuid: str, info: DocInfo) -> bool:
        if not await self._ensureExist(uuid): return False
        await self.logger.debug("(db_conn) Updating info for {} - {}".format(uuid, info))
        with self.lock:
            self.cursor.execute("UPDATE files SET info_str=? WHERE uuid=?", (info.toString(), uuid))
            self.setModifiedFlag(True)
        return True
    
    async def updateBibtex(self, uuid: str, bibtex: str) -> bool:
        if not await self._ensureExist(uuid): return False
        await self.logger.debug("(db_conn) Updating bibtex for {}".format(uuid))
        with self.lock:
            self.cursor.execute("UPDATE files SET bibtex=? WHERE uuid=?", (bibtex, uuid))
            self.setModifiedFlag(True)
        return True
    
    async def updateComments(self, uuid: str, comments: str) -> bool:
        if not await self._ensureExist(uuid): return False
        # await self.logger.debug("(db_conn) Updating comments for {}".format(uuid))   # too verbose
        with self.lock:
            self.cursor.execute("UPDATE files SET comments=? WHERE uuid=?", (comments, uuid))
            self.setModifiedFlag(True)
        return True
    
    async def updateAbstract(self, uuid: str, abstract: str) -> bool:
        if not await self._ensureExist(uuid): return False
        # await self.logger.debug("(db_conn) Updating abstract for {}".format(uuid))   # too verbose
        with self.lock:
            self.cursor.execute("UPDATE files SET abstract=? WHERE uuid=?", (abstract, uuid))
            self.setModifiedFlag(True)
        return True
    
    async def commit(self):
        if not self.__modified: return
        with self.lock:
            self.conn.commit()
            self.setModifiedFlag(False)
        await self.logger.debug("Committed document database")
    
    async def printData(self, uuid: str):
        if not await self._ensureExist(uuid): return False
        with self.lock:
            self.cursor.execute("SELECT * FROM files WHERE uuid=?", (uuid,))
            row = self.cursor.fetchone()
        print(row)


class SavingThread(threading.Thread):
    """
    A thread that save the database periodically
    """
    def __init__(self, db_conn: DBConnection, save_interval: float = 10.0):
        super().__init__(daemon=True)
        self.db_conn = db_conn
        self.save_interval = save_interval
    
    def run(self):
        import time
        async def _commit():
            await asyncio.sleep(self.save_interval)
            await self.db_conn.commit()
        # TODO: register to main loop instead of using threading
        while True:
            try:
                loop = asyncio.get_running_loop()
                loop.call_later(0, asyncio.create_task, _commit())
            except RuntimeError:
                loop = asyncio.new_event_loop()
                loop.call_later(0, asyncio.create_task, _commit())
                loop.run_forever()