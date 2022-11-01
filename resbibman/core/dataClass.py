from __future__ import annotations
import logging
import urllib.parse
import shutil, requests, json
from ..confReader import getConfV, ASSETS_PATH
import typing, re, string, os, asyncio
from typing import List, Union, Set, TYPE_CHECKING, Dict, Type, Optional, TypedDict, Sequence, overload
import difflib
import markdown
from .fileTools import FileGenerator
from .utils import formatMarkdownHTML, TimeUtils
from .clInteractions import ChoicePromptAbstract
from ..perf.asynciolib import asyncioLoopRun
try:
    # may crash when generating config file withouot config file...
    # because getConf was used in constructing static variable
    from .fileToolsV import FileManipulatorVirtual
except (FileNotFoundError, KeyError):
    pass
from .bibReader import BibParser
#  from .utils import HTML_TEMPLATE_RAW
from .encryptClient import generateHexHash
from . import globalVar as G

from QCollapsibleCheckList import DataItemAbstract as CollapsibleChecklistDataItemAbstract

if TYPE_CHECKING:
    from RBMWeb.backend.rbmlibs import DataPointInfo

class DataPointInfo(TypedDict):
    has_file: bool
    file_status: str
    file_type: str
    year: typing.Any
    title: str
    author: str
    authors: List[str]
    tags: List[str]
    uuid: str
    url: str
    time_added: float
    time_modified: float
    bibtex: str
    doc_size: float # in M.
    base_name: str  # for directory name

class DataCore:
    logger = G.logger_rbm

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
            return []
        accum = []
        all_p_tags = []
        for i in range(0, len(sp)-1):
            accum += [sp[i]]
            all_p_tags.append(cls.SEP.join(accum))
        return DataTags(all_p_tags)
    
    @classmethod
    def allChildsOf(cls, tag: str, tag_pool: Sequence[str]) -> DataTags:
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
    def stripTags_(cls, tags: Sequence[str]) -> Sequence[str]:
        """in place operation"""
        if isinstance(tags, set):
            for t in tags:
                stripped = cls.stripTag(t)
                if stripped == t:
                    continue
                tags.remove(t)
                tags.add(stripped)
        else:
            for i in range(len(tags)):
                tags[i] = cls.stripTag(tags[i])
        return tags

class DataTags(Set[str], DataCore):
    @overload
    def __init__(self):...
    @overload
    def __init__(self, s: Sequence[str]):...
    @overload
    def __init__(self, s: DataTags):...

    def __init__(self, arg: Union[Sequence[str], DataTags, None] = None):
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
    
    def union(self, *s) -> DataTags:
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
        return self.union(childs)
    
    def toStr(self):
        if len(self) > 0:
            return "; ".join(self.toOrderedList())
        else:
            return "<None>"

class DataPoint(DataCore):
    MAX_AUTHOR_ABBR = 18
    def __init__(self, fm: FileManipulatorVirtual):
        """
        The basic data structure that holds single data
        fm - FileManipulator, data completeness should be confirmed ahead (use fm.screen())
        """
        self.fm = fm
        self.__parent_db: DataBase
        self.__force_offline = False
        self.loadInfo()

    @property
    def data_path(self):
        return self.fm.path

    @property
    def info(self) -> DataPointInfo:
        """
        Generate datapoint info
        """
        return {
            "has_file":self.fm.hasFile(),
            "file_status":self.getFileStatusStr(),
            "file_type": self.fm.file_extension,
            "year":self.year,
            "title":self.title,
            "author":self.getAuthorsAbbr(),
            "authors": self.authors,
            "tags":list(self.tags),
            "uuid":self.uuid,
            "url":self.fm.getWebUrl(),
            "time_added": self.fm.getTimeAdded(),
            "time_modified": self.fm.getTimeModified(),

            "bibtex": self.fm.readBib(),
            "doc_size": self.fm.getDocSize(),
            "base_name": self.fm.base_name,
        }
    
    def _forceOffline(self):
        """
        Will be called when run on server side or failed to connect to the server
        """
        self.__force_offline = True
        self.fm._forceOffline()

    def setPromptObj(self, prompt_obj: ChoicePromptAbstract):
        """
        User prompt method set with GUI modules
        """
        self.fm.prompt_obj = prompt_obj
    
    def sync(self) -> bool:
        """
        Synchronize,
        if the data is in remote, call self.fm._sync to check if is up-to-date and upload/dowload or do nothing
        else if the data is new, upload to the remote
        (if in offline mode, self.fm._sync will fail thus return False)
        return if success
        """
        if self.uuid in self.par_db.remote_info:
            remote_info = self.par_db.remote_info[self.uuid]
            self.fm.v_info = remote_info
            SUCCESS = self.fm._sync()
        else:
            # New data that remote don't have
            self.logger.info("Creating new data remote {}".format(self.uuid))
            SUCCESS = self.fm._uploadRemote()
        if SUCCESS:
            # update local virtual info
            self.fm.v_info = self.info
        return SUCCESS

    @property
    def par_db(self) -> DataBase:
        return self.__parent_db
    
    @par_db.setter
    def par_db(self, db: DataBase):
        if not hasattr(self, "__parent_db"):
            self.__parent_db = db
        else:
            self.par_db.logger.warn("Can't re-assign database for datapoint: {}".format(self))
    
    @property
    def is_local(self):
        if self.__force_offline:
            return True
        return self.fm.has_local

    @property
    def file_path(self) -> Union[None, str]:
        return self.fm.file_p

    def reload(self):
        _re_watch = False
        if self.fm.has_local:
            if self.fm.is_watched:
                # The old observer may not be stopped (because it's in another thread),
                # so unwatch file changes, otherwise may endup in 2 file observers,
                # and the old one can't be unwatched because we lost reference to it
                self.logger.debug("de-watching {}".format(self.uuid))
                self.fm.setWatch(False)
                _re_watch = True
            self.fm = FileManipulatorVirtual(self.data_path, prompt_obj = self.fm.prompt_obj)
            if not self.par_db.offline:
                # set up a v_info
                if self.uuid in self.par_db.remote_info.keys():
                    self.fm.v_info = self.par_db.remote_info[self.uuid]
                else:
                    ...
        else:
            # to decide later
            pass
        if self.__force_offline:
            self.fm._forceOffline()
        self.fm.screen()
        # set watch to True, because we may have un-watched it
        if _re_watch:
            self.logger.debug("re-watching {}".format(self.uuid))
            self.fm.setWatch(True)
        self.loadInfo()

    def loadInfo(self):
        #  self.logger.debug("Loading info for: {}".format(self.data_path))
        self.has_file = self.fm.hasFile()
        self.bib = BibParser()(self.fm.readBib())[0]
        self.uuid = self.fm.getUuid()
        self.tags = DataTags(self.fm.getTags())
        self.title = self.bib["title"]
        self.authors = self.bib["authors"]
        self.year = self.bib["year"]
        self.time_added = self.fm.getTimeAdded()
        self.time_modified = self.fm.getTimeModified()

    def changeBib(self, bib_str: str) -> bool:
        """
        **
            May encounter permission error if any program is using the file
            should prompt closing the file before this operation
        **
        Change bibtex info
        - bib_str: bibtex string
        return if base_name changed
        """
        self.fm.writeBib(bib_str)
        bib = BibParser()(bib_str)[0]
        fg = FileGenerator(None, 
                           title = bib["title"], 
                           authors = bib["authors"], 
                           year = bib["year"])
        # maybe change base_name
        base_name_changed = self.fm.changeBasename(fg.base_name)
        # update datapoint
        self.reload()
        return base_name_changed
    
    def addFile(self, extern_file_p: str) -> bool:
        """
        Add document to this data, 
        Will only work if the file is in local and not have document file
        return if success
        """
        return self.fm.addFile(extern_file_p)
    
    def changeTags(self, new_tags: DataTags):
        self.fm.writeTags(list(new_tags))
        self.tags = new_tags
    
    def stringInfo(self):
        bib = self.bib

        info_txt = \
        "\u27AA {title}\n\u27AA {year}\n\u27AA {authors}\n".format(title = bib["title"], year = bib["year"], authors = " \u2726 ".join(bib["authors"]))
        if "journal"  in bib:
            info_txt = info_txt + "{icon} {journal}".format(icon = u"\U0001F56e", journal = bib["journal"][0])
        elif "booktitle" in bib:
            info_txt = info_txt + "{icon} {booktitle}".format(icon = u"\U0001F56e", booktitle = bib["booktitle"][0])
        if self.has_file:
            info_txt = info_txt + "\nFile size: {}M".format(self.fm.getDocSize())
        info_txt = "--{}--\n".format(bib["type"]) + info_txt
        return info_txt
    
    def screenByPattern(self, pattern) -> bool:
        """
        Return if the self.stringInfo meets the regex pattern
        """
        # string = self.title+";"+";".join(self.authors)+";"+self.year
        string = self.stringInfo() + "\n" + self.uuid
        string = string.lower()
        pattern = pattern.lower()
        result = re.search(pattern, string)
        if result is None:
            return False
        else: return True

    def htmlComment(self, abs_fpath: bool = True) -> str:
        """
        - abs_fpath: whether to use absolute path to any file in the html
        """
        self.logger.debug("htmlComment (DataPoint): render comment")
        comment = self.fm.readComments()
        if comment == "":
            return ""
        misc_f = self.fm.folder_p
        misc_f = misc_f.replace(os.sep, "/")
        if abs_fpath:
            comment = comment.replace("./misc", misc_f)

        comment_html = markdown.markdown(comment)
        #  comment_html = self.COMMENT_HTML_TEMPLATE.substitute(\
        #                  content = comment_html, style = self.COMMENT_CSS)
        return formatMarkdownHTML(comment_html, abs_fpath = abs_fpath)

    def getFileStatusStr(self):
        """
        Unicode icon indicate if the datapoint contains file
        """
        if self.has_file:
            if self.is_local:
                return "\u2726"
            else:
                return "\u2726"
                # return "\u29bf"
        else:
            if self.is_local:
                return "\u2727"
            else:
                return "\u2727"
                # return "\u29be"

    def stringCitation(self):
        """
        Generate citation string, should be adapted to more formats in the future
        """
        bib = self.bib
        title = bib["title"]
        year = bib["year"]
        string = f"{self.getAuthorsAbbr()} {title}. ({year})"
        if "journal" in bib:
            string += ". {}".format(bib["journal"][0])
        elif "booktitle" in bib:
            string += ". {}".format(bib["booktitle"][0])
        string += "."
        return string

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

class DataList(List[DataPoint], DataCore):
    SORT_YEAR = "Year"
    SORT_AUTHOR = "Author"
    SORT_TIMEADDED = "Time added"
    SORT_TIMEOPENED = "Time opened"
    TB_HEADER = {
        0: "Year",
        1: "Author",
        2: "Title"
    }
    TB_FUNCS = {
        0: lambda x: x.year,
        1: lambda x: x.getAuthorsAbbr(),
        2: lambda x: x.title
    }
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def sortBy(self, mode, reverse: bool = False):
        if mode == self.SORT_AUTHOR:
            return self.sort(key = lambda x: x.authors[0], reverse = reverse)
        elif mode == self.SORT_YEAR:
            return self.sort(key = lambda x: int(x.year), reverse = reverse)
        elif mode == self.SORT_TIMEADDED:
            return self.sort(key = lambda x: x.time_added, reverse = reverse)
        elif mode == self.SORT_TIMEOPENED:
            return self.sort(key = lambda x: x.time_modified, reverse = reverse)

    def reloadFromFile(self, idx):
        self[idx].reload()
    
    def getTable(self):
        pass

    # def getTableItem(self, row: int, col: int) -> str:
        # data = self[row]
        # return DataList.TB_FUNCS[col](data)

    # def getTableHeaderItem(self, col: int) -> str:
        # return self.TB_HEADER[col]

class DataTableList(DataList, DataCore):
    HEADER_FILESTATUS = "File status"
    HEADER_YEAR = "Year"
    HEADER_AUTHOR = "Author"
    HEADER_TITLE = "Title"
    HEADER_TIMEMODIFY = "Time modified"
    _HEADER_FUNCS = {
        HEADER_FILESTATUS: lambda x: x.getFileStatusStr(),
        HEADER_YEAR: lambda x: x.year,
        HEADER_AUTHOR: lambda x: x.getAuthorsAbbr(),
        HEADER_TITLE: lambda x: x.title,
        HEADER_TIMEMODIFY: lambda x: TimeUtils.toStr(TimeUtils.stamp2Local(x.time_modified))
    }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.header_order = getConfV("table_headers")

    def getTableItem(self, row: int, col: int) -> str:
        data = self[row]
        return DataTableList._HEADER_FUNCS[self.header_order[col]](data)

    def getTableHeaderItem(self, col: int) -> str:
        return self.header_order[col]

class DataBase(Dict[str, DataPoint], DataCore):

    @property
    def offline(self) -> bool:
        if hasattr(self, "_force_offline") and self._force_offline:
            return True
        return getConfV("host") == ""

    @property
    def n_local(self):
        """Number of local files"""
        count = 0
        for uuid, dp in self.items():
            if dp.is_local:
                count += 1
        return count
    
    @property
    def remote_info(self)-> Dict[str, DataPointInfo]:
        d = dict()
        for f_info in self.__file_list_remote:
            d[f_info["uuid"]] = f_info
        return d

    def init(self, db_local = "", force_offline = False):
        """
        An abstraction of self.construct, load both db_local and remote server
        reset offline status
        """
        self._force_offline = force_offline
        if not self.offline:
            flist = self.fetch()
            if flist is None:
                # None indicate an server error
                asyncioLoopRun(self.constuct([], force_offline=True))
            else:
                # server may be back when reload (re-call self.init)
                asyncioLoopRun(self.constuct(flist, force_offline=self._force_offline))
        if db_local:
            # when load database is provided
            to_load = []
            for f in os.listdir(db_local):
                f_path = os.path.join(db_local, f)
                if os.path.isdir(f_path):
                    to_load.append(f_path)
            asyncioLoopRun(self.constuct(to_load))

    async def constuct(self, vs: Union[List[str], List[DataPointInfo]], force_offline = False):
        """
        Construct the DataBase (Add new entries to database)
         - vs: list of DataPointInfo or local data directories
         - force_offline: use when called by server side
                         or when server is down
        """
        async def _getDataPoint(v_, force_offline_: bool) -> Union[DataPoint, None]:
            fm = FileManipulatorVirtual(v_)
            if fm.screen():
                # this process, if in local mode, is IO-bounded (DataPoint.loadInfo)
                data = DataPoint(fm)
                if force_offline_:
                    data._forceOffline()
            else:
                data = None
            return data

        # load all datapoint
        async_tasks = []
        for v in vs:
            async_tasks.append(_getDataPoint(v, force_offline))
        all_data = await asyncio.gather(*async_tasks)
        # add to database
        for d_ in all_data:
            if d_ is not None:
                self.add(d_)
        if force_offline:
            self._force_offline = True

    def fetch(self) -> Union[List[DataPointInfo], None]:
        """
        update self.remote_info
        will not change data
        return None for failed fetching
        return Union[List[DataPointInfo], None]
        """
        if self.offline:
            self.logger.info("Offline mode, can't fetch database")
            return None

        addr = "http://{}:{}".format(getConfV("host"), getConfV("port"))
        params = {
            "tags":""
        }
        flist_addr = "{}/filelist?{}".format(addr, urllib.parse.urlencode(params)) 

        try:
            res = requests.get(flist_addr)
            if res.status_code != 200:
                self.logger.info("Faild to fetch remote data ({})".format(res.status_code))
                return None
        except requests.exceptions.ConnectionError:
            self.logger.warning("Server is down, abort fetching remote data.")
            return None
        
        flist = res.text
        flist = json.loads(flist)["data"]
        self.__file_list_remote = flist
        return flist

    def add(self, data: Union[DataPoint, str]) -> DataPoint:
        """
        Add a data to the DataBase
         - data: DataPoint or path to the local data directory
        return DataPoint
        """
        if isinstance(data, str):
            # path to the data folder
            assert os.path.exists(data)
            fm = FileManipulatorVirtual(data)
            fm.screen()
            data = DataPoint(fm)
        data.par_db = self
        self[data.uuid] = data
        return data
    
    def delete(self, uuid: str):
        """
        Delete a DataPoint by uuid,
        will delete remote data if in online mode and remote data exists
        """
        if uuid in self.keys():
            dp: DataPoint = self[uuid]
            if dp.fm.has_local:
                dp.fm.setWatch(False)
                shutil.rmtree(dp.data_path)
            if not self.offline:
                # If remote has this data, delete remote as well, 
                # otherwise it will be downloaded again when sync
                if not dp.fm._deleteRemote():
                    self.logger.info("Oops, the data on the server side may not be deleted")
                    self.logger.warn("You may need to sync->delete again for {}".format(dp))
            del self[uuid]

    def watchFileChange(self, v: List[Union[DataPoint, str]]):
        """
        Watch file status change
        Will restrict watch only to the input, unwatch all others
         - v: list of uuid or DataPoint
        """
        for uuid, dp in self.items():
            dp: DataPoint
            if dp.fm.is_watched:
                dp.fm.setWatch(False)
        for v_ in v:
            if isinstance(v_, DataPoint):
                v_.fm.setWatch(True)
            else:
                self[v_].setWatch(True)
        return

    @property
    def total_tags(self) -> DataTags:
        tags = DataTags([])
        for d in self.values():
            tags = tags.union(d.tags)
        return tags
    
    def getDataByTags(self, tags: Union[list, set, DataTags]) -> DataList:
        datalist = DataList()
        for data in self.values():
            tag_data = DataTags(data.tags)
            tags = DataTags(tags)
            if tags.issubset(tag_data.withParents()):
                datalist.append(data)
        return datalist
    
    def renameTag(self, tag_old: str, tag_new: str) -> bool:
        """
        Rename a tag for the entire database
        return if success
        """
        data = self.getDataByTags(DataTags([tag_old]))
        if not self.offline:
            if not self.allUptodate():
                self.logger.warning("Rename failed, remote file is advance than local, solve conflict before renaming")
                return False
            # request remote tag change
            post_args = {
                "key": generateHexHash(getConfV("access_key")),
                "cmd": "renameTagAll",
                "uuid": "_",
                "args": json.dumps([tag_old, tag_new]),
                "kwargs": json.dumps({})
            }
            if not self.remoteCMD(post_args):
                self.logger.info("Abort renaming")
                return False

        # change local tag
        # (After remote change so local is always updated than remote)
        self.logger.info(f"Renaming local tag: {tag_old} -> {tag_new}")
        for d in data:
            d: DataPoint
            t = d.tags
            t = TagRule.renameTag(t, tag_old, tag_new)
            if t is not None:
                d.changeTags(t)
        return True
    
    def deleteTag(self, tag: str) -> bool:
        """
        Delete a tag for the entire database
        return if success
        """
        data = self.getDataByTags(DataTags([tag]))
        if not self.offline:
            if not self.allUptodate():
                self.logger.warning("Delete tag failed, remote file is advance than local, solve conflict before deleting tag")
                return False
            # request remote tag delete
            post_args = {
                "key": generateHexHash(getConfV("access_key")),
                "cmd": "deleteTagAll",
                "uuid": "_",
                "args": json.dumps([tag]),
                "kwargs": json.dumps({})
            }
            if not self.remoteCMD(post_args):
                self.logger.info("Abort deleting tag")
                return False

        # delete local tag
        # (After remote delete so local is always updated than remote)
        self.logger.info(f"Deleting local tag: {tag}")
        for d in data:
            d: DataPoint
            ori_tags = d.tags
            after_deleted = TagRule.deleteTag(ori_tags, tag)
            if after_deleted is not None:
                d.changeTags(after_deleted)
        return True

    def findSimilarByBib(self, bib_str: str) -> Union[None, DataPoint]:
        """
        Check if similar file already exists.
        """
        parser = BibParser(mode = "single")
        bib = parser(bib_str)[0]
        # Check if the file already exists
        for k, v in self.items():
            t1 = v.bib["title"].lower()
            t2 = bib["title"].lower()
            similarity = difflib.SequenceMatcher(a = t1, b = t2).ratio()
            if similarity > 0.8:
                return v
        return None

    def remoteCMD(self, post_args) -> bool:
        """
        post command to remote/cmdA
        """
        if self.offline:
            return False
        addr = "http://{}:{}".format(getConfV("host"), getConfV("port"))
        post_addr = "{}/cmdA".format(addr) 
        res = requests.post(post_addr, params = post_args)
        if not res.ok:
            self.logger.info(f"failed requesting {post_addr} ({res.status_code}).")
            return False
        return True

    def allUptodate(self, fetch: bool = True, strict: bool = False) -> bool:
        """
        Return if all data points in local are up-to-date with remote
         - fetch (bool): whether to perform self.fetch()
         - strict (bool): only return true if all data points are the same as remote,
            Otherwise will return true if all data points are same/advance than remote
        """
        if self.offline:
            return True
        # udpate remote file info
        if fetch:
            self.fetch()
        for d in self.values():
            d: DataPoint
            remote_info = self.remote_info
            if d.is_local:
                # update file manipulator v_info to the same with remote
                if fetch: d.fm.v_info = remote_info[d.uuid]
                if d.fm.is_uptodate == "behind":
                    self.logger.info(f"allUptodate (database): data({d.uuid}) is behind remote")
                    return False
                if strict and d.fm.is_uptodate == "advance":
                    self.logger.info(f"allUptodate (database): data({d.uuid}) is advance than remote")
                    return False
        return True

    def exportFiles(self, uids: List[str], dst: str):
        """
        Copy data folders to dst
         - uids: data uids to export
         - dst: destination folder to store the exported files (folders)
        """
        assert os.path.exists(dst) and os.path.isdir(dst), "Destination should be an existing directory"
        for uid in uids:
            dp: DataPoint = self[uid]
            src_pth = dp.data_path
            dst_pth = os.path.join(dst, os.path.basename(src_pth))
            if os.path.exists(src_pth):
                shutil.copytree(src_pth, dst_pth)
