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
    
    def save(self):
        pass

class DataBase(dict):
    def add(self, data: DataPoint):
        self[data.uuid] = data