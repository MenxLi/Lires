"""
A back up of the old sqlite connection interface, changed in 1.5.0
Sqlite connection interface
"""
from __future__ import annotations
import json, os, uuid
import typing
from typing import TypedDict, Optional, TYPE_CHECKING
import dataclasses
import platform
import aiosqlite

from .base import LiresBase
from ..utils import TimeUtils
from ..version import VERSION

if TYPE_CHECKING:
    from ..types.dataT import FileTypeT

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
    doc_ext: FileTypeT  # Document file type

class DBConnection(LiresBase):
    """
    to manage database connection
    """
    logger = LiresBase.loggers().core

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
    
    async def init(self) -> DBConnection:
        """
        May call this function to re-init the connection after close
        """
        self.conn = await aiosqlite.connect(self.db_path)
        await self.__maybeCreateTable()
        return self
    
    async def isInitialized(self) -> bool:
        try:
            if self.conn is None:
                return False
            return True
        except AttributeError:
            return False
    
    async def setModifiedFlag(self, modified: bool):
        self.__modified = modified
    
    async def __maybeCreateTable(self):
        """
        Create table if not exist
        """
        # check if table exists
        async with self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='files'") as cursor:
            if not await cursor.fetchone():
                await cursor.execute("""
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
                await self.setModifiedFlag(True)
    
    async def close(self):
        await self.commit()
        await self.conn.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    
    def __formatRow(self, row: tuple | aiosqlite.Row) -> DBFileInfo:
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
        # self.cursor.execute("SELECT * FROM files WHERE uuid=?", (uuid,))
        # row = self.cursor.fetchone()

        async with self.conn.execute("SELECT * FROM files WHERE uuid=?", (uuid,)) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
        return self.__formatRow(row)
    
    async def getMany(self, uuids: list[str]) -> list[DBFileInfo]:
        """
        Get file info by uuid
        """
        # self.cursor.execute("SELECT * FROM files WHERE uuid IN ({})".format(",".join(["?"]*len(uuids))), uuids)
        # rows = self.cursor.fetchall()

        async with self.conn.execute("SELECT * FROM files WHERE uuid IN ({})".format(",".join(["?"]*len(uuids))), uuids) as cursor:
            rows = await cursor.fetchall()
        if len(list(rows)) != len(uuids):
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
            await self.conn.execute("DELETE FROM files WHERE uuid=?", (item["uuid"],))
        await self.conn.execute("INSERT INTO files VALUES (?,?,?,?,?,?,?)", (
            item["uuid"], item["bibtex"], item["abstract"], item["comments"], item["info_str"], item["doc_ext"], None
        ))
        await self.setModifiedFlag(True)
        return True
    
    async def keys(self) -> list[str]:
        """
        Return all uuids
        """
        async with self.conn.execute("SELECT uuid FROM files") as cursor:
            return [row[0] for row in await cursor.fetchall()]
    
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
        await self.conn.execute("INSERT INTO files VALUES (?,?,?,?,?,?,?)", (
            uid, bibtex, abstract, comments, doc_info.toString(), doc_ext, None
        ))
        await self.setModifiedFlag(True)
        return uid
    
    async def removeEntry(self, uuid: str) -> bool:
        if not await self._ensureExist(uuid): return False
        await self.logger.debug("(db_conn) Removing entry {}".format(uuid))
        await self.conn.execute("DELETE FROM files WHERE uuid=?", (uuid,))
        await self.setModifiedFlag(True)
        await self.logger.debug("Removed entry {}".format(uuid))
        return True
    
    async def setDocExt(self, uuid: str, ext: Optional[str]) -> bool:
        if not await self._ensureExist(uuid): return False
        await self.logger.debug("(db_conn) Setting doc_ext for {} to {}".format(uuid, ext))
        await self.conn.execute("UPDATE files SET doc_ext=? WHERE uuid=?", (ext, uuid))
        await self.setModifiedFlag(True)
        return True
    
    async def updateInfo(self, uuid: str, info: DocInfo) -> bool:
        if not await self._ensureExist(uuid): return False
        await self.logger.debug("(db_conn) Updating info for {} - {}".format(uuid, info))
        await self.conn.execute("UPDATE files SET info_str=? WHERE uuid=?", (info.toString(), uuid))
        await self.setModifiedFlag(True)
        return True
    
    async def updateBibtex(self, uuid: str, bibtex: str) -> bool:
        if not await self._ensureExist(uuid): return False
        await self.logger.debug("(db_conn) Updating bibtex for {}".format(uuid))
        await self.conn.execute("UPDATE files SET bibtex=? WHERE uuid=?", (bibtex, uuid))
        await self.setModifiedFlag(True)
        return True
    
    async def updateComments(self, uuid: str, comments: str) -> bool:
        if not await self._ensureExist(uuid): return False
        # await self.logger.debug("(db_conn) Updating comments for {}".format(uuid))   # too verbose
        await self.conn.execute("UPDATE files SET comments=? WHERE uuid=?", (comments, uuid))
        await self.setModifiedFlag(True)
        return True
    
    async def updateAbstract(self, uuid: str, abstract: str) -> bool:
        if not await self._ensureExist(uuid): return False
        # await self.logger.debug("(db_conn) Updating abstract for {}".format(uuid))   # too verbose
        await self.conn.execute("UPDATE files SET abstract=? WHERE uuid=?", (abstract, uuid))
        await self.setModifiedFlag(True)
        return True
    
    async def commit(self):
        """
        Be sure to register this function to the event loop!
        """
        if not self.__modified: return
        await self.conn.commit()
        await self.setModifiedFlag(False)
        await self.logger.debug("Committed document database")
    
    async def printData(self, uuid: str):
        if not await self._ensureExist(uuid): return False
        async with self.conn.execute("SELECT * FROM files WHERE uuid=?", (uuid,)) as cursor:
            row = cursor.fetchone()
        print(row)
