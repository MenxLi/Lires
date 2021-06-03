import typing
from typing import List, Union
from .fileTools import FileManipulator
from .bibReader import BibParser

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
        self.tags = self.fm.getTags()
        self.title = self.bib["title"]
        self.authors = self.bib["authors"]
        self.year = self.bib["year"]
    
    def changeTags(self, newTages: Union[list, set]):
        pass
    
    def save(self):
        pass

class DataList(list):
    SORT_YEAR = "Year"
    SORT_AUTHOR = "Author"
    SORT_TIMEADDED = "Time added"
    def sortBy(self, mode):
        pass

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

class DataTags(set):
    pass
