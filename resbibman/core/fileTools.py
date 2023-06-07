"""
The tools that deals with files in the database
"""
from pathlib import Path
import os, shutil, json, platform, typing, uuid, time, sys, sqlite3
from typing import List, Union, TypedDict, Optional, TypeVar
import threading
import dataclasses
from functools import wraps

from . import globalVar as G
from .bibReader import BibParser
from .utils import TimeUtils
from .utils import openFile as _openFile
from ..confReader import getConf, getDatabase
from ..version import VERSION
from .htmlTools import packHtml, openTmp_hpack

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

@dataclasses.dataclass
class DocInfo:
    """
    This is a intermediate class for storing document information.
    The user is supposed to use FileManipulator to access those informations.
    """
    uuid: str
    time_import: float
    time_modify: float
    version_import: str
    version_modify: str
    device_import: str
    device_modify: str
    tags: list[str]
    url: str

    DocInfoDictT = typing.TypedDict("DocInfoDictT", {
        "uuid": str,
        "time_import": float,
        "time_modify": float,
        "version_import": str,
        "version_modify": str,
        "device_import": str,
        "device_modify": str,
        "tags": list[str],
        "url": str,
    })

    @classmethod
    def fromString(cls, s: str):
        s_dict = json.loads(s)
        return cls(**s_dict)

    def toString(self) -> str:
        return json.dumps(self.toDict())
    
    def toDict(self) -> DocInfoDictT:
        return dataclasses.asdict(self)     # type: ignore

class DBFileInfo(TypedDict):
    uuid: str           # File uuid, should be unique for each file
    bibtex: str         # Bibtex string, should be valid and remove abstract, at least contains title, year, authors
    abstract: str       # Abstract, markdown
    comments: str       # Note markdown
    info_str: str       # Info string, json serializable string of DocInfo
    doc_ext: str        # Document file type, e.g. '.pdf', '.docx'

# a wrapper that marks an object instance needs lock,
def lock_required(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        assert hasattr(self, "lock"), "The object does not have a lock attribute"
        with self.lock:
            return func(self, *args, **kwargs)
    return wrapper
class DBConnection:
    """
    to manage database connection
    """
    logger = G.logger_rbm
    db_fname = "rbm.db"
    lock = threading.Lock()

    def __init__(self, db_dir: str) -> None:
        # create db if not exist
        db_path = os.path.join(db_dir, self.db_fname)
        if not os.path.exists(db_dir):
            self.logger.info("Created new database directory: {}".format(db_dir))
            os.mkdir(db_dir)
        if not os.path.exists(db_path):
            self.logger.info("Created new database: {}".format(db_path))

        self.db_dir = db_dir
        self.db_path = db_path

        # when check_same_thread=False, the connection can be used in multiple threads
        # however, we have to ensure that only one thread is doing writing at the same time
        # refer to: https://docs.python.org/3/library/sqlite3.html#sqlite3.connect
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.__maybeCreateTable()
    
    def __maybeCreateTable(self):
        """
        Create table if not exist
        """
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            uuid TEXT PRIMARY KEY,
            bibtex TEXT NOT NULL,
            abstract TEXT NOT NULL,
            comments TEXT NOT NULL,
            info_str TEXT NOT NULL,
            doc_ext TEXT NOT NULL,
            misc_dir TEXT
        )
        """)
        self.conn.commit()
    
    
    def close(self):
        self.conn.close()
    
    @lock_required
    def __getitem__(self, uuid: str) -> Optional[DBFileInfo]:
        """
        Get file info by uuid
        """
        self.cursor.execute("SELECT * FROM files WHERE uuid=?", (uuid,))
        row = self.cursor.fetchone()
        if row is None:
            return None
        return {
            "uuid": row[0],
            "bibtex": row[1],
            "abstract": row[2],
            "comments": row[3],
            "info_str": row[4],
            "doc_ext": row[5],
        }
    
    def insertItem(self, item: DBFileInfo) -> bool:
        """
        Insert item into database, will overwrite if uuid already exists
        """
        if self[item["uuid"]] is not None:
            # if uuid already exists, delete it first
            self.cursor.execute("DELETE FROM files WHERE uuid=?", (item["uuid"],))
        with self.lock:
            self.cursor.execute("INSERT INTO files VALUES (?,?,?,?,?,?,?)", (
                item["uuid"], item["bibtex"], item["abstract"], item["comments"], item["info_str"], item["doc_ext"], None
            ))
            self.conn.commit()
        return True
    
    @lock_required
    def keys(self) -> list[str]:
        """
        Return all uuids
        """
        self.cursor.execute("SELECT uuid FROM files")
        return [row[0] for row in self.cursor.fetchall()]
    
    def _ensureExist(self, uuid: str) -> bool:
        if self[uuid] is None:
            self.logger.error("uuid {} not exists".format(uuid))
            return False
        return True
    
    def addEntry(self, bibtex: str, abstract: str = "", comments: str = "", doc_ext: str = "") -> Optional[str]:
        """
        Add an entry to the database
        return uuid if success, None if failed
        """
        # generate info
        default_info = DocInfo(
            uuid = str(uuid.uuid4()),
            time_import = TimeUtils.nowStamp(),
            time_modify = TimeUtils.nowStamp(),
            version_import = VERSION,
            version_modify = VERSION,
            device_import = platform.node(),
            device_modify = platform.node(),
            tags = [],
            url = ""
        )
        uid = default_info.uuid
        # check if uuid already exists
        if self[uid] is not None:
            self.logger.error("uuid {} already exists".format(uid))
            return None
        # insert
        with self.lock:
            self.cursor.execute("INSERT INTO files VALUES (?,?,?,?,?,?,?)", (
                uid, bibtex, abstract, comments, default_info.toString(), doc_ext, None
            ))
            self.conn.commit()
        return uid
    
    def removeEntry(self, uuid: str) -> bool:
        if not self._ensureExist(uuid): return False
        with self.lock:
            self.cursor.execute("DELETE FROM files WHERE uuid=?", (uuid,))
            self.conn.commit()
        self.logger.debug("Removed entry {}".format(uuid))
        return True
    
    def setDocExt(self, uuid: str, ext: Optional[str]) -> bool:
        if not self._ensureExist(uuid): return False
        with self.lock:
            self.cursor.execute("UPDATE files SET doc_ext=? WHERE uuid=?", (ext, uuid))
            self.conn.commit()
        return True
    
    def updateInfo(self, uuid: str, info: DocInfo) -> bool:
        if not self._ensureExist(uuid): return False
        with self.lock:
            self.cursor.execute("UPDATE files SET info_str=? WHERE uuid=?", (info.toString(), uuid))
            self.conn.commit()
        return True
    
    def updateBibtex(self, uuid: str, bibtex: str) -> bool:
        if not self._ensureExist(uuid): return False
        with self.lock:
            self.cursor.execute("UPDATE files SET bibtex=? WHERE uuid=?", (bibtex, uuid))
            self.conn.commit()
        return True
    
    def updateComments(self, uuid: str, comments: str) -> bool:
        if not self._ensureExist(uuid): return False
        with self.lock:
            self.cursor.execute("UPDATE files SET comments=? WHERE uuid=?", (comments, uuid))
            self.conn.commit()
        return True
    
    def printData(self, uuid: str):
        if not self._ensureExist(uuid): return False
        with self.lock:
            self.cursor.execute("SELECT * FROM files WHERE uuid=?", (uuid,))
            row = self.cursor.fetchone()
        print(row)


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

def _addDocumentFile(db_conn: DBConnection, uid: str, src: str):
    """
    Copy document to database directory
    """
    ext = _getFileExt(src)
    dst = os.path.join(db_conn.db_dir, uid + ext)
    shutil.copyfile(src, dst)
    db_conn.setDocExt(uid, ext)

def addDocument(db_conn: DBConnection, citation: str, abstract: str = "", comments: str = "", doc_src: Optional[str] = None) -> Optional[str]:
    """
    Should use this function to add document to database instead of directly using DBConnection.addEntry or use FileGenerator

    - citation: bibtex string, should be valid, at least contains title, year, authors
        may support other formats in the future...
    - doc_src: document source path, should be a file path, if None, doc_ext will be empty, else the document will be copied to the database directory

    return uuid if success, None if failed
    """
    import pybtex.scanner
    parser = BibParser(mode = "single")
    try:
        bib = parser(citation)[0]   # check if citation is valid
    except IndexError as e:
        G.logger_rbm.warning(f"IndexError while parsing bibtex, check if your bibtex info is empty: {e}")
        return 
    except pybtex.scanner.PrematureEOF:
        G.logger_rbm.warning(f"PrematureEOF while parsing bibtex, invalid bibtex")
        return 
    except KeyError:
        G.logger_rbm.warning(f"KeyError. (Author year and title must be provided)")
        return 

    if "abstract" in bib and abstract == "":
        abstract = bib["abstract"]

    uid = db_conn.addEntry(citation, abstract, comments)
    if uid is None:
        return None

    # copy document
    if doc_src is not None:
        _addDocumentFile(db_conn, uid, doc_src)
    return uid
    

class FileManipulator:
    logger = G.logger_rbm

    LOG_TOLERANCE_INTERVAL = 0.5

    @staticmethod
    def getDatabaseConnection(db_dir: str) -> DBConnection:
        return DBConnection(db_dir)

    def __init__(self, uid: str, db_local: Optional[DBConnection | str] = None):
        self._uid = uid

        # Common init for subclasses should be implementd in self.init
        self.init(db_local)
    
    def init(self, db_local: Optional[DBConnection | str] = None):
        if db_local is None:
            self._conn = DBConnection(getDatabase())
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
            self.logger.warning("file {} not exists, but file extension exists".format(file_path))
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

    def _createFileOB(self):
        """
        file observer thread
        """
        def _onCreated(event):
            if self._log():
                self.logger.debug(f"file_ob (fm) - {event.src_path} created.")
        def _onDeleted(event):
            if self._log():
                self.logger.debug(f"file_ob (fm) - {event.src_path} deleted.")
        def _onModified(event):
            if self._log():
                self.logger.debug(f"file_ob (fm) - {event.src_path} modified.")
        def _onMoved(event):
            if self._log():
                self.logger.debug(f"file_ob (fm) - {event.src_path} moved to {event.dest_path}.")

        # event_handler = PatternMatchingEventHandler(patterns = self.WATCHING_EXT, 
        #                                             ignore_patterns = [".DS_Store"], 
        #                                             case_sensitive=True)
        # event_handler.on_created = _onCreated
        # event_handler.on_deleted = _onDeleted
        # event_handler.on_modified = _onModified
        # event_handler.on_moved = _onMoved
        observer = Observer()
        # TO IMPLEMENT LATER!!
        print("TODO: implement file observer")
        # observer.schedule(event_handler, self.path, recursive=True)
        # self.logger.debug(f"_createFileOB (fm): Created file observer for: {self.uuid}")
        return observer

    def openFile(self) -> bool:
        # import pdb; pdb.set_trace()
        if self.file_p is None:
            return False
        if self.file_extension == ".hpack":
            openTmp_hpack(self.file_p)
        else:
            # Open file in MacOS will be treated as a file modification
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
        """log the modification time to the info file"""
        if not self._enable_log_modification_timestamp:
            return False
        time_now = time.time()
        if time_now - self._time_last_log < self.LOG_TOLERANCE_INTERVAL:
            # Prevent multiple log at same time
            return False
        db_data = self.conn[self.uuid]; assert db_data
        info = DocInfo.fromString(db_data["info_str"])
        info.time_modify = TimeUtils.nowStamp()
        info.device_modify = platform.node()
        info.version_modify = VERSION
        self.conn.updateInfo(self.uuid, info)

        self._time_last_log = time_now
        self.logger.debug("_log (fm): {}".format(self.uuid))
        return True
    
    def screen(self):
        print("TODO: remove screen")
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
        if self.hasFile():
            self.logger.warn("The file is already existing")
            return False
        doc_ext = _getFileExt(extern_file_p)
        if doc_ext not in getConf()["accepted_extensions"]:
            self.logger.warn("The file extension is not supported")
            return False
        _addDocumentFile(self.conn, self.uuid, extern_file_p)
        self.logger.debug("addFile (fm): {}".format(self.uuid))
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
        return self.conn.updateBibtex(self.uuid, bib)
    
    def readComments(self) -> str:
        db_data = self.conn[self.uuid]; assert db_data
        return db_data["comments"]
    
    def writeComments(self, comments: str):
        self.conn.updateComments(self.uuid, comments)
        self._log()
    
    def getTags(self) -> list[str]:
        db_data = self.conn[self.uuid]; assert db_data
        info = DocInfo.fromString(db_data["info_str"])
        return info.tags
    
    def writeTags(self, tags: list[str]):
        if not isinstance(tags, list):
            tags = list(tags)
        db_data = self.conn[self.uuid]; assert db_data
        info = DocInfo.fromString(db_data["info_str"])
        info.tags = tags
        self._log()
        return self.conn.updateInfo(self.uuid, info)
    
    def getWebUrl(self) -> str:
        db_data = self.conn[self.uuid]; assert db_data
        info = DocInfo.fromString(db_data["info_str"])
        return info.url
    
    def setWebUrl(self, url: str):
        db_data = self.conn[self.uuid]; assert db_data
        info = DocInfo.fromString(db_data["info_str"])
        info.url = url
        self._log()
        return self.conn.updateInfo(self.uuid, info)
    
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
        if not self.hasMisc():
            return False
        _openFile(self._misc_dir)
    
    def openBib(self):
        raise NotImplementedError("TODO: open bib")

    def deleteEntry(self) -> bool:
        """
        Will delete the entry from the database, and delete the file and misc folder if exist.
        """
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
        self.logger.debug("deleteDocument (fm): {}".format(self.uuid))
        self._log()
        return True

    def setWatch(self, status: bool = False):
        """
        Watch the file for changes, and update timestamp if changed.
        """
        self.logger.warn("TODO: implement setWatch")
