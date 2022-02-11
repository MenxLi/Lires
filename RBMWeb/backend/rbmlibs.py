import os, copy
from typing import List, Union
from resbibman.confReader import getConfV
from resbibman.backend.dataClass import DataBase, DataList, DataPoint, DataTableList, DataTags
from resbibman.backend.fileTools import FileManipulator

def getDataBaseInfo() -> Union[List[dict], None]:
    db_path = getConfV("database")
    a = {
        "year":None,
        "title":None,
        "author":None,
        "tags":None,
        "uuid":None
    }
    return [ a ]

class DatabaseReader:
    def __init__(self, db_path: str) -> None:
        self.loadDB(db_path)
    
    def loadDB(self, db_path: str):
        print("Loading database...")
        self.db_path = db_path
        self.db = DataBase()
        for f in os.listdir(db_path):
            f = os.path.join(db_path, f)
            if os.path.isdir(f):
                fm = FileManipulator(f)
                if fm.screen():
                    data = DataPoint(fm)
                    self.db[data.uuid] = copy.deepcopy(data)
        print("Finish.")
    
    def getDictDataFromDataPoint(self, dp: DataPoint) -> dict:
        return {
            "file_status":dp.getFileStatusStr(),
            "year":dp.year,
            "title":dp.title,
            "author":dp.getAuthorsAbbr(),
            "tags":list(dp.tags),
            "uuid":dp.uuid,
            "url":dp.fm.getWebUrl()
        }
    
    def getDictDataListByTags(self, tags: Union[list, DataTags]) -> List[dict]:
        dl = self.db.getDataByTags(tags)
        return list(map(self.getDictDataFromDataPoint, dl))
    
    def getPDFPathByUUID(self, uuid: str):
        return self.db[uuid].fm.file_p