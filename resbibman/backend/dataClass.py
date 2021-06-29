import typing, re
from typing import List, Union, Iterable, Set
from .fileTools import FileManipulator
from .bibReader import BibParser

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
    def __init__(self, fm: FileManipulator):
        """
        The basic data structure that hold single data
        fmp - FileManipulator, data completeness should be confirmed ahead (use fmp.screen())
        """
        self.fm = fm
        self.data_path = fm.path
        self.loadInfo()

    def reload(self):
        self.fm = FileManipulator(self.data_path)
        self.fm.screen()
        self.loadInfo()

    def loadInfo(self):
        self.bib = BibParser()(self.fm.readBib())[0]
        self.uuid = self.fm.getUuid()
        self.tags = DataTags(self.fm.getTags())
        self.title = self.bib["title"]
        self.authors = self.bib["authors"]
        self.year = self.bib["year"]
        self.time_added = self.fm.getTimeAdded()
        self.time_modified = self.fm.getTimeModified()
    
    def changeTags(self, new_tags: DataTags):
        self.fm.writeTags(list(new_tags))
        self.tags = new_tags
    
    def screenByPattern(self, pattern):
        string = self.title+";"+";".join(self.authors)+";"+self.year
        string = string.lower()
        pattern = pattern.lower()
        result = re.search(pattern, string)
        if result is None:
            return False
        else: return True

    def save(self):
        pass

class DataList(list):
    SORT_YEAR = "Year"
    SORT_AUTHOR = "Author"
    SORT_TIMEADDED = "Time added"
    SORT_TIMEOPENED = "Time opened"
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

class DataBase(dict):
    def add(self, data: DataPoint):
        self[data.uuid] = data
    
    def getDataByTags(self, tags: Union[list, set]) -> DataList:
        datalist = DataList()
        for data in self.values():
            tag_data = set(data.tags)
            tags = set(tags)
            if tag_data.issubset(tags):
                datalist.append(data)
        return datalist

