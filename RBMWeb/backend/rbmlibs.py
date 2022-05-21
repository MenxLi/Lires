import os, copy
from typing import List, Union
from resbibman.confReader import getConfV
from resbibman.core.dataClass import DataBase, DataList, DataPoint, DataTableList, DataTags
from resbibman.core.fileTools import FileManipulator
from resbibman.core.htmlTools import unpackHtmlTmp

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
            "has_file":dp.fm.hasFile(),
            "file_status":dp.getFileStatusStr(),
            "file_type": dp.fm.file_extension,
            "year":dp.year,
            "title":dp.title,
            "author":dp.getAuthorsAbbr(),
            "authors":"|".join(dp.authors),
            "tags":list(dp.tags),
            "uuid":dp.uuid,
            "url":dp.fm.getWebUrl(),
            "time_added": dp.fm.getTimeAdded(),
            "time_modified": dp.fm.getTimeModified(),
        }

    def getDictDataListByTags(self, tags: Union[list, DataTags], sort_by = DataList.SORT_TIMEADDED) -> List[dict]:
        dl = self.db.getDataByTags(tags)
        dl.sortBy(sort_by)
        return list(map(self.getDictDataFromDataPoint, dl))

    def getPDFPathByUUID(self, uuid: str):
        return self.db[uuid].fm.file_p

    def getTmpHtmlPathByUUID(self, uuid: str):
        dp = self.db[uuid]
        if not dp.fm.file_extension == ".hpack":
            return ""
        file_p = dp.fm.file_p
        html_p = unpackHtmlTmp(file_p, tmp_dir_name = uuid)
        return html_p

    def getCommentPathByUUID(self, uuid: str):
        return self.db[uuid].fm.comment_p

    def getURLByUUID(self, uuid: str):
        return self.db[uuid].fm.getWebURL()

    def getCommentHTMLByUUID(self, uuid: str):
        return self.db[uuid].htmlComment()
