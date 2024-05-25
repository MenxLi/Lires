from __future__ import annotations
import os, asyncio, dataclasses, zipfile
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
from typing import List, Union, Optional, Literal
from .dataTags import DataTags, TagRule
from .fileTools import FileManipulator
from .dbConn import DBFileInfo, DBConnection
from .base import LiresBase
from ..vector.database import VectorDatabase
from ..types.dataT import DataPointSummary

class DataCore(LiresBase):
    logger = LiresBase.loggers().core

class DataPoint(DataCore):
    """
    A buffer that holds parsed information of a single data
    Provide quick access to data information and some high-level operations
    """
    MAX_AUTHOR_ABBR = 36
    fm: FileManipulator
    def __init__(self, summary: DataPointSummary):
        """ The basic data structure that holds single data """
        self.__summary = summary

    async def init(self, db: DataBase) -> DataPoint:
        self.fm = await FileManipulator(self.summary.uuid).init(db.conn)
        self.__parent = db
        return self
    
    @property
    def summary(self) -> DataPointSummary: return self.__summary
    @property
    def parent(self) -> DataBase: return self.__parent
    
    ## For qiuick access
    @property
    def time_added(self): return self.__summary.time_added
    @property
    def time_modified(self): return self.__summary.time_modified
    @property
    def uuid(self): return self.__summary.uuid
    @property
    def has_file(self): return self.__summary.has_file
    @property
    def tags(self): return DataTags(self.__summary.tags)
    @property
    def title(self): return self.__summary.title
    @property
    def year(self): return self.__summary.year
    @property
    def authors(self): return self.__summary.authors
    @property
    def publication(self): return self.__summary.publication
    
    # @deprecated
    async def stringInfo(self):
        summary = self.summary
        info_txt = \
        "\u27AA {title}\n\u27AA {year}\n\u27AA {authors}\n".format(title = summary.title, year = summary.year, authors = " \u2726 ".join(summary.authors))
        info_txt = info_txt + "\n\u27AA {publication}".format(publication = summary.publication)
        if self.has_file:
            info_txt = info_txt + "\nFile size: {}Bytes".format(await self.fm.getDocSize())
        return info_txt
    
    @classmethod
    def getAuthorsAbbr(cls, authors: List[str]):
        """
        Get authors abbreviation, i.e.:
            when only have one author: return the only author's first name
            otherwise return the first author's first name + et al.
        Author name abbreviation has a maximum length of self.MAX_AUTHOR_ABBR
        """
        if len(authors) == 1:
            author = cls._getFirstName(authors[0]) + "."
        else:
            author = cls._getFirstName(authors[0]) + " et al."
        if len(author) < cls.MAX_AUTHOR_ABBR:
            return author
        else:
            return author[:cls.MAX_AUTHOR_ABBR-4] + "..."

    @classmethod
    def _getFirstName(cls, name: str):
        x = name.split(", ")
        return x[0]
    
    def __str__(self) -> str:
        return f"{self.year}-{self.title}"
    
    __repr__ = __str__


SortType = Literal["year", "author", "time_added", "time_opened"]
def sortDataList(data_list: List[DataPoint], sort_by: SortType) -> List[DataPoint]:
    if sort_by == "year":
        return sorted(data_list, key = lambda x: int(x.year))
    elif sort_by == "author":
        return sorted(data_list, key = lambda x: x.authors[0])
    elif sort_by == "time_added":
        return sorted(data_list, key = lambda x: x.time_added)
    elif sort_by == "time_opened":
        return sorted(data_list, key = lambda x: x.time_modified)
    else:
        raise ValueError("Unknown sort type")

async def assembleDatapoint(raw_info: DBFileInfo, db: DataBase) -> DataPoint:

    # it's a bit tricky to get file information in one go
    _fm = await FileManipulator(raw_info["uuid"]).init(db.conn)     # type: ignore
    _file_size = await _fm.getDocSize()
    _has_file = True if _file_size > 0 else False
    _file_size = round(_file_size/(1048576), 2) if _has_file else 0 # convert to MB

    summary = DataPointSummary(
        doc_type = raw_info['type'], 
        has_file =_has_file,
        file_type=raw_info["doc_ext"],
        year = raw_info["year"],
        title = raw_info["title"],
        authors = raw_info["authors"],
        author = DataPoint.getAuthorsAbbr(raw_info["authors"]),
        publication=raw_info["publication"],
        tags = raw_info["tags"],
        uuid = raw_info["uuid"],
        url = raw_info["url"],
        time_added = raw_info["time_import"],
        time_modified = raw_info["time_modify"],
        bibtex = raw_info["bibtex"],
        doc_size= _file_size,
        note_linecount = len([line for line in raw_info["comments"].split("\n") if line.strip() != ""]),
        has_abstract= (abs_ := raw_info["abstract"].strip()) != "" and abs_ != "<Not avaliable>",
    )
    return await DataPoint(summary).init(db)

class DataBase(DataCore):
    @dataclasses.dataclass(frozen=True)
    class DatabasePath:
        main_dir: str
        file_dir: str
        index_dir: str
        summary_dir: str
        vector_db_file: str
    
    __thread_pool = ThreadPoolExecutor(max_workers=4)

    def __init__(self):
        super().__init__()
        self.__conn: DBConnection | None = None   # type: ignore
        self.__vector_db: VectorDatabase | None = None

    @property
    def conn(self) -> DBConnection:
        if self.__conn is None:
            raise RuntimeError("Database not initialized")
        return self.__conn
    
    async def init(self, db: str) -> DataBase:
        """
        - db: str | DBConnection, the database path or the database connection instance
        """
        assert isinstance(db, str), "Invalid input"     # type check
        if not os.path.exists(db):
            os.mkdir(db)
        # to prevent multiple loading of the same database
        conn = await FileManipulator.getDatabaseConnection(db) 
        self.__conn = conn      # set database-wise connection instance

        self.__vector_db = await VectorDatabase(self.path.vector_db_file, [
            {
                'name': 'doc_feature',
                'dimension': 768,
                'conent_type': 'TEXT'
            },
        ]).init()

        # create the file structure
        _path = self.path
        for p in [_path.file_dir, _path.index_dir, _path.summary_dir]:
            if not os.path.exists(p):
                os.mkdir(p)
        return self
    
    async def commit(self): 
        await asyncio.gather(self.conn.commit(), self.vector.commit())
    async def close(self):
        await asyncio.gather(self.conn.close(), self.vector.close())
        self.__conn = None

    @property
    def path(self):
        """
        Defines the file structure of the database, 
        will be used by other modules to access the files
            Database
            ├── lrs.db
            ├── index
            │     ├── vector.db
            │     └── summary
            |          └── ...
            └── files
                └── ...
        """
        if not os.path.exists(os.path.join(self.conn.db_dir, "index")):
            os.mkdir(os.path.join(self.conn.db_dir, "index"))
        return self.DatabasePath(
            main_dir = self.conn.db_dir,
            file_dir = os.path.join(self.conn.db_dir, "files"),
            index_dir = os.path.join(self.conn.db_dir, "index"),
            summary_dir = os.path.join(self.conn.db_dir, "index", "summary"),
            vector_db_file = os.path.join(self.conn.db_dir, "index", "vector_v1.db"),
        )
    
    @property
    def vector(self) -> VectorDatabase:
        if self.__vector_db is None:
            raise RuntimeError("Vector database not initialized")
        return self.__vector_db
    
    async def dump(self, include_files = False) -> bytes:
        """
        if include files, dump the database to a zip file. 
        else, dump the database to a sqlite file
        """
        dump_lock = asyncio.Lock()
        async with dump_lock:
            await self.conn.commit()

            if not include_files:
                with open(self.conn.db_path, "rb") as f:
                    return f.read()
            else:
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    # include the database file
                    db_fname = os.path.basename(self.conn.db_path)
                    zf.write(self.conn.db_path, db_fname)
                    # include the document files and attachments
                    for root, _, files in os.walk(self.path.file_dir):
                        for f in files:
                            zf.write(os.path.join(root, f), os.path.relpath(os.path.join(root, f), self.path.main_dir))
                return zip_buffer.getvalue()
    
    async def delete(self, uuid: str) -> bool:
        """ Delete a DataPoint by uuid"""
        if not await self.has(uuid):
            await self.logger.error(f"Data not found: {uuid}")
            return False
        await self.logger.info("Deleting {}".format(uuid))
        dp = await self.get(uuid)
        return await dp.fm.deleteEntry(create_backup=False)
    
    # query statistics
    async def count(self) -> int:
        return await self.conn.size()
    async def tags(self) -> DataTags:
        return DataTags(await self.conn.tags())
    async def authors(self) -> list[str]:
        return await self.conn.authors()
    async def keys(self) -> List[str]:
        return await self.conn.keys(sortby="time_import", reverse=True)
    async def has(self, uuid: str) -> bool:
        return await self.conn.get(uuid) is not None
    
    async def diskUsage(self) -> int:
        """ return the disk usage of the database in bytes """
        def _get_size(path: str) -> int:
            size = 0
            for root, _, files in os.walk(path):
                for f in files:
                    size += os.path.getsize(os.path.join(root, f))
            return size
        return await asyncio.get_event_loop().run_in_executor(self.__thread_pool, _get_size, self.path.main_dir)

    async def get(self, uuid: str) -> DataPoint:
        """ Get DataPoint by uuid """
        if (info := await self.conn.get(uuid)) is None:
            raise self.Error.LiresEntryNotFoundError(f"Data not found: {uuid}")
        return await assembleDatapoint(info, self)

    async def gets(self, uuids: list[str], sort_by='time_import', reverse = True) -> list[DataPoint]:
        """ Get DataPoints by uuids """
        conn = self.conn
        all_info = await conn.getMany(uuids, sort_by=sort_by, reverse=reverse)
        tasks = [assembleDatapoint(info, self) for info in all_info]
        return await asyncio.gather(*tasks)
    
    async def getAll(self, sort_by = 'time_import', reverse=True) -> list[DataPoint]:
        """ Get all DataPoints, may remove in the future """
        all_info = await self.conn.getAll(sort_by=sort_by, reverse=reverse)
        return await asyncio.gather(*[assembleDatapoint(info, self) for info in all_info])
    
    async def getIDByTags(self, tags: Union[list, set, DataTags], from_uids: Optional[List[str]] = None) -> list[str]:
        """
        Get DataPoints by tags, including all child tags
        """
        async def _getByStrictIntersect(tags: DataTags, from_uids: Optional[List[str]] = None) -> list[str]:
            return await self.conn.filter(from_uids=from_uids, tags=tags.toOrderedList())
        async def _getBySingle(tag: str, from_uids: Optional[List[str]] = None) -> list[str]:
            return await self.conn.filter(from_uids=from_uids, tags=[tag])

        all_tags = DataTags(await self.conn.tags())
        strict_query_tags = DataTags()                      # the exact tags to be queried
        relaxed_query_tag_groups: list[DataTags] = []       # the tags groups that will be relaxed by union of each group
        for t in tags:
            if len(_w_child_t:= DataTags([t]).withChildsFrom(all_tags))==1:
                strict_query_tags.add(_w_child_t.pop())
            else:
                relaxed_query_tag_groups.append(_w_child_t)
        # get all possible combinations
        to_be_intersect = [await _getByStrictIntersect(strict_query_tags, from_uids)]
        for r in relaxed_query_tag_groups:
            to_be_union: list[list[str]] = []
            for t in r:
                to_be_union.append(await _getBySingle(t, from_uids))
            to_be_intersect.append(list(set().union(*to_be_union)))
        # get the intersection
        if len(to_be_intersect) == 1:
            # return await self.gets(to_be_intersect[0])
            return to_be_intersect[0]
        else:
            return list(set(to_be_intersect[0]).intersection(*to_be_intersect[1:]))

    async def getDataByTags(self, tags: Union[list, set, DataTags], from_uids: Optional[List[str]] = None) -> list[DataPoint]:
        return await self.gets(await self.getIDByTags(tags, from_uids))
    
    async def renameTag(self, tag_old: str, tag_new: str) -> bool:
        """
        Rename a tag for the entire database
        return if success
        """
        data = await self.getDataByTags(DataTags([tag_old]))
        await self.logger.info(f"Rename tag: {tag_old} -> {tag_new} [count: {len(data)}]")
        tasks = []
        for d in data:
            d: DataPoint
            t = d.tags
            t = TagRule.renameTag(t, tag_old, tag_new)
            if t is not None:
                tasks.append(d.fm.writeTags(t))
        await asyncio.gather(*tasks)
        return True
    
    async def deleteTag(self, tag: str) -> bool:
        """
        Delete a tag for the entire database
        return if success
        """
        data = await self.getDataByTags(DataTags([tag]))
        await self.logger.info(f"Delete tag: {tag}")
        tasks = []
        for d in data:
            d: DataPoint
            ori_tags = d.tags
            after_deleted = TagRule.deleteTag(ori_tags, tag)
            if after_deleted is not None:
                tasks.append(d.fm.writeTags(after_deleted))
        await asyncio.gather(*tasks)
        return True