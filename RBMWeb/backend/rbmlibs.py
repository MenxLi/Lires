import typing
import os, sys, shutil
from typing import List, Union, TypedDict
from resbibman.confReader import getConfV, TMP_WEB_NOTES, ASSETS_PATH
from resbibman.core.dataClass import DataBase, DataList, DataPoint, DataTags
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
    time_added: float
    time_modified: float

    # bib: dict       # refer to BibParser.__call__ | DataPoint.bib
    bibtex: str
    doc_size: float # in M.
    base_name: str  # for directory name

class DatabaseReader:
    def __init__(self, db_path: str) -> None:
        self.loadDB(db_path)

    def loadDB(self, db_path: str):
        print("Loading database: {}".format(db_path))
        self.db_path = db_path
        self.db = DataBase()
        self.db.init(db_path, force_offline=True)
        print("Finish.")

    def getDataInfo(self, uid: str):
        return self.getDictDataFromDataPoint(self.db[uid])

    def getDictDataFromDataPoint(self, dp: DataPoint) -> DataPointInfo:
        return dp.info
        #  return {
        #      "has_file":dp.fm.hasFile(),
        #      "file_status":dp.getFileStatusStr(),
        #      "file_type": dp.fm.file_extension,
        #      "year":dp.year,
        #      "title":dp.title,
        #      "author":dp.getAuthorsAbbr(),
        #      # "authors":"|".join(dp.authors),
        #      "authors": dp.authors,
        #      "tags":list(dp.tags),
        #      "uuid":dp.uuid,
        #      "url":dp.fm.getWebUrl(),
        #      "time_added": dp.fm.getTimeAdded(),
        #      "time_modified": dp.fm.getTimeModified(),
        #
        #      "bibtex": dp.fm.readBib(),
        #      # "bib": dp.bib,
        #      "doc_size": dp.fm.getDocSize(),
        #      "base_name": dp.fm.base_name,
        #  }

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

    def getTmpNotesPathByUUID(self, uuid: str):
        dp: DataPoint = self.db[uuid]
        #  htm_str = self.getCommentHTMLByUUID(uuid)
        htm_str = dp.htmlComment(abs_fpath = False)
        tmp_notes_pth = os.path.join(TMP_WEB_NOTES, uuid)
        if os.path.exists(tmp_notes_pth):
            shutil.rmtree(tmp_notes_pth)
        os.mkdir(tmp_notes_pth)
        tmp_notes_html = os.path.join(tmp_notes_pth, "index.html")
        tmp_notes_misc = os.path.join(tmp_notes_pth, "misc")
        with open(tmp_notes_html, "w") as fp:
            fp.write(htm_str)
        os.symlink(dp.fm.folder_p, tmp_notes_misc)

        # For mathjax, not working somehow?
        math_jax_path = os.path.join(ASSETS_PATH, "mathjax")
        for f in os.listdir(math_jax_path):
            mjf_path = os.path.join(math_jax_path, f)
            os.symlink(mjf_path, os.path.join(tmp_notes_pth, f))
        return tmp_notes_html

    def getCommentPathByUUID(self, uuid: str):
        return self.db[uuid].fm.comment_p

    def getURLByUUID(self, uuid: str):
        return self.db[uuid].fm.getWebURL()

    def getCommentHTMLByUUID(self, uuid: str):
        """DEPRECATED"""
        dp: DataPoint = self.db[uuid]
        htm = dp.htmlComment(abs_fpath = False)
        return htm
