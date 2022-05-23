import os, copy
import typing
from typing import Dict, List, Union, TypedDict
from resbibman.confReader import getConfV
from resbibman.core.dataClass import DataBase, DataList, DataPoint, DataTableList, DataTags
from resbibman.core.fileToolsV import FileManipulatorVirtual
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
    time_added: str
    time_modified: str

    # bib: dict       # refer to BibParser.__call__ | DataPoint.bib
    bibtex: str
    doc_size: float # in M.
    base_name: str  # for directory name

class DatabaseReader:
    def __init__(self, db_path: str) -> None:
        self.loadDB(db_path)

    def loadDB(self, db_path: str):
        print("Loading database: ".format(db_path))
        self.db_path = db_path
        self.db = DataBase()
        valid_f = []
        for f in os.listdir(db_path):
            f = os.path.join(db_path, f)
            if os.path.isdir(f):
                valid_f.append(f)
        self.db.constuct(valid_f, force_offline=True)
        print("Finish.")

    def getDictDataFromDataPoint(self, dp: DataPoint) -> DataPointInfo:
        return {
            "has_file":dp.fm.hasFile(),
            "file_status":dp.getFileStatusStr(),
            "file_type": dp.fm.file_extension,
            "year":dp.year,
            "title":dp.title,
            "author":dp.getAuthorsAbbr(),
            # "authors":"|".join(dp.authors),
            "authors": dp.authors,
            "tags":list(dp.tags),
            "uuid":dp.uuid,
            "url":dp.fm.getWebUrl(),
            "time_added": dp.fm.getTimeAdded(),
            "time_modified": dp.fm.getTimeModified(),

            "bibtex": dp.fm.readBib(),
            # "bib": dp.bib,
            "doc_size": dp.fm.getDocSize(),
            "base_name": dp.fm.base_name,
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
