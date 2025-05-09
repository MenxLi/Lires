"""
Sqlite connection interface
"""
from __future__ import annotations
import json, os, uuid, asyncio
import typing
from typing import TypedDict, Optional, TYPE_CHECKING
import dataclasses
import platform
import aiosqlite
import functools

from .dbConnUpgrade import *
from .base import LiresBase
from ..utils import TimeUtils
from ..utils.author import format_author_name
from ..version import VERSION, versionize

if TYPE_CHECKING:
    from ..types.dataT import FileTypeT


DB_MOD_LOCK = asyncio.Lock()

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
    def from_string(cls, s: str):
        s_dict = json.loads(s)
        return cls(**s_dict)

    def to_string(self) -> str:
        return json.dumps(self.to_dict())
    
    def to_dict(self) -> DocInfoDictT:
        return dataclasses.asdict(self)     # type: ignore

# use this to separate tags and authors,
# because sqlite does not support list type, 
# use this, we can easily split and join the string, 
# it should be faster than json?
LIST_SEP = "&sp;"
class DBFileRawInfo(TypedDict):
    uuid: str           # File uuid, should be unique for each file
    bibtex: str         # Bibtex string, should be valid and remove abstract, at least contains title, year, authors
    type: str          # Type, string
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

def parse_list(s: str) -> list[str]:
    if s == "": return []
    return s.split(LIST_SEP)
def dump_list(l: list[str]) -> str:
    return LIST_SEP.join(l)


class DBFileInfo(TypedDict):
    # The same as DBFileRawInfo, but with some fields converted to their original type
    uuid: str           
    bibtex: str         
    type: str
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

        self.cache = DBConnectionCache()
    
    async def init(self) -> DBConnection:
        """
        May call this function to re-init the connection after close
        """
        async with DB_MOD_LOCK:
            self.conn = await aiosqlite.connect(self.db_path)
            await self.__init_tables()
            await self.__auto_upgrade()
            await self.cache.init()
            await self.cache.build_init_cache(await self.get_all())
        return self
    
    async def is_initialized(self) -> bool:
        try:
            if self.conn is None:
                return False
            return True
        except AttributeError:
            return False
    
    async def set_modified_flag(self, modified: bool):
        self.__modified = modified
    
    async def __maybe_create_meta_table(self):
        # check if meta table exists
        async with self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='meta'") as cursor:
            if not await cursor.fetchone():
                await cursor.execute("""
                CREATE TABLE IF NOT EXISTS meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """)
                await self.set_modified_flag(True)
        
        async def get_init_version():
            has_main_table = await (await self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='files'")).fetchone()
            if not has_main_table:
                # this is a new database, insert current version
                return VERSION
            else:
                # backware compatibility, since 1.8.0, version is stored in meta table
                # main table exists means this is an existing database, insert 0.0.0, for auto upgrade
                return '0.0.0'

        # check if version key exists
        async with self.conn.execute("SELECT value FROM meta WHERE key='version'") as cursor:
            ret = await cursor.fetchone()
            if ret is None:
                await self.conn.execute("INSERT INTO meta (key, value) VALUES ('version', ?)", (await get_init_version(),))
                await self.set_modified_flag(True)
    
    async def __init_tables(self):
        """ Create table if not exist """
        # create meta table
        await self.__maybe_create_meta_table()

        # create main table
        async with self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='files'") as cursor:
            if not await cursor.fetchone():
                await cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    uuid TEXT PRIMARY KEY,

                    bibtex TEXT NOT NULL,
                    type TEXT NOT NULL,
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
                await self.set_modified_flag(True)
    
    async def __auto_upgrade(self):
        """
        Auto upgrade database if needed, 
        for backward compatibility
        """
        async def set_version_record(version: str):
            await self.conn.execute("UPDATE meta SET value=? WHERE key='version'", (version,))
            await self.set_modified_flag(True)

        ## Update functions

        ## Check version and upgrade
        curr_version = versionize(VERSION)
        async with self.conn.execute("SELECT value FROM meta WHERE key='version'") as cursor:
            ver = await cursor.fetchone()
            assert ver is not None
            record_version = versionize(ver[0])

        if record_version < versionize("1.8.0"):
            await upgrade_1_8_0(self)
            await set_version_record("1.8.0")

        if record_version != curr_version:
            await set_version_record(curr_version.string())
            await self.logger.info("Upgraded database {} from version {} to {}".format(self.db_path, record_version, curr_version))
        
    async def close(self):
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
            "type": row[2],
            "title": row[3],
            "year": row[4],
            "publication": row[5],
            "authors": parse_list(row[6]),
            "tags": parse_list(row[7]),
            "url": row[8],
            "abstract": row[9],
            "comments": row[10],
            "time_import": row[11],
            "time_modify": row[12],
            "info_str": row[13],
            "doc_ext": row[14]
        }

    async def size(self) -> int:
        async with self.conn.execute("SELECT COUNT(*) FROM files") as cursor:
            return (await cursor.fetchone())[0]     # type: ignore
    async def authors(self) -> list[str]:
        return await self.cache.all_authors()
    async def tags(self) -> list[str]:
        return await self.cache.all_tags()
    async def keys(self, sortby = None, reverse = False) -> list[str]:
        """ Return all uuids """
        if await self.size() == 0:
            # just return empty list if no entry,
            # otherwise the following query will raise an error if sortby is not None
            return []   
        if not sortby:
            async with self.conn.execute("SELECT uuid FROM files") as cursor:
                return [row[0] for row in await cursor.fetchall()]
        else:
            async with self.conn.execute("SELECT uuid FROM files ORDER BY {} {}".format(sortby, "DESC" if reverse else "ASC")) as cursor:
                return [row[0] for row in await cursor.fetchall()]
    async def check_nonexist(self, uuids: list[str]) -> list[str]:
        """Check if uuids exist, return those not exist """
        async with self.conn.execute("SELECT uuid FROM files WHERE uuid IN ({})".format(",".join(["?"]*len(uuids))), uuids) as cursor:
            exist = [row[0] for row in await cursor.fetchall()]
        return list(set(uuids).difference(exist))
    
    async def sort_keys(self, keys: list[str], sort_by: str = "time_import", reverse: bool = True) -> list[str]:
        """ Sort keys by a field """
        async with self.conn.execute("SELECT uuid, {} FROM files WHERE uuid IN ({}) ORDER BY {} {}".format(sort_by, ",".join(["?"]*len(keys)), sort_by, "DESC" if reverse else "ASC"), keys) as cursor:
            rows = await cursor.fetchall()
        return [row[0] for row in rows]
    
    async def get(self, uuid: str) -> Optional[DBFileInfo]:
        """
        Get file info by uuid
        """
        async with self.conn.execute("SELECT * FROM files WHERE uuid=?", (uuid,)) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
        return self.__formatRow(row)
    
    async def get_many(self, uuids: list[str], sort_by = 'time_import', reverse = True) -> list[DBFileInfo]:
        """ Get file info by uuid, this will use new order specified by orderBy!  """
        if await self.size() == 0: return []
        async with self.conn.execute("SELECT * FROM files WHERE uuid IN ({}) ORDER BY {} {}".format(",".join(["?"]*len(uuids)), sort_by, "DESC" if reverse else "ASC"), uuids) as cursor:
            rows = await cursor.fetchall()
        if len(list(rows)) != len(uuids):
            raise self.Error.LiresEntryNotFoundError("Some uuids not found")
        ret = [self.__formatRow(row) for row in rows]
        return ret
    
    async def get_all(self, sort_by = 'time_import', reverse = True) -> list[DBFileInfo]:
        """
        Get all file info
        """
        if await self.size() == 0: return []
        async with self.conn.execute("SELECT * FROM files ORDER BY {} {}".format(sort_by, "DESC" if reverse else "ASC")) as cursor:
            rows = await cursor.fetchall()
        return [self.__formatRow(row) for row in rows]
    
    async def _insert_item(self, item_raw: DBFileRawInfo) -> bool:
        """
        Insert item into database, will overwrite if uuid already exists
        """
        await self.logger.debug("(db_conn) Inserting item {}".format(item_raw["uuid"]))
        if await self.get(item_raw["uuid"]) is not None:
            # if uuid already exists, delete it first
            await self.conn.execute("DELETE FROM files WHERE uuid=?", (item_raw["uuid"],))
        await self.conn.execute(
            """
            INSERT INTO files (uuid, bibtex, type, title, year, publication, authors, tags, url, abstract, comments, time_import, time_modify, info_str, doc_ext)
            VALUES (?,?,?, ?,?,?,?, ?,?,?, ?,?,?, ?,?)
            """,
            (
                item_raw["uuid"],
                item_raw["bibtex"],
                item_raw["type"],
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
                                
        await self.set_modified_flag(True)
        return True
    
    async def _ensure_exist(self, uuid: str) -> Optional[DBFileInfo]:
        if not (ret:=await self.get(uuid)):
            await self.logger.error("uuid {} not exists".format(uuid))
        return ret
    
    async def add_entry(
            self, 

            # bibtex fields
            bibtex: str, 
            dtype: str,
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
            docinfo_dict = doc_info_default.to_dict()
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
        async with DB_MOD_LOCK:
            await self._insert_item({
                "uuid": uid,
                "bibtex": bibtex,
                "type": dtype,
                "title": title,
                "year": year,
                "publication": publication,
                "authors": dump_list(authors),
                "tags": dump_list(tags),
                "url": url,
                "abstract": abstract,
                "comments": comments,
                "time_import": TimeUtils.now_stamp(),
                "time_modify": TimeUtils.now_stamp(),
                "info_str": doc_info.to_string(),
                "doc_ext": doc_ext
            })
            # add cache
            await self.cache.add_tag_cache(uid, tags)
            await self.cache.add_author_cache(uid, authors)
            await self.set_modified_flag(True)
        return uid
    
    async def _touch_entry(self, uuid: str) -> bool:
        # exist check should be done before calling this function
        await self.conn.execute("UPDATE files SET time_modify=? WHERE uuid=?", (TimeUtils.now_stamp(), uuid))
        info = DocInfo.from_string(
            (await (await self.conn.execute("SELECT info_str FROM files WHERE uuid=?", (uuid,))).fetchone())[0]  # type: ignore
        )
        info.version_modify = VERSION
        info.device_modify = __THIS_NODE__
        await self.conn.execute("UPDATE files SET info_str=? WHERE uuid=?", (info.to_string(), uuid))
        await self.set_modified_flag(True)
        return True
    
    async def remove_entry(self, uuid: str) -> bool:
        if not (entry:=await self._ensure_exist(uuid)): return False
        await self.conn.execute("DELETE FROM files WHERE uuid=?", (uuid,))

        # remove related cache
        await self.cache.remove_tag_cache(uuid, entry["tags"])
        await self.cache.remove_author_cache(uuid, entry["authors"])

        await self.set_modified_flag(True)
        await self.logger.debug("(db_conn) Removed entry {}".format(uuid))
        return True
    
    async def set_doc_ext(self, uuid: str, ext: Optional[str]) -> bool:
        if not await self._ensure_exist(uuid): return False
        await self.logger.debug("(db_conn) Setting doc_ext for {} to {}".format(uuid, ext))
        await self.conn.execute("UPDATE files SET doc_ext=? WHERE uuid=?", (ext, uuid))
        await self._touch_entry(uuid)
        return True
    
    async def update_bibtex(
        self, uuid: str, 
        bibtex: str, 
        dtype: str,
        title: str,
        year: str,
        publication: str,
        authors: list[str],
        ) -> bool:
        """Provide a new bibtex string, and update the title, year, publication, authors accordingly."""
        if not (old_entry:=await self._ensure_exist(uuid)): return False
        await self.logger.debug("(db_conn) Updating bibtex for {}".format(uuid))

        async with DB_MOD_LOCK:
            await self.conn.execute("UPDATE files SET bibtex=?, type=?, title=?, year=?, publication=?, authors=? WHERE uuid=?", (
                bibtex, dtype, title, year, publication, dump_list(authors), uuid
            ))

            # check if authors changed and maybe update cache
            if set(old_entry["authors"]) != set(authors):
                await self.logger.debug("(db_conn) Updating author cache for {}".format(uuid))
                await self.cache.remove_author_cache(uuid, old_entry["authors"])
                await self.cache.add_author_cache(uuid, authors)

            await self._touch_entry(uuid)
        return True
    
    async def update_tags(self, uuid: str, tags: list[str]) -> bool:
        async with DB_MOD_LOCK:
            if not (old_entry:=await self._ensure_exist(uuid)): return False
            await self.logger.debug("(db_conn) Updating tags for {}".format(uuid))
            await self.conn.execute("UPDATE files SET tags=? WHERE uuid=?", (dump_list(tags), uuid))

            # check if tags changed and maybe update cache
            if set(old_entry["tags"]) != set(tags):
                await self.logger.debug("(db_conn) Updating tag cache for {}".format(uuid))
                await self.cache.remove_tag_cache(uuid, old_entry["tags"])
                await self.cache.add_tag_cache(uuid, tags)

            await self._touch_entry(uuid)
        return True
    
    async def update_url(self, uuid: str, url: str) -> bool:
        async with DB_MOD_LOCK:
            if not await self._ensure_exist(uuid): return False
            await self.logger.debug("(db_conn) Updating url for {}".format(uuid))
            await self.conn.execute("UPDATE files SET url=? WHERE uuid=?", (url, uuid))
            await self._touch_entry(uuid)
        return True
    
    async def update_comments(self, uuid: str, comments: str) -> bool:
        async with DB_MOD_LOCK:
            if not await self._ensure_exist(uuid): return False
            # await self.logger.debug("(db_conn) Updating comments for {}".format(uuid))   # too verbose
            await self.conn.execute("UPDATE files SET comments=? WHERE uuid=?", (comments, uuid))
            await self._touch_entry(uuid)
        return True
    
    async def update_abstract(self, uuid: str, abstract: str) -> bool:
        async with DB_MOD_LOCK:
            if not await self._ensure_exist(uuid): return False
            # await self.logger.debug("(db_conn) Updating abstract for {}".format(uuid))   # too verbose
            await self.conn.execute("UPDATE files SET abstract=? WHERE uuid=?", (abstract, uuid))
            await self._touch_entry(uuid)
        return True
    
    async def commit(self):
        """
        Be sure to register this function to the event loop!
        """
        if not self.__modified: return
        await self.conn.commit()
        await self.cache.conn.commit()
        await self.set_modified_flag(False)
        await self.logger.debug("Committed document database")
    
    async def print_data(self, uuid: str):
        if not await self._ensure_exist(uuid): return False
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
        time_import: Optional[tuple[Optional[float], Optional[float]]] = None,
        time_modify: Optional[tuple[Optional[float], Optional[float]]] = None,
        authors: Optional[list[str]] = None,
        tags: Optional[list[str]] = None
    ) -> list[str]:
        '''
        A simple filter function for fast search,

        (tag, and author) will involve more search operations,

        - year: tuple of two int, [start, end), if start or end is None, it will be treated as -inf or inf
        '''
        # build query
        if await self.size() == 0:
            return []
        query_conds = []
        query_items = []

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
        
        if time_import:
            if time_import[0] is None:
                time_import = (0, time_import[1])
            if time_import[1] is None:
                time_import = (time_import[0], 9999999999)
            query_conds.append("time_import>=? AND time_import<?")
            query_items.extend(time_import)
        
        if time_modify:
            if time_modify[0] is None:
                time_modify = (0, time_modify[1])
            if time_modify[1] is None:
                time_modify = (time_modify[0], 9999999999)
            query_conds.append("time_modify>=? AND time_modify<?")
            query_items.extend(time_modify)

        # better debug info, put uid in the end
        if from_uids is not None:
            query_conds.append("uuid IN ({})".format(",".join(["?"]*len(from_uids))))
            query_items.extend(from_uids)

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
            ret = set(ret).intersection(await self.cache.query_authors(authors, strict, ignore_case))
        if tags:
            ret = set(ret).intersection(await self.cache.query_tags(tags, strict, ignore_case))
        return list(ret)

class DBConnectionCache(LiresBase):
    """
    Reverse index for authors and tags, for faster searching (maybe more?)
    The subtables must be two columns, the first is the key, the second is the value (named "entries")
    the value should be a json string of a list of uuids
    """
    logger = LiresBase.loggers().core
    def __init__(self) -> None:
        self.__conn: aiosqlite.Connection
    
    @property
    def conn(self):
        try:
            return self.__conn
        except AttributeError:
            raise AttributeError("DBConnectionCache is not initialized")

    async def init(self):
        # create in-memory database, remember to close it after use!
        # self.__conn = await aiosqlite.connect(f"file:{self.__id}?mode=memory&cache=shared", uri=True)
        self.__conn = await aiosqlite.connect(f":memory:")

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

    async def build_init_cache(self, all_items: list[DBFileInfo]):
        await self.logger.debug("[DBCache] Building initial cache")
        # build cache for authors and tags
        authors_cache: dict[str, list[str]] = {}
        tags_cache: dict[str, list[str]] = {}
        for item in all_items:
            for author in item["authors"]:
                # format author name!
                author = format_author_name(author)

                if author not in authors_cache:
                    authors_cache[author] = []
                authors_cache[author].append(item["uuid"])
            for tag in item["tags"]:
                if tag not in tags_cache:
                    tags_cache[tag] = []
                tags_cache[tag].append(item["uuid"])
        await self._remove_all_cache()
        for author, entries in authors_cache.items():
            await self.conn.execute("INSERT INTO authors (author, entries) VALUES (?, ?)", (author, json.dumps(entries)))
        for tag, entries in tags_cache.items():
            await self.conn.execute("INSERT INTO tags (tag, entries) VALUES (?, ?)", (tag, json.dumps(entries)))
        await self.logger.debug("[DBCache] Initial cache built")
    
    async def _remove_all_cache(self):
        async with self.conn.execute("DELETE FROM authors") as cursor:
            await cursor.fetchall()
        async with self.conn.execute("DELETE FROM tags") as cursor:
            await cursor.fetchall()
    
    async def all_authors(self) -> list[str]:
        async with self.conn.execute("SELECT author FROM authors") as cursor:
            return [row[0] for row in await cursor.fetchall()]
    
    async def all_tags(self) -> list[str]:
        async with self.conn.execute("SELECT tag FROM tags") as cursor:
            return [row[0] for row in await cursor.fetchall()]

    async def _query_by(self, table: str, col: str, q: list[str], strict: bool, ignore_case: bool) -> set[str]:
        """ return a set of uuids that match the query """
        res_list: list[set[str]] = []

        for item in q:
            if strict and not ignore_case:
                q_cond = "{}=?".format(col)
            elif strict and ignore_case:
                q_cond = "{}=? COLLATE NOCASE".format(col)
            elif not strict and not ignore_case:
                q_cond = "{} LIKE ?".format(col)
            else:
                q_cond = "{} LIKE ? COLLATE NOCASE".format(col)

            if not strict:
                q_item = f"%{item}%"
            else:
                q_item = item

            query = "SELECT entries FROM {} WHERE ".format(table) + q_cond
            found_uids = []
            async with self.conn.execute(query, (q_item,)) as cursor:
                for row in await cursor.fetchall():
                    found_uids.append(json.loads(row[0]))

            # for every search query, get result's union
            if not found_uids: continue
            res_list.append(set(functools.reduce(lambda x, y: x+y, found_uids)))
        
        # return intersection of all results
        if not res_list: return set()
        return functools.reduce(lambda x, y: x.intersection(y), res_list)

    async def query_authors(self, q: list[str], strict: bool = False, ignore_case: bool = True) -> set[str]:
        q = [format_author_name(x) for x in q]
        return await self._query_by("authors", "author", q, strict, ignore_case)
    async def query_tags(self, q: list[str], strict: bool = False, ignore_case: bool = True) -> set[str]:
        return await self._query_by("tags", "tag", q, strict, ignore_case)
    
    # These functions are for updating cache, should be called after the main database is updated
    async def remove_tag_cache(self, uuid: str, tags: list[str]):
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
    
    async def remove_author_cache(self, uuid: str, authors: list[str]):
        for author in authors:
            async with self.conn.execute("SELECT entries FROM authors WHERE author=?", (author,)) as cursor:
                ret = await cursor.fetchone()
            if ret is None:
                continue
            entries: list[str] = json.loads(ret[0])
            try:
                entries.remove(uuid)
            except ValueError as e:
                await self.logger.error(f"Failed to remove {uuid} from author {author}, {e}. Maybe the entry is not in the list?")
            if not entries:
                await self.conn.execute("DELETE FROM authors WHERE author=?", (author,))
            await self.conn.execute("UPDATE authors SET entries=? WHERE author=?", (json.dumps(entries), author))
    
    async def add_tag_cache(self, uuid: str, tags: list[str]):
        for tag in tags:
            async with self.conn.execute("SELECT entries FROM tags WHERE tag=?", (tag,)) as cursor:
                ret = await cursor.fetchone()
            if ret is None:
                await self.conn.execute("INSERT INTO tags (tag, entries) VALUES (?, ?)", (tag, json.dumps([uuid])))
            else:
                entries: list[str] = json.loads(ret[0])
                entries.append(uuid)
                await self.conn.execute("UPDATE tags SET entries=? WHERE tag=?", (json.dumps(entries), tag))
    
    async def add_author_cache(self, uuid: str, authors: list[str]):
        for author in authors:
            author = format_author_name(author)
            async with self.conn.execute("SELECT entries FROM authors WHERE author=?", (author,)) as cursor:
                ret = await cursor.fetchone()
            if ret is None:
                await self.conn.execute("INSERT INTO authors (author, entries) VALUES (?, ?)", (author, json.dumps([uuid])))
            else:
                entries: list[str] = json.loads(ret[0])
                entries.append(uuid)
                await self.conn.execute("UPDATE authors SET entries=? WHERE author=?", (json.dumps(entries), author))