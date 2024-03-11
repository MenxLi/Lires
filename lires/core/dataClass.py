from __future__ import annotations
import os, asyncio
from typing import List, Union, Optional, Literal
from .dataTags import DataTags, TagRule
try:
    # may crash when generating config file withouot config file...
    # because getConf was used in constructing static variable
    from .fileTools import FileManipulator
    from .dbConn import DBFileInfo, DBConnection
except (FileNotFoundError, KeyError):
    pass
from .base import LiresBase
from .bibReader import parseBibtex, ParsedRef
from ..types.dataT import DataPointSummary
from ..utils import TimeUtils

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
        return self
    
    @property
    def summary(self) -> DataPointSummary:
        """ Generate datapoint info """
        return self.__summary
    
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
            info_txt = info_txt + "\nFile size: {}M".format(await self.fm.getDocSize())
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
    _fm = await FileManipulator(raw_info["uuid"]).init(db.conn)    # type: ignore
    _file_size = await _fm.getDocSize()
    _has_file = True if _file_size > 0 else False

    summary = DataPointSummary(
        has_file=_has_file,
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
    def __init__(self):
        super().__init__()
        self.__conn: DBConnection = None   # type: ignore

    @property
    def conn(self) -> DBConnection:
        if self.__conn is None:
            raise RuntimeError("Database not initialized")
        return self.__conn
    
    async def init(self, db: str | DBConnection) -> DataBase:
        if isinstance(db, DBConnection):
            assert not isinstance(db, str)  # type check only
            assert await db.isInitialized()
            self.__conn = db
            return self
        assert isinstance(db, str), "Invalid input"     # type check
        if not os.path.exists(db):
            os.mkdir(db)
        conn = await FileManipulator.getDatabaseConnection(db) 
        self.__conn = conn      # set database-wise connection instance
        return self
    
    async def delete(self, uuid: str) -> bool:
        """ Delete a DataPoint by uuid"""
        if not self.has(uuid):
            await self.logger.error(f"Data not found: {uuid}")
            return False
        await self.logger.info("Deleting {}".format(uuid))
        dp = await self.get(uuid)
        return await dp.fm.deleteEntry()
    
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
    async def get(self, uuid: str) -> DataPoint:
        """ Get DataPoint by uuid """
        if (info := await self.conn.get(uuid)) is None:
            raise self.Error.LiresEntryNotFoundError(f"Data not found: {uuid}")
        return await assembleDatapoint(info, self)

    async def gets(self, uuids: list[str]) -> list[DataPoint]:
        """ Get DataPoints by uuids """
        conn = self.conn
        all_info = await conn.getMany(uuids)
        tasks = [assembleDatapoint(info, self) for info in all_info]
        return await asyncio.gather(*tasks)
    
    async def getAll(self) -> list[DataPoint]:
        """ Get all DataPoints, may remove in the future """
        all_info = await self.conn.getAll()
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