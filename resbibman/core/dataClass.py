from __future__ import annotations
import shutil
from resbibman.confReader import getConfV
import typing, re, string, os
from typing import List, Union, Iterable, Set, TYPE_CHECKING
import difflib
import markdown
from .fileTools import FileManipulator, FileGenerator
from .fileToolsV import FileManipulatorVirtual
from .bibReader import BibParser
from .utils import HTML_TEMPLATE_RAW

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
    def __init__(self, fm: FileManipulator):
        """
        The basic data structure that hold single data
        fmp - FileManipulator, data completeness should be confirmed ahead (use fmp.screen())
        """
        self.fm = fm
        self.data_path = fm.path
        self.loadInfo()

    @property
    def file_path(self) -> Union[None, str]:
        return self.fm.file_p

    def reload(self):
        self.fm = FileManipulator(self.data_path)
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
        string = self.stringInfo()
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
            return "\u2726"
        else:
            return "\u2727"

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
        print(string)
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

    def constuct(self, vs: Union[List[str], List[DataPointInfo]]):
        for v in vs:
            fm = FileManipulatorVirtual(v)
            if fm.screen():
                data = DataPoint(fm)
                self.add(data)

    def add(self, data: Union[DataPoint, str]):
        if isinstance(data, str):
            # path to the data folder
            assert os.path.exists(data)
            fm = FileManipulatorVirtual(data)
            fm.screen()
            data = DataPoint(fm)
        self[data.uuid] = data
    
    def delete(self, uuid: str):
        if uuid in self.keys():
            dp: DataPoint = self[uuid]
            if dp.fm.has_local:
                shutil.rmtree(dp.data_path)
            del self[uuid]
    
    def getDataByTags(self, tags: Union[list, set, DataTags]) -> DataList:
        datalist = DataList()
        for data in self.values():
            tag_data = set(data.tags)
            tags = set(tags)
            if tags.issubset(tag_data):
                datalist.append(data)
        return datalist
    
    def renameTag(self, tag_old: str, tag_new: str):
        data = self.getDataByTags(DataTags([tag_old]))
        for d in data:
            taglist = d.tags.toOrderedList()
            taglist = [tag_new if i == tag_old else i for i in taglist]
            d.changeTags(DataTags(taglist))
    
    def deleteTag(self, tag: str):
        data = self.getDataByTags(DataTags([tag]))
        for d in data:
            taglist = d.tags.toOrderedList()
            taglist.remove(tag)
            d.changeTags(DataTags(taglist))

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
