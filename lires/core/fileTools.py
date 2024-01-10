"""
The tools that deals with files in the database
"""
from __future__ import annotations
import os, shutil, platform, time, sys
from typing import List, TypedDict, Optional, TYPE_CHECKING, Any
import threading

from .base import G, LiresBase
from .dbConn import DBConnection, DocInfo
from .bibReader import BibParser
from ..utils import TimeUtils
from ..utils import openFile as _openFile
from ..confReader import DATABASE_DIR, ACCEPTED_EXTENSIONS
from ..version import VERSION

# from watchdog.observers import Observer
# from watchdog.events import PatternMatchingEventHandler

if TYPE_CHECKING:
    from .dataClass import DataTags

def _getFileExt(fpath: str):
    """
    Get document extension from file path
    """
    assert not os.path.isdir(fpath)
    ext = os.path.splitext(fpath)[1]
    if ext == "":
        raise ValueError("fpath must have extension")
    if not ext.startswith("."):
        ext = "." + ext
    return ext

def _addDocumentFileBlob(db_conn: DBConnection, uid: str, file_blob: bytes, ext: str):
    """
    Create document in database directory
    """
    assert ext.startswith(".")
    dst = os.path.join(db_conn.db_dir, uid + ext)
    with open(dst, "wb") as f:
        f.write(file_blob)
    db_conn.setDocExt(uid, ext)

def _addDocumentFile(db_conn: DBConnection, uid: str, src: str):
    """
    Copy document to database directory
    """
    ext = _getFileExt(src)
    with open(src, "rb") as f:
        _addDocumentFileBlob(db_conn, uid, f.read(), ext)

def addDocument(
        db_conn: DBConnection, 
        citation: str, abstract: str = "", 
        comments: str = "", 
        doc_src: Optional[str] = None,
        doc_info: Optional[DocInfo | dict[str, Any]] = None,
        check_duplicate: bool = True
        ) -> Optional[str]:
    """
    Should use this function to add document to database instead of directly using DBConnection.addEntry or use FileGenerator

    - citation: bibtex string, should be valid, at least contains title, year, authors
        may support other formats in the future...
    - doc_src: document source path, should be a file path, if None, doc_ext will be empty, else the document will be copied to the database directory
    - doc_info: DocInfo object, should be None for new data generated, can be provided for data imported from other sources (e.g. old version)
        or, a dict that contains partial information of DocInfo
    - check_duplicate: if True, will check if there is duplicate entry in the database, if there is, will not add the document
    return uuid if success, None if failed
    """
    import pybtex.scanner
    parser = BibParser(mode = "single")
    try:
        bib = parser(citation)[0]   # check if citation is valid
    except IndexError as e:
        G.loggers.core.warning(f"IndexError while parsing bibtex, check if your bibtex info is empty: {e}")
        return 
    except pybtex.scanner.PrematureEOF:
        G.loggers.core.warning(f"PrematureEOF while parsing bibtex, invalid bibtex")
        return 
    except KeyError:
        G.loggers.core.warning(f"KeyError. (Author year and title must be provided)")
        return 

    if "abstract" in bib and abstract == "":
        abstract = bib["abstract"][0]
    
    # maybe remove abstract from citation, so that the bibtex won't be too long
    # the abstract will be stored in the database separately
    citation = BibParser.removeAbstract(citation)

    if check_duplicate:
        # check if duplicate
        def getSearchStr(bib: dict[str, Any]) -> str:
            return f"title:{bib['title'].lower()} AND year:{bib['year']}"
        bib = parser(citation)[0]
        search_str = getSearchStr(bib)
        # traverse all entries in the database and check if there is duplicate
        for _uid in db_conn.keys():
            d_file_info = db_conn[_uid]
            aim_bib = parser(d_file_info["bibtex"])[0] # type: ignore
            aim_search_str = getSearchStr(aim_bib)
            if search_str == aim_search_str:
                G.loggers.core.warning(f"Duplicate entry found: {_uid}")
                return None

    uid = db_conn.addEntry(citation, abstract, comments, doc_info = doc_info)
    if uid is None:
        return None

    # copy document
    if doc_src is not None:
        _addDocumentFile(db_conn, uid, doc_src)
    return uid
    

class FileManipulator(LiresBase):
    logger = LiresBase.loggers().core

    # LOG_TOLERANCE_INTERVAL = 0.5

    @staticmethod
    def getDatabaseConnection(db_dir: str) -> DBConnection:
        return DBConnection(db_dir)

    def __init__(self, uid: str, db_local: Optional[DBConnection | str] = None):
        self._uid = uid

        # Common init for subclasses should be implementd in self.init
        self.init(db_local)
    
    def init(self, db_local: Optional[DBConnection | str] = None):
        if db_local is None:
            self._conn = DBConnection(DATABASE_DIR)
        elif isinstance(db_local, str):
            self._conn = DBConnection(db_local)
        else:
            self._conn = db_local

        self._time_last_log = 0
        # a switch to trigger the logging of file modification time
        self._enable_log_modification_timestamp = True

    @property
    def conn(self) -> DBConnection:
        return self._conn
    
    @property
    def uuid(self) -> str:
        return self._uid
    
    @property
    def file_extension(self) -> str:
        """Document file extension, empty string if not exists"""
        d_info = self.conn[self.uuid]
        assert d_info is not None, "uuid {} not exists".format(self.uuid)
        return d_info["doc_ext"]
    
    @file_extension.setter
    def file_extension(self, new_ext):
        file_pth = self.file_p
        file_existance = os.path.exists(file_pth) if file_pth is not None else False
        if new_ext == "":
            assert not file_existance, "should not set file extension to empty string when file exists"
        else:
            assert file_existance, "should not set file extension to none existent file"
        self.conn.setDocExt(self.uuid, new_ext)
    
    @property
    def file_p(self) -> Optional[str]:
        """Document file path, None if not exists"""
        if self.file_extension == "":
            return None
        file_path = os.path.join(self.conn.db_dir, self.uuid + self.file_extension)
        if not os.path.exists(file_path):
            self.logger.error("file {} not exists, but file extension exists".format(file_path))
            self.file_extension = ""
            self.logger.warning("cleared the file extension to auto-fix the problem")
            return None
        return file_path

    def hasFile(self):
        return self.file_p is not None

    ValidFileT = TypedDict("ValidFileT", {"root": str, "fname": List[str]})
    def gatherFiles(self) -> ValidFileT:
        """
        gather all files associated with this datapoint,
        may include: document and misc files
        could be used to compress files for upload and download
        """
        # get selected files
        selected_files = []
        if self.hasFile():
            selected_files.append(self.file_p)
        if self.hasMisc():
            selected_files.append(self.getMiscDir())
        for f in selected_files:
            assert (os.path.exists(f) and self.conn.db_dir in f), "File {} not in db_dir {}".format(f, self.conn.db_dir)
        selected_fname = [os.path.basename(f) for f in selected_files]
        return {
            "root": self.conn.db_dir,
            "fname": selected_fname,
        }
    

    @property
    def is_watched(self) -> bool:
        return hasattr(self, "file_ob")

    def openFile(self) -> bool:
        # import pdb; pdb.set_trace()
        if self.file_p is None:
            return False
        else:
            # Open file in MacOS will somehow be treated as a file modification
            # so temporarily ban file observer log modification time
            if sys.platform == "darwin":
                self._enable_log_modification_timestamp = False

            _openFile(self.file_p)

            # maybe re-enable file observer log modification time
            def _restartLoggingModification():
                # relax some time to open the file
                time.sleep(2)
                self._enable_log_modification_timestamp = True
            if sys.platform == "darwin":
                threading.Thread(target=_restartLoggingModification, args=(), daemon=True).start()
        return True
    
    def _log(self) -> bool:
        """
        log the modification time to the info file,
        the log should be triggered last in case of other updateInfo overwrite the modification time
        """
        self.logger.debug("(fm) _log: {}".format(self.uuid))
        if not self._enable_log_modification_timestamp:
            return False
        time_now = time.time()
        # if time_now - self._time_last_log < self.LOG_TOLERANCE_INTERVAL:
        #     # Prevent multiple log at same time
        #     return False
        db_data = self.conn[self.uuid]; assert db_data
        info = DocInfo.fromString(db_data["info_str"])
        info.time_modify = TimeUtils.nowStamp()
        info.device_modify = platform.node()
        info.version_modify = VERSION
        assert self.conn.updateInfo(self.uuid, info), "Failed to update info when logging modification time"

        self._time_last_log = time_now
        return True
    
    # miscelaneous files directory
    @property
    def _misc_dir(self):
        return os.path.join(self.conn.db_dir, self.uuid)
    def getMiscDir(self, create = False):
        if create and not os.path.exists(self._misc_dir):
            os.mkdir(self._misc_dir)
        return self._misc_dir
    def hasMisc(self) -> bool:
        if not os.path.exists(self._misc_dir):
            return False
        elif os.path.isdir(self._misc_dir) and os.listdir(self._misc_dir)==[]:
            return False
        else:
            return True
    
    def addFile(self, extern_file_p) -> bool:
        """
        add file to the database, will copy the file to the database directory
        """
        doc_ext = _getFileExt(extern_file_p)
        if self.hasFile():
            self.logger.warn("The file is already existing")
            return False
        if doc_ext not in ACCEPTED_EXTENSIONS:
            self.logger.warn("The file extension is not supported")
            return False
        with open(extern_file_p, "rb") as f:
            file_blob = f.read()
        return self.__addRawFileBlob(file_blob, doc_ext)
    
    def addFileBlob(self, file_blob: bytes, ext: str) -> bool:
        """
        add binary file to the database, will create the file in the database directory
        """
        if self.hasFile():
            self.logger.warn("The file is already existing")
            return False
        if ext not in ACCEPTED_EXTENSIONS:
            self.logger.warn("The file extension is not supported")
            return False
        return self.__addRawFileBlob(file_blob, ext)
    
    def __addRawFileBlob(self, file_blob: bytes, ext: str) -> bool:
        """
        add binary file to the database, without condition check
        """
        _addDocumentFileBlob(self.conn, self.uuid, file_blob, ext)
        self.logger.debug("(fm) __addRawFileBlob: {}".format(self.uuid))
        self._log()
        return True

    def getDocSize(self) -> float:
        if not self.hasFile():
            return 0.0
            # return None
        assert self.file_p      # make sure file_p is not None, type check
        size = os.path.getsize(self.file_p)
        size = size/(1048576)   # byte to M
        return round(size, 2)

    def readBib(self) -> str:
        db_data = self.conn[self.uuid]; assert db_data
        return db_data["bibtex"]

    def writeBib(self, bib: str):
        self.logger.debug("(fm) writeBib: {}".format(self.uuid))
        self._log()
        return self.conn.updateBibtex(self.uuid, bib)
    
    def readAbstract(self) -> str:
        db_data = self.conn[self.uuid]; assert db_data
        return db_data["abstract"]
    
    def writeAbstract(self, abstract: str):
        self.logger.debug("(fm) writeAbstract: {}".format(self.uuid))
        self._log()
        return self.conn.updateAbstract(self.uuid, abstract)
    
    def readComments(self) -> str:
        db_data = self.conn[self.uuid]; assert db_data
        return db_data["comments"]
    
    def writeComments(self, comments: str):
        self.logger.debug("(fm) writeComments: {}".format(self.uuid))
        self.conn.updateComments(self.uuid, comments)
        self._log()
    
    def getTags(self) -> list[str]:
        db_data = self.conn[self.uuid]; assert db_data
        info = DocInfo.fromString(db_data["info_str"])
        return info.tags
    
    def writeTags(self, tags: list[str] | DataTags):
        self.logger.debug("(fm) writeTags: {}".format(self.uuid))
        if not isinstance(tags, list):
            tags = tags.toOrderedList()
        db_data = self.conn[self.uuid]; assert db_data
        info = DocInfo.fromString(db_data["info_str"])
        info.tags = tags
        assert self.conn.updateInfo(self.uuid, info), "Failed to update info when setting tags"
        self._log()
    
    def getWebUrl(self) -> str:
        db_data = self.conn[self.uuid]; assert db_data
        info = DocInfo.fromString(db_data["info_str"])
        return info.url
    
    def setWebUrl(self, url: str):
        self.logger.debug("(fm) setWebUrl: {}".format(self.uuid))
        db_data = self.conn[self.uuid]; assert db_data
        info = DocInfo.fromString(db_data["info_str"])
        info.url = url
        assert self.conn.updateInfo(self.uuid, info), "Failed to update info when setting url"
        self._log()
    
    def getTimeAdded(self) -> float:
        db_data = self.conn[self.uuid]; assert db_data
        info = DocInfo.fromString(db_data["info_str"])
        record_added = info.time_import
        if isinstance(record_added, str):
            # old version compatable (< 0.6.0)
            return TimeUtils.strLocalTimeToDatetime(record_added).timestamp()
        else:
            return float(record_added)
    
    def getTimeModified(self) -> float:
        db_data = self.conn[self.uuid]; assert db_data
        info = DocInfo.fromString(db_data["info_str"])
        record_modified = info.time_modify
        if isinstance(record_modified, str):
            # old version compatable (< 0.6.0)
            return TimeUtils.strLocalTimeToDatetime(record_modified).timestamp()
        else:
            return float(record_modified)
    
    def getVersionModify(self) -> str:
        db_data = self.conn[self.uuid]; assert db_data
        info = DocInfo.fromString(db_data["info_str"])
        return info.version_modify
    
    def openMiscDir(self):
        if self.hasMisc():
            _openFile(self._misc_dir)
    
    def deleteEntry(self, create_backup = True) -> bool:
        """
        Will delete the entry from the database, and delete the file and misc folder if exist.
        if create_backup is True, will create a backup of the document
        """
        if create_backup:
            _conn_dir = self.conn.db_dir
            _backup_dir = os.path.join(_conn_dir, ".trash")
            if not os.path.exists(_backup_dir):
                os.mkdir(_backup_dir)
            old_entry = self.conn[self.uuid]    # must be called in advance to prevent dead lock
            assert old_entry
            with DBConnection(_backup_dir) as trash_db:
                _success = trash_db.addEntry(
                    old_entry["bibtex"], 
                    old_entry["abstract"], 
                    old_entry["comments"], 
                    doc_ext="",     # ignore the file
                    doc_info = DocInfo.fromString(old_entry["info_str"])
                    )
                if _success:    # otherwise, maybe duplicate entry
                    if self.hasFile():
                        _addDocumentFile(trash_db, self.uuid, self.file_p)  # type: ignore
                    if self.hasMisc():
                        shutil.copytree(self._misc_dir, os.path.join(_backup_dir, self.uuid))
            self.logger.debug("(fm) deleteEntry: {} (backup created)".format(self.uuid))
        
        if self.hasFile():
            self.deleteDocument()
        if os.path.exists(self._misc_dir):
            shutil.rmtree(self._misc_dir)
        return self.conn.removeEntry(self.uuid)
    
    def deleteDocument(self) -> bool:
        if not self.hasFile():
            return False
        file_p = self.file_p; assert file_p is not None
        os.remove(file_p)
        self.conn.setDocExt(self.uuid, "")
        self.logger.debug("(fm) deleteDocument: {}".format(self.uuid))
        self._log()
        return True

    def setWatch(self, status: bool = False):
        """
        Watch the file for changes, and update timestamp if changed.
        """
        self.logger.warn("TODO: implement setWatch")
