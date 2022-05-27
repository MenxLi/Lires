from __future__ import annotations
import logging
import shutil, requests, json
from resbibman.confReader import getConfV
import typing, re, string, os
from typing import List, Union, Iterable, Set, TYPE_CHECKING, Dict
import difflib
import markdown
from .fileTools import FileGenerator
try:
    # may crash when generating config file withouot config file...
    # because getConf was used in constructing static variable
    from .fileToolsV import FileManipulatorVirtual
except (FileNotFoundError, KeyError):
    pass
from .bibReader import BibParser
from .utils import HTML_TEMPLATE_RAW
from .encryptClient import generateHexHash
from . import globalVar as G

if TYPE_CHECKING:
    from RBMWeb.backend.rbmlibs import DataPointInfo

class DataTags(set):
    def toOrderedList(self):
        ordered_list = list(self)
        ordered_list.sort()
        return ordered_list
    
    def union(self, *s):
        return DataTags(super().union(*s))
    
    def toStr(self):
        if len(self) > 0:
            return "; ".join(self.toOrderedList())
        else:
            return "<None>"

class DataPoint:
    COMMENT_HTML_TEMPLATE = string.Template(HTML_TEMPLATE_RAW)
    logger = G.logger_rbm
    def __init__(self, fm: FileManipulatorVirtual):
        """
        The basic data structure that hold single data
        fmp - FileManipulator, data completeness should be confirmed ahead (use fmp.screen())
        """
        self.fm = fm
        self.data_path = fm.path
        self.__parent_db: DataBase
        self.__force_offline = False
        self.loadInfo()
    
    def _forceOffline(self):
        """Called when run server"""
        self.__force_offline = True
        self.fm._forceOffline()
    
    def sync(self) -> bool:
        if self.uuid in self.par_db.remote_info:
            remote_info = self.par_db.remote_info[self.uuid]
            self.fm.v_info = remote_info
            return self.fm._sync()
        else:
            # New data that remote don't have
            self.logger.info("Creating new data remote {}".format(self.uuid))
            return self.fm._uploadRemote()

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
        if self.fm.has_local:
            self.fm = FileManipulatorVirtual(self.data_path)
        else:
            # to decide later
            pass
        if self.__force_offline:
            self.fm.forceOffline()
        self.fm.screen()
        self.loadInfo()

    def loadInfo(self):
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
        out = self.fm.changeBasename(fg.base_name)
        # update datapoint
        self.data_path = self.fm.path
        self.reload()
        return out
    
    def addFile(self, extern_file_p: str) -> bool:
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
    
    def screenByPattern(self, pattern):
        # string = self.title+";"+";".join(self.authors)+";"+self.year
        string = self.stringInfo() + "\n" + self.uuid
        string = string.lower()
        pattern = pattern.lower()
        result = re.search(pattern, string)
        if result is None:
            return False
        else: return True

    def htmlComment(self) -> str:
        comment = self.fm.readComments()
        if comment == "":
            return ""
        misc_f = self.fm.folder_p
        misc_f = misc_f.replace(os.sep, "/")
        comment = comment.replace("./misc", misc_f)

        comment_html = markdown.markdown(comment)
        comment_html = self.COMMENT_HTML_TEMPLATE.substitute(content = comment_html)
        return comment_html

    def save(self):
        pass

    def getFileStatusStr(self):
        """If the datapoint contains file"""
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
        if len(self.authors) == 1:
            author = self._getFirstName(self.authors[0]) + "."
        else:
            author = self._getFirstName(self.authors[0]) + " et al."
        return author

    def _getFirstName(self, name: str):
        x = name.split(", ")
        return x[0]
    
    def __str__(self) -> str:
        return f"{self.year}-{self.title}"
    
    __repr__ = __str__

class DataList(list):
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

    def sortBy(self, mode):
        if mode == self.SORT_AUTHOR:
            return self.sort(key = lambda x: x.authors[0])
        elif mode == self.SORT_YEAR:
            return self.sort(key = lambda x: int(x.year))
        elif mode == self.SORT_TIMEADDED:
            return self.sort(key = lambda x: x.time_added)
        elif mode == self.SORT_TIMEOPENED:
            return self.sort(key = lambda x: x.time_modified)

    def reloadFromFile(self, idx):
        self[idx].reload()
    
    def getTable(self):
        pass

    # def getTableItem(self, row: int, col: int) -> str:
        # data = self[row]
        # return DataList.TB_FUNCS[col](data)

    # def getTableHeaderItem(self, col: int) -> str:
        # return self.TB_HEADER[col]

class DataTableList(DataList):
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
        HEADER_TIMEMODIFY: lambda x: x.time_modified
    }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.header_order = getConfV("table_headers")

    def getTableItem(self, row: int, col: int) -> str:
        data = self[row]
        return DataTableList._HEADER_FUNCS[self.header_order[col]](data)

    def getTableHeaderItem(self, col: int) -> str:
        return self.header_order[col]

class DataBase(dict):
    logger = G.logger_rbm

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
        load both db_local and remote server
        reset offline status
        """
        self._force_offline = force_offline
        if not self.offline:
            flist = self.pull()
            if not flist:
                # empty may indicate an server error
                self.constuct([], force_offline=True)
            else:
                # server may be back when reload 
                self.constuct(flist, force_offline=self._force_offline)
        if db_local:
            # when load database is provided
            to_load = []
            for f in os.listdir(db_local):
                f_path = os.path.join(db_local, f)
                if os.path.isdir(f_path):
                    to_load.append(f_path)
            self.constuct(to_load)

    def constuct(self, vs: Union[List[str], List[DataPointInfo]], force_offline = False):
        """
         - force_offline: use when called by server side
                         or when server is down
        """
        for v in vs:
            fm = FileManipulatorVirtual(v)
            if fm.screen():
                data = DataPoint(fm)
                if force_offline:
                    data._forceOffline()
                self.add(data)
        if force_offline:
            self._force_offline = True

    def pull(self) -> List[DataPointInfo]:
        """
        update self.remote_info
        will not change data
        """
        if self.offline:
            self.logger.info("Offline mode, can't pull database")
            return []

        addr = "http://{}:{}".format(getConfV("host"), getConfV("port"))
        flist_addr = "{}/filelist/%".format(addr) 

        try:
            res = requests.get(flist_addr)
            if res.status_code != 200:
                self.logger.info("Faild to pull remote data ({})".format(res.status_code))
                return []
        except requests.exceptions.ConnectionError:
            self.logger.warning("Server is down, abort pulling remote data.")
            return []
        
        flist = res.text
        flist = json.loads(flist)["data"]
        self.__file_list_remote = flist
        return flist

    def add(self, data: Union[DataPoint, str]) -> DataPoint:
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
        if uuid in self.keys():
            dp: DataPoint = self[uuid]
            if dp.fm.has_local:
                dp.fm.setWatch(False)
                shutil.rmtree(dp.data_path)
            if not self.offline:
                # If remote has this data, delete remote as well, 
                # otherwise it will be downloaded again when sync
                if dp.uuid in self.remote_info:     # Check if is it in remote
                    if not dp.fm._deleteRemote():
                        self.logger.info("Oops, the data on the server side hasn't been deleted")
                        self.logger.warn("You may need to sync->delete again for {}".format(dp))
            del self[uuid]

    def watchFileChange(self, v: List[Union[DataPoint, str]]):
        for uuid, dp in self.items():
            dp.fm.setWatch(False)
        for v_ in v:
            if isinstance(v_, DataPoint):
                v_.fm.setWatch(True)
            else:
                self[v_].setWatch(True)
        return
    
    def getDataByTags(self, tags: Union[list, set, DataTags]) -> DataList:
        datalist = DataList()
        for data in self.values():
            tag_data = set(data.tags)
            tags = set(tags)
            if tags.issubset(tag_data):
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
                "args": json.dumps([tag_old, tag_new])
            }
            if not self.remoteCMD(post_args):
                self.logger.info("Abort renaming")
                return False

        # change local tag
        # (After remote change so local is always updated than remote)
        self.logger.info(f"Renaming local tag: {tag_old} -> {tag_new}")
        for d in data:
            d: DataPoint
            taglist = d.tags.toOrderedList()
            taglist = [tag_new if i == tag_old else i for i in taglist]
            d.changeTags(DataTags(taglist))
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
                "args": json.dumps([tag])
            }
            if not self.remoteCMD(post_args):
                self.logger.info("Abort deleting tag")
                return False

        # delete local tag
        # (After remote delete so local is always updated than remote)
        self.logger.info(f"Deleting local tag: {tag}")
        for d in data:
            taglist = d.tags.toOrderedList()
            taglist.remove(tag)
            d.changeTags(DataTags(taglist))
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

    def allUptodate(self) -> bool:
        """
        Return if all data points in local are up-to-date with remote
        """
        if self.offline:
            return True
        # udpate remote file info
        self.pull()
        for d in self.values():
            if d.is_local:
                # update data point v_info to the same with remote
                d.v_info = self.remote_info[d.uuid]
                if d.fm.is_uptodate == "behind":
                    self.logger.info(f"data({d.uuid}) is behind remote")
                    return False
        return True
