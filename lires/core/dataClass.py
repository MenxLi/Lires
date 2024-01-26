from __future__ import annotations
import os
from typing import List, Union, Set, Dict, Optional, Sequence, overload, TypeVar, Literal
import difflib
from ..utils import Timer
try:
    # may crash when generating config file withouot config file...
    # because getConf was used in constructing static variable
    from .fileTools import FileManipulator
    from .dbConn import DBFileInfo
except (FileNotFoundError, KeyError):
    pass
from .base import LiresBase
from .bibReader import parseBibtex, ParsedRef
from ..types.dataT import DataPointSummary

class DataCore(LiresBase):
    logger = LiresBase.loggers().core

class TagRule(DataCore):
    SEP = "->"
    @classmethod
    def allParentsOf(cls, tag: str) -> DataTags:
        """
        assume cls.SEP is '.'
        input: a.b.c
        return: [a, a.b]
        """
        sp = tag.split(cls.SEP)
        if len(sp) == 1:
            return DataTags([])
        accum = []
        all_p_tags = []
        for i in range(0, len(sp)-1):
            accum += [sp[i]]
            all_p_tags.append(cls.SEP.join(accum))
        return DataTags(all_p_tags)
    
    @classmethod
    def allChildsOf(cls, tag: str, tag_pool: Sequence[str] | DataTags) -> DataTags:
        """
        assume cls.SEP is '.'
        input: (a.b, [a, a.b, a.b.c, a.b.d])
        return: [a.b.c, a.b.d]
        """
        ret = []
        for t in tag_pool:
            if t.startswith(tag) and len(t)>len(tag)+len(cls.SEP):
                if t[len(tag): len(tag) + 2] == cls.SEP:
                    ret.append(t)
        return DataTags(ret)
    
    @classmethod
    def renameTag(cls, src: DataTags, aim_tag: str, new_tag: str) -> Optional[DataTags]:
        """
        return None if tag not in src nor it's all parent tags
        otherwise:
            for tag in src:
                if tag is the aim_tag:
                    change tag to new_tag
                if aim_tag is in the tag's parent tags: 
                    change the parent tag
                    ( e.g. <cls.SEP='.'> tag: a.b.c, aim_tag: a.b, new_tag: d,
                        change the tag to b.c)
                else:
                    keep the tag same
        """
        aim_tag = cls.stripTag(aim_tag)
        new_tag = cls.stripTag(new_tag)

        if aim_tag not in src.withParents():
            return None

        out_tags = []
        for tag in src:
            # first determine if tag is a intermediate node
            if tag == aim_tag:
                out_tags.append(new_tag)
            elif tag.startswith(aim_tag):
                tag = new_tag + tag[len(aim_tag):]
                out_tags.append(tag)
            else:
                out_tags.append(tag)
        return DataTags(out_tags)
    
    @classmethod
    def deleteTag(cls, src: DataTags, aim_tag: str) -> Optional[DataTags]:
        """
        delete aim_tag, as well as it's all child tags from src
        return None if none of tags in src in aim_tag and it's child tags
        e.g. 
            <cls.SEP='.'>
            src: (a.b, a.b.c, b.c)
            aim_tag: a.b
            return - (b.c)
        """
        _delete_something = False
        out_tags = []
        may_delete = DataTags([aim_tag]).withChildsFrom(src)
        for t in src:
            if t in may_delete:
                _delete_something = True
                continue
            out_tags.append(t)
        if _delete_something:
            return DataTags(out_tags)
        else:
            return None
    
    @classmethod
    def stripTag(cls, tag: str) -> str:
        tag_sp = tag.split(cls.SEP)
        tag_sp = [t.strip() for t in tag_sp]
        return cls.SEP.join(tag_sp)

    @classmethod
    def stripTags_(cls, tags: DataTagT_G) -> DataTagT_G:
        """in place operation"""
        if isinstance(tags, set):
            for t in tags:
                stripped = cls.stripTag(t)
                if stripped == t:
                    continue
                tags.remove(t)
                tags.add(stripped)  # type: ignore
        else:
            for i in range(len(tags)):
                tags[i] = cls.stripTag(tags[i])
        return tags

class DataTags(Set[str], DataCore):
    @overload
    def __init__(self):...
    @overload
    def __init__(self, arg: DataTagT):...

    def __init__(self, arg: Union[DataTagT, None] = None):
        if arg is None:
            super().__init__()
        elif isinstance(arg, DataTags):
            super().__init__(arg)
        else:
            super().__init__(TagRule.stripTags_(arg))

    def toOrderedList(self):
        ordered_list = list(self)
        ordered_list.sort()
        return ordered_list
    
    def union(self, *s: Set|DataTags|list) -> DataTags:
        return DataTags(super().union(*s))
    
    def withParents(self) -> DataTags:
        parents = DataTags()
        for s in self:
            parents = parents.union(TagRule.allParentsOf(s))
        return self.union(parents)

    def withChildsFrom(self, child_choices: DataTags):
        childs = DataTags()
        for s in self:
            childs = childs.union(TagRule.allChildsOf(s, child_choices))
        return self.union(childs) # type: ignore
    
    def toStr(self):
        if len(self) > 0:
            return "; ".join(self.toOrderedList())
        else:
            return "<None>"

DataTagT = Union[DataTags, List[str], Set[str]]
DataTagT_G = TypeVar('DataTagT_G', bound=DataTagT)

class DataPoint(DataCore):
    """
    A buffer that holds parsed information of a single data
    """
    MAX_AUTHOR_ABBR = 36
    def __init__(self, fm: FileManipulator):
        """
        The basic data structure that holds single data
        fm - FileManipulator, data completeness should be confirmed ahead (use fm.screen())
        """
        self.fm = fm
        self.__summary: DataPointSummary | None = None
    
    @property
    def summary(self) -> DataPointSummary:
        """
        Generate datapoint info
        """
        assert self.__summary is not None
        return self.__summary

    async def filePath(self) -> Optional[str]:
        return await self.fm.filePath()

    async def reload(self):
        await self.loadInfo()

    async def loadInfo(self, parse_bibtex=True) -> DataPoint:
        """
        Parse bibtex and other info into the memory
        """
        self.has_file = await self.fm.hasFile()
        self.uuid = self.fm.uuid
        self.tags = DataTags(await self.fm.getTags())

        self.time_added = await self.fm.getTimeAdded()
        self.time_modified = await self.fm.getTimeModified()

        if parse_bibtex:
            self.loadParsedBibtex_(await parseBibtex(await self.fm.readBib()))

        self.__summary = DataPointSummary(**{
            "has_file": self.has_file,
            "file_type": await self.fm.fileExt(),
            "year":self.year,
            "title":self.title,
            "author":self.getAuthorsAbbr(),
            "authors": self.authors,
            "publication": self.publication,
            "tags":list(self.tags),
            "uuid":self.uuid,
            "url":await self.fm.getWebUrl(),
            "time_added": await self.fm.getTimeAdded(),
            "time_modified": await self.fm.getTimeModified(),
            "bibtex": await self.fm.readBib(),
            "doc_size": await self.fm.getDocSize(),
            "note_linecount": len([line for line in (await self.fm.readComments()).split("\n") if line.strip() != ""]),
            "has_abstract": (abs_ := (await self.fm.readAbstract()).strip()) != "" and abs_ != "<Not avaliable>",
        })
        return self
    
    
    def loadParsedBibtex_(self, parsed_bibtex: ParsedRef):
        self.bib = parsed_bibtex["bib"]
        self.title = parsed_bibtex["title"]
        self.year = parsed_bibtex["year"]
        self.authors = parsed_bibtex["authors"]
        self.publication = parsed_bibtex["publication"]


    async def changeBib(self, bib_str: str) -> bool:
        """
        Change bibtex info
        - bib_str: bibtex string
        return if success
        """
        ret = bool(await self.fm.writeBib(bib_str))
        # update datapoint
        await self.reload()
        return ret
    
    async def addFile(self, extern_file_p: str) -> bool:
        """
        Add document to this data, 
        Will only work if the file is in local and not have document file
        return if success
        """
        return await self.fm.addFile(extern_file_p)
    
    async def changeTags(self, new_tags: DataTags):
        await self.fm.writeTags(new_tags)
        self.tags = new_tags
    
    async def stringInfo(self):
        bib = self.bib

        info_txt = \
        "\u27AA {title}\n\u27AA {year}\n\u27AA {authors}\n".format(title = bib["title"], year = bib["year"], authors = " \u2726 ".join(bib["authors"]))
        if "journal"  in bib:
            info_txt = info_txt + "{icon} {journal}".format(icon = u"\U0001F56e", journal = bib["journal"][0])
        elif "booktitle" in bib:
            info_txt = info_txt + "{icon} {booktitle}".format(icon = u"\U0001F56e", booktitle = bib["booktitle"][0])
        if self.has_file:
            info_txt = info_txt + "\nFile size: {}M".format(await self.fm.getDocSize())
        info_txt = "--{}--\n".format(bib["type"]) + info_txt
        return info_txt
    
    def getFileStatusStr(self):
        """
        Unicode icon indicate if the datapoint contains file
        """
        if self.has_file:
            return "\u2726"
        else:
            return "\u2727"

    def getAuthorsAbbr(self):
        """
        Get authors abbreviation, i.e.:
            when only have one author: return the only author's first name
            otherwise return the first author's first name + et al.
        Author name abbreviation has a maximum length of self.MAX_AUTHOR_ABBR
        """
        if len(self.authors) == 1:
            author = self._getFirstName(self.authors[0]) + "."
        else:
            author = self._getFirstName(self.authors[0]) + " et al."
        if len(author) < self.MAX_AUTHOR_ABBR:
            return author
        else:
            return author[:self.MAX_AUTHOR_ABBR-4] + "..."

    def _getFirstName(self, name: str):
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

class DataBase(Dict[str, DataPoint], DataCore):
    def __init__(self, local_path: Optional[str] = None):
        super().__init__()
        self.__conn = None

    async def destroy(self):
        """
        Make sure all datapoint is deleted from database
        """
        for k in self.uuids:
            del self[k]
        await self.logger.debug("Closing DataBase's DBConnection")
        if self.__conn is not None:
            await self.__conn.close()
            del self.__conn
            self.__conn = None
        await self.logger.debug("Deleted DataBase object")

    @property
    def conn(self):
        if self.__conn is None:
            raise RuntimeError("Database not initialized")
        return self.__conn
    
    async def init(self, db_local: str) -> DataBase:
        """ An abstraction of self.construct """
        if not os.path.exists(db_local):
            os.mkdir(db_local)
        conn = await FileManipulator.getDatabaseConnection(db_local) 
        self.__conn = conn      # set database-wise connection instance
        await self.logger.debug("Initializing new DataBase's DBConnection")
        if db_local:
            # when load database is provided
            to_load = await conn.keys()
            await self.constuct(to_load)
        return self     # enable chaining initialization

    async def constuct(self, vs: List[str]):
        """
        Construct the DataBase (Add new entries to database)
         - vs: list of data uuids
        """
        all_data: list[DataPoint] = []
        for v_ in vs:
            fm = await FileManipulator(v_).init(self.conn)
            data = await DataPoint(fm).loadInfo()
            all_data.append(data)

            # _all_parsed_bibtex = parallelParseBibtex(_all_bibtex)
            # for d, parsed_bib in zip(all_data, _all_parsed_bibtex):
            #     d.loadParsedBibtex_(parsed_bib)
        # add to database
        for d_ in all_data:
            if d_ is not None:
                await self.add(d_)

    async def add(self, data: Union[DataPoint, str]) -> DataPoint:
        """
        Add a data to the DataBase
         - data: DataPoint or uid
        return DataPoint
        """
        if isinstance(data, str):
            # uid of the data
            fm = await FileManipulator(data).init(self.conn)
            data = await DataPoint(fm).loadInfo()
        self[data.uuid] = data
        return data
    
    async def delete(self, uuid: str) -> bool:
        """
        Delete a DataPoint by uuid,
        will delete remote data if in online mode and remote data exists
        """
        await self.logger.info("Deleting {}".format(uuid))
        if uuid in self.keys():
            dp: DataPoint = self[uuid]
            res = await dp.fm.deleteEntry()
            del self[uuid]
            return res
        return False

    @property
    def total_tags(self) -> DataTags:
        tags = DataTags([])
        for d in self.values():
            tags = tags.union(d.tags)
        return tags
    
    @property
    def uuids(self) -> List[str]:
        return list(self.keys())
    
    def getDataByTags(self, tags: Union[list, set, DataTags], from_uids: Optional[List[str]] = None) -> list[DataPoint]:
        datalist = []
        for data in self.values():
            if not from_uids is None:
                # filter by uids (for searching purposes)
                if data.uuid not in from_uids:
                    continue
            tag_data = DataTags(data.tags)
            tags = DataTags(tags)
            if tags.issubset(tag_data.withParents()):
                datalist.append(data)
        return datalist
    
    async def renameTag(self, tag_old: str, tag_new: str) -> bool:
        """
        Rename a tag for the entire database
        return if success
        """
        data = self.getDataByTags(DataTags([tag_old]))
        await self.logger.info(f"Rename tag: {tag_old} -> {tag_new}")
        for d in data:
            d: DataPoint
            t = d.tags
            t = TagRule.renameTag(t, tag_old, tag_new)
            if t is not None:
                await d.changeTags(t)
        return True
    
    async def deleteTag(self, tag: str) -> bool:
        """
        Delete a tag for the entire database
        return if success
        """
        data = self.getDataByTags(DataTags([tag]))
        await self.logger.info(f"Delete tag: {tag}")
        for d in data:
            d: DataPoint
            ori_tags = d.tags
            after_deleted = TagRule.deleteTag(ori_tags, tag)
            if after_deleted is not None:
                await d.changeTags(after_deleted)
        return True

    async def findSimilarByBib(self, bib_str: str) -> Optional[DataPoint]:
        """
        Check if similar file already exists.
        """
        # Check if the file already exists
        t2 = (await parseBibtex(bib_str))["title"]
        for _, v in self.items():
            t1 = v.title
            similarity = difflib.SequenceMatcher(a = t1, b = t2).ratio()
            if similarity > 0.8:
                return v
        return None