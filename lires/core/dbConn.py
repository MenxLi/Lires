"""
Sqlite connection interface
"""
from __future__ import annotations
import json, os, uuid, hashlib
import typing
from typing import TypedDict, Optional, TYPE_CHECKING
import dataclasses
import platform
import aiosqlite

from .base import LiresBase
from ..utils import TimeUtils
from ..utils.author import formatAuthorName
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
    version_import: str
    version_modify: str
    device_import: str
    device_modify: str

    DocInfoDictT = typing.TypedDict("DocInfoDictT", {
        "uuid": str,            # maybe ommited in the future, duplicate with file key
        "version_import": str,
        "version_modify": str,
        "device_import": str,
        "device_modify": str,
    })

    @classmethod
    def fromString(cls, s: str):
        s_dict = json.loads(s)
        return cls(**s_dict)

    def toString(self) -> str:
        return json.dumps(self.toDict())
    
    def toDict(self) -> DocInfoDictT:
        return dataclasses.asdict(self)     # type: ignore

# use this to separate tags and authors,
# because sqlite does not support list type, 
# use this, we can easily split and join the string, 
# it should be faster than json?
LIST_SEP = "&sp;"
class DBFileRawInfo(TypedDict):
    uuid: str           # File uuid, should be unique for each file
    bibtex: str         # Bibtex string, should be valid and remove abstract, at least contains title, year, authors
    title: str          # Title, string
    year: int           # int, year
    publication: str    # Publication, string
    authors: str        # Authors, string (separator: LIST_SEP)
    tags: str           # Tags, string (separator: LIST_SEP)
    url: str            # URL, string
    abstract: str       # Abstract, markdown
    comments: str       # Note markdown
    time_import: float  # Time imported, float
    time_modify: float  # Time modified, float
    info_str: str       # Info string, json serializable string of DocInfo
    doc_ext: FileTypeT  # Document file type

def parseList(s: str) -> list[str]:
    if s == "": return []
    return s.split(LIST_SEP)
def dumpList(l: list[str]) -> str:
    return LIST_SEP.join(l)


class DBFileInfo(TypedDict):
    # The same as DBFileRawInfo, but with some fields converted to their original type
    uuid: str           
    bibtex: str         
    title: str         
    year: int          
    publication: str   
    authors: list[str] 
    tags: list[str]   
    url: str         
    abstract: str   
    comments: str  
    time_import: float  # Time imported, float
    time_modify: float  # Time modified, float
    info_str: str 
    doc_ext: FileTypeT


__THIS_NODE__ = platform.node()
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

        self.cache = DBConnectionCache(
            cache_id=hashlib.md5(
                os.path.abspath(db_path).encode()
                ).hexdigest()
            )
    
    async def init(self) -> DBConnection:
        """
        May call this function to re-init the connection after close
        """
        self.conn = await aiosqlite.connect(self.db_path)
        await self.__maybeCreateTable()
        await self.cache.init()
        await self.cache.buildInitCache(await self.getAll())
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
                    title TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    publication TEXT NOT NULL,
                    authors TEXT NOT NULL,

                    tags TEXT NOT NULL,
                    url TEXT NOT NULL,
                    abstract TEXT NOT NULL,
                    comments TEXT NOT NULL,
                    time_import REAL NOT NULL DEFAULT 0,
                    time_modify REAL NOT NULL DEFAULT 0,
                    info_str TEXT NOT NULL,
                    doc_ext TEXT NOT NULL,
                    misc_dir TEXT
                )
                """)
                await self.setModifiedFlag(True)
        
    async def close(self):
        await self.commit()
        await self.conn.close()
        await self.cache.conn.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.commit()
        await self.close()

    
    def __formatRow(self, row: tuple | aiosqlite.Row) -> DBFileInfo:
        return {
            "uuid": row[0],
            "bibtex": row[1],
            "title": row[2],
            "year": row[3],
            "publication": row[4],
            "authors": parseList(row[5]),
            "tags": parseList(row[6]),
            "url": row[7],
            "abstract": row[8],
            "comments": row[9],
            "time_import": row[10],
            "time_modify": row[11],
            "info_str": row[12],
            "doc_ext": row[13]
        }

    async def size(self) -> int:
        async with self.conn.execute("SELECT COUNT(*) FROM files") as cursor:
            return (await cursor.fetchone())[0]     # type: ignore
    async def authors(self) -> list[str]:
        return await self.cache.allAuthors()
    async def tags(self) -> list[str]:
        return await self.cache.allTags()
    async def keys(self, sortby = None, reverse = False) -> list[str]:
        """ Return all uuids """
        if await self.size() == 0: return []
        if not sortby:
            async with self.conn.execute("SELECT uuid FROM files") as cursor:
                return [row[0] for row in await cursor.fetchall()]
        else:
            async with self.conn.execute("SELECT uuid FROM files ORDER BY {} {}".format(sortby, "DESC" if reverse else "ASC")) as cursor:
                return [row[0] for row in await cursor.fetchall()]
    async def checkNoneExist(self, uuids: list[str]) -> list[str]:
        """Check if uuids exist, return those not exist """
        async with self.conn.execute("SELECT uuid FROM files WHERE uuid IN ({})".format(",".join(["?"]*len(uuids))), uuids) as cursor:
            exist = [row[0] for row in await cursor.fetchall()]
        return list(set(uuids).difference(exist))
    
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
            raise self.Error.LiresEntryNotFoundError("Some uuids not found")
        ret = [self.__formatRow(row) for row in rows]
        return ret
    
    async def getAll(self) -> list[DBFileInfo]:
        """
        Get all file info
        """
        async with self.conn.execute("SELECT * FROM files") as cursor:
            rows = await cursor.fetchall()
        return [self.__formatRow(row) for row in rows]
    
    async def _insertItem(self, item_raw: DBFileRawInfo) -> bool:
        """
        Insert item into database, will overwrite if uuid already exists
        """
        await self.logger.debug("(db_conn) Inserting item {}".format(item_raw["uuid"]))
        if await self.get(item_raw["uuid"]) is not None:
            # if uuid already exists, delete it first
            await self.conn.execute("DELETE FROM files WHERE uuid=?", (item_raw["uuid"],))
        await self.conn.execute(
            """
            INSERT INTO files (uuid, bibtex, title, year, publication, authors, tags, url, abstract, comments, time_import, time_modify, info_str, doc_ext)
            VALUES (?,?,?, ?,?,?, ?,?,?, ?,?,?, ?,?)
            """,
            (
                item_raw["uuid"],
                item_raw["bibtex"],
                item_raw["title"],
                item_raw["year"],
                item_raw["publication"],
                item_raw["authors"],
                item_raw["tags"],
                item_raw["url"],
                item_raw["abstract"],
                item_raw["comments"],
                item_raw["time_import"],
                item_raw["time_modify"],
                item_raw["info_str"],
                item_raw["doc_ext"]
            ))
                                
        await self.setModifiedFlag(True)
        return True
    
    async def _ensureExist(self, uuid: str) -> Optional[DBFileInfo]:
        if not (ret:=await self.get(uuid)):
            await self.logger.error("uuid {} not exists".format(uuid))
        return ret
    
    async def addEntry(
            self, 

            # bibtex fields
            bibtex: str, 
            title: str,
            year: int | str,
            publication: str,
            authors: list[str],
            
            tags: list[str] = [],
            url: str = "",
            abstract: str = "", 
            comments: str = "", 
            doc_ext: FileTypeT = "",
            doc_info: Optional[DocInfo | dict] = None
            ) -> Optional[str]:
        """
        Add an entry to the database
        DocInfo will be generated if not provided, should be None for new data generated,
            can be provided for data imported from other sources (e.g. old version),
            or a dict that contains partial information (will be merged with generated default info)
        return uuid if success, None if failed
        """
        year = int(year)
        # generate info
        doc_info_default = DocInfo(
            uuid = str(uuid.uuid4()),
            version_import = VERSION,
            version_modify = VERSION,
            device_import = __THIS_NODE__,
            device_modify = __THIS_NODE__,
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
        await self._insertItem({
            "uuid": uid,
            "bibtex": bibtex,
            "title": title,
            "year": year,
            "publication": publication,
            "authors": dumpList(authors),
            "tags": dumpList(tags),
            "url": url,
            "abstract": abstract,
            "comments": comments,
            "time_import": TimeUtils.nowStamp(),
            "time_modify": TimeUtils.nowStamp(),
            "info_str": doc_info.toString(),
            "doc_ext": doc_ext
        })
        # add cache
        await self.cache.addTagCache(uid, tags)
        await self.cache.addAuthorCache(uid, authors)
        await self.setModifiedFlag(True)
        return uid
    
    async def _touchEntry(self, uuid: str) -> bool:
        # exist check should be done before calling this function
        await self.conn.execute("UPDATE files SET time_modify=? WHERE uuid=?", (TimeUtils.nowStamp(), uuid))
        info = DocInfo.fromString(
            (await (await self.conn.execute("SELECT info_str FROM files WHERE uuid=?", (uuid,))).fetchone())[0]  # type: ignore
        )
        info.version_modify = VERSION
        info.device_modify = __THIS_NODE__
        await self.conn.execute("UPDATE files SET info_str=? WHERE uuid=?", (info.toString(), uuid))
        await self.setModifiedFlag(True)
        return True
    
    async def removeEntry(self, uuid: str) -> bool:
        if not (entry:=await self._ensureExist(uuid)): return False
        await self.logger.debug("(db_conn) Removing entry {}".format(uuid))
        await self.conn.execute("DELETE FROM files WHERE uuid=?", (uuid,))

        # remove related cache
        await self.cache.removeTagCache(uuid, entry["tags"])
        await self.cache.removeAuthorCache(uuid, entry["authors"])

        await self.setModifiedFlag(True)
        await self.logger.debug("Removed entry {}".format(uuid))
        return True
    
    async def setDocExt(self, uuid: str, ext: Optional[str]) -> bool:
        if not await self._ensureExist(uuid): return False
        await self.logger.debug("(db_conn) Setting doc_ext for {} to {}".format(uuid, ext))
        await self.conn.execute("UPDATE files SET doc_ext=? WHERE uuid=?", (ext, uuid))
        await self._touchEntry(uuid)
        return True
    
    async def updateBibtex(
        self, uuid: str, 
        bibtex: str, 
        title: str,
        year: str,
        publication: str,
        authors: list[str],
        ) -> bool:
        """Provide a new bibtex string, and update the title, year, publication, authors accordingly."""
        if not (old_entry:=await self._ensureExist(uuid)): return False
        await self.logger.debug("(db_conn) Updating bibtex for {}".format(uuid))
        await self.conn.execute("UPDATE files SET bibtex=?, title=?, year=?, publication=?, authors=? WHERE uuid=?", (
            bibtex, title, year, publication, dumpList(authors), uuid
        ))

        # check if authors changed and maybe update cache
        if set(old_entry["authors"]) != set(authors):
            await self.logger.debug("(db_conn) Updating author cache for {}".format(uuid))
            await self.cache.removeAuthorCache(uuid, old_entry["authors"])
            await self.cache.addAuthorCache(uuid, authors)

        await self._touchEntry(uuid)
        return True
    
    async def updateTags(self, uuid: str, tags: list[str]) -> bool:
        if not (old_entry:=await self._ensureExist(uuid)): return False
        await self.logger.debug("(db_conn) Updating tags for {}".format(uuid))
        await self.conn.execute("UPDATE files SET tags=? WHERE uuid=?", (dumpList(tags), uuid))

        # check if tags changed and maybe update cache
        if set(old_entry["tags"]) != set(tags):
            await self.logger.debug("(db_conn) Updating tag cache for {}".format(uuid))
            await self.cache.removeTagCache(uuid, old_entry["tags"])
            await self.cache.addTagCache(uuid, tags)

        await self._touchEntry(uuid)
        return True
    
    async def updateUrl(self, uuid: str, url: str) -> bool:
        if not await self._ensureExist(uuid): return False
        await self.logger.debug("(db_conn) Updating url for {}".format(uuid))
        await self.conn.execute("UPDATE files SET url=? WHERE uuid=?", (url, uuid))
        await self._touchEntry(uuid)
        return True
    
    async def updateComments(self, uuid: str, comments: str) -> bool:
        if not await self._ensureExist(uuid): return False
        # await self.logger.debug("(db_conn) Updating comments for {}".format(uuid))   # too verbose
        await self.conn.execute("UPDATE files SET comments=? WHERE uuid=?", (comments, uuid))
        await self._touchEntry(uuid)
        return True
    
    async def updateAbstract(self, uuid: str, abstract: str) -> bool:
        if not await self._ensureExist(uuid): return False
        # await self.logger.debug("(db_conn) Updating abstract for {}".format(uuid))   # too verbose
        await self.conn.execute("UPDATE files SET abstract=? WHERE uuid=?", (abstract, uuid))
        await self._touchEntry(uuid)
        return True
    
    async def commit(self):
        """
        Be sure to register this function to the event loop!
        """
        if not self.__modified: return
        await self.conn.commit()
        await self.cache.conn.commit()
        await self.setModifiedFlag(False)
        await self.logger.debug("Committed document database")
    
    async def printData(self, uuid: str):
        if not await self._ensureExist(uuid): return False
        async with self.conn.execute("SELECT * FROM files WHERE uuid=?", (uuid,)) as cursor:
            row = cursor.fetchone()
        print(row)
    
    # ==============================================================================
    #                              for searching
    # ==============================================================================

    async def filter(
        self, strict = True,
        ignore_case = False,
        from_uids: Optional[list[str]] = None,
        title: Optional[str] = None,
        publication: Optional[str] = None,
        note: Optional[str] = None,
        year: Optional[tuple[Optional[int], Optional[int]] | int] = None,
        authors: Optional[list[str]] = None,
        tags: Optional[list[str]] = None
    ) -> list[str]:
        '''
        !! not fully tested yet !!
        A simple filter function for fast search,

        (tag, and author) will involve more search operations,

        - year: tuple of two int, [start, end), if start or end is None, it will be treated as -inf or inf
        '''
        if await self.size() == 0: return []
        # build query
        query_conds = []
        query_items = []
        if from_uids is not None:
            query_conds.append("uuid IN ({})".format(",".join(["?"]*len(from_uids))))
            query_items.extend(from_uids)
        for [field, value] in [
            ["title", title],
            ["publication", publication],
            ["comments", note]
        ]:
            if value:
                if strict and not ignore_case:
                    query_conds.append("{}=?".format(field))
                elif strict and ignore_case:
                    query_conds.append("{}=? COLLATE NOCASE".format(field))
                elif not strict and not ignore_case:
                    query_conds.append("{} LIKE ?".format(field))
                else:
                    query_conds.append("{} LIKE ? COLLATE NOCASE".format(field))
                
                # build query items
                if not strict:
                    query_items.append(f"%{value}%")
                else:
                    query_items.append(value)

        if year:
            if isinstance(year, int):
                year = (year, year+1)
            if year[0] is None:
                year = (0, year[1])
            if year[1] is None:
                year = (year[0], 9999)
            query_conds.append("year>=? AND year<?")
            query_items.extend(year)

        # reverse for better debug info
        query_conds.reverse()
        query_items.reverse()

        if query_conds:
            # execute
            query = "SELECT uuid FROM files WHERE " + " AND ".join(query_conds)
            await self.logger.debug(
                "Executing query: {} | with items: {}"
                .format(_q[:100] + "..." if len(_q:=str(query)) > 100 else _q, 
                        _it[:100] + "..." if len(_it:=str(query_items)) > 100 else _it)
                )

            async with self.conn.execute(
                query, tuple(query_items)
                ) as cursor:
                ret = [row[0] for row in await cursor.fetchall()]
        else:
            ret = await self.keys()
        
        if authors:
            ret = set(ret).intersection(await self.cache.queryAuthors(authors, strict, ignore_case))
        if tags:
            ret = set(ret).intersection(await self.cache.queryTags(tags, strict, ignore_case))
        return list(ret)

class DBConnectionCache(LiresBase):
    """
    Reverse index for authors and tags, for faster searching (maybe more?)
    The subtables must be two columns, the first is the key, the second is the value (named "entries")
    the value should be a json string of a list of uuids
    """
    logger = LiresBase.loggers().core
    def __init__(self, cache_id: str) -> None:
        self.__id = cache_id
        self.__conn: aiosqlite.Connection
    
    @property
    def conn(self):
        try:
            return self.__conn
        except AttributeError:
            raise AttributeError("DBConnectionCache is not initialized")

    async def init(self):
        # create in-memory database, remember to close it after use!
        self.__conn = await aiosqlite.connect(f"file:{self.__id}?mode=memory&cache=shared", uri=True)

        # two cache tables for authors and tags
        async with self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='authors'") as cursor:
            if not await cursor.fetchone():
                await cursor.execute("""
                CREATE TABLE IF NOT EXISTS authors (
                    author TEXT PRIMARY KEY,
                    entries TEXT NOT NULL
                )
                """)
        async with self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tags'") as cursor:
            if not await cursor.fetchone():
                await cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    tag TEXT PRIMARY KEY,
                    entries TEXT NOT NULL
                )
                """)
        return self

    async def buildInitCache(self, all_items: list[DBFileInfo]):
        await self.logger.info("[DBCache] Building initial cache")
        # build cache for authors and tags
        authors_cache: dict[str, list[str]] = {}
        tags_cache: dict[str, list[str]] = {}
        for item in all_items:
            for author in item["authors"]:
                # format author name!
                author = formatAuthorName(author)

                if author not in authors_cache:
                    authors_cache[author] = []
                authors_cache[author].append(item["uuid"])
            for tag in item["tags"]:
                if tag not in tags_cache:
                    tags_cache[tag] = []
                tags_cache[tag].append(item["uuid"])
        await self._removeAllCache()
        for author, entries in authors_cache.items():
            await self.conn.execute("INSERT INTO authors (author, entries) VALUES (?, ?)", (author, json.dumps(entries)))
        for tag, entries in tags_cache.items():
            await self.conn.execute("INSERT INTO tags (tag, entries) VALUES (?, ?)", (tag, json.dumps(entries)))
        await self.logger.debug("[DBCache] Initial cache built")
    
    async def _removeAllCache(self):
        async with self.conn.execute("DELETE FROM authors") as cursor:
            await cursor.fetchall()
        async with self.conn.execute("DELETE FROM tags") as cursor:
            await cursor.fetchall()
    
    async def allAuthors(self) -> list[str]:
        async with self.conn.execute("SELECT author FROM authors") as cursor:
            return [row[0] for row in await cursor.fetchall()]
    
    async def allTags(self) -> list[str]:
        async with self.conn.execute("SELECT tag FROM tags") as cursor:
            return [row[0] for row in await cursor.fetchall()]

    async def _queryBy(self, table: str, col: str, q: list[str], strict: bool, ignore_case: bool) -> set[str]:
        """ return a set of uuids that match the query """
        query_conds = []
        query_items = []
        for item in q:
            if strict and not ignore_case:
                query_conds.append("{}=?".format(col))
            elif strict and ignore_case:
                query_conds.append("{}=? COLLATE NOCASE".format(col))
            elif not strict and not ignore_case:
                query_conds.append("{} LIKE ?".format(col))
            else:
                query_conds.append("{} LIKE ? COLLATE NOCASE".format(col))
            if not strict:
                query_items.append(f"%{item}%")
            else:
                query_items.append(item)
        query = "SELECT entries FROM {} WHERE ".format(table) + " OR ".join(query_conds)
        found_uids = []
        async with self.conn.execute(query, tuple(query_items)) as cursor:
            for row in await cursor.fetchall():
                found_uids.append(json.loads(row[0]))
        if not found_uids: return set()
        if len(found_uids) == 1: return set(found_uids[0])
        # make a intersection
        ret = set(found_uids[0])
        for uid in found_uids[1:]:
            ret = ret.intersection(uid)
        return ret
    async def queryAuthors(self, q: list[str], strict: bool = False, ignore_case: bool = True) -> set[str]:
        q = [formatAuthorName(x) for x in q]
        return await self._queryBy("authors", "author", q, strict, ignore_case)
    async def queryTags(self, q: list[str], strict: bool = False, ignore_case: bool = True) -> set[str]:
        return await self._queryBy("tags", "tag", q, strict, ignore_case)
    
    # These functions are for updating cache, should be called after the main database is updated
    async def removeTagCache(self, uuid: str, tags: list[str]):
        for tag in tags:
            async with self.conn.execute("SELECT entries FROM tags WHERE tag=?", (tag,)) as cursor:
                ret = await cursor.fetchone()
            if ret is None:
                continue
            entries: list[str] = json.loads(ret[0])
            entries.remove(uuid)
            if not entries:
                await self.conn.execute("DELETE FROM tags WHERE tag=?", (tag,))
            await self.conn.execute("UPDATE tags SET entries=? WHERE tag=?", (json.dumps(entries), tag))
    
    async def removeAuthorCache(self, uuid: str, authors: list[str]):
        for author in authors:
            async with self.conn.execute("SELECT entries FROM authors WHERE author=?", (author,)) as cursor:
                ret = await cursor.fetchone()
            if ret is None:
                continue
            entries: list[str] = json.loads(ret[0])
            entries.remove(uuid)
            if not entries:
                await self.conn.execute("DELETE FROM authors WHERE author=?", (author,))
            await self.conn.execute("UPDATE authors SET entries=? WHERE author=?", (json.dumps(entries), author))
    
    async def addTagCache(self, uuid: str, tags: list[str]):
        for tag in tags:
            async with self.conn.execute("SELECT entries FROM tags WHERE tag=?", (tag,)) as cursor:
                ret = await cursor.fetchone()
            if ret is None:
                await self.conn.execute("INSERT INTO tags (tag, entries) VALUES (?, ?)", (tag, json.dumps([uuid])))
            else:
                entries: list[str] = json.loads(ret[0])
                entries.append(uuid)
                await self.conn.execute("UPDATE tags SET entries=? WHERE tag=?", (json.dumps(entries), tag))
    
    async def addAuthorCache(self, uuid: str, authors: list[str]):
        for author in authors:
            async with self.conn.execute("SELECT entries FROM authors WHERE author=?", (author,)) as cursor:
                ret = await cursor.fetchone()
            if ret is None:
                await self.conn.execute("INSERT INTO authors (author, entries) VALUES (?, ?)", (author, json.dumps([uuid])))
            else:
                entries: list[str] = json.loads(ret[0])
                entries.append(uuid)
                await self.conn.execute("UPDATE authors SET entries=? WHERE author=?", (json.dumps(entries), author))