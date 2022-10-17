"""
The tools that deals with files in the database
"""
from pathlib import Path
import os, shutil, json, platform, typing, uuid, time, sys
from typing import List, Union, TypedDict
import warnings
import threading

from . import globalVar as G
from .utils import openFile, TimeUtils
from ..confReader import getConf, getConfV
from ..version import VERSION
from .htmlTools import packHtml, openTmp_hpack

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

class FileNameType(TypedDict):
    bibtex: str
    document: str
    comment: str
    info: str
    misc: str

class FileGeneratorBase:
    def __init__(self, title: str, year: Union[int, str], authors: List[str]):
        """
        - title: The title of the paper
        - year: the publish year
        - authors: list of authors
        """
        self.title = title
        self.year = year
        self.authors = authors
        self.base_name = self.generateBaseName()[:70]
        return None

    def generateBaseName(self):
        year = str(self.year)
        author = self.strSubstitute(self.authors[0])
        title = self.strSubstitute(self.title)
        base_name = "{}-{}-{}".format(year, author, title)
        return base_name
    
    def strSubstitute(self, string: str):
        substitute_table = {
            " ": "_",
            ",":"^",
            ":":"",
            "/":"-",
            "\\":"-",
            "?":"",
        }
        for k, v in substitute_table.items():
            string = string.replace(k, v)
        return string

class FileGenerator(FileGeneratorBase):
    """
    To generate default files in the database when import the file
    """
    FOLDERNAME = "misc" # folder name for additional (Miscellaneous) files in the data folder
    COMMENTPREFIX = "comment@"
    FILEPREFIX = "file@"
    INFOPREFIX = "info@"
    BIBPREFIX = "bib@"

    def __init__(self, file_path: Union[str, None], title: str, year: Union[int, str], authors: List[str]):
        """
        file_path: path to the original paper, set to None for no file serving
        """
        super().__init__(title, year, authors)
        self.file_path = file_path

    @property
    def file_names(self) -> FileNameType:
        """
        To get file names without actually generate files
        """
        return {
            "bibtex": self.BIBPREFIX+self.base_name+".bib",
            "document": self.FILEPREFIX + self.base_name,           # name without extension
            "comment": self.COMMENTPREFIX+self.base_name+".md",
            "info": self.INFOPREFIX+self.base_name+".json",
            "misc": self.FOLDERNAME
        }
    
    @property
    def dst_path(self) -> str:
        """
        Return generated directory path
        """
        if hasattr(self, "dst_dir"):
            return self.dst_dir
        else:
            warnings.warn("Call generateDefaultFiles for FileGenerator to generate files")
            return ""

    def generateDefaultFiles(self, data_dir):
        """
         - data_dir: database directory
        """
        self.data_dir = data_dir
        if self.file_path is not None:
            _file_name = os.path.split(self.file_path)[-1]
            file_name, self.file_extension = os.path.splitext(_file_name)
            if not self.file_extension in getConf()["accepted_extensions"]:
                warnings.warn("Incorrect file type, check extensions.")
                return False

        self.dst_dir = os.path.join(self.data_dir, self.base_name)
        while(True):
            if not os.path.exists(self.dst_dir):
                os.mkdir(self.dst_dir)
                break
            else:
                warnings.warn("File existed before?")
                self.base_name = self.base_name + "a"
                self.dst_dir = os.path.join(self.data_dir, self.base_name)
        
        if self.file_path is not None:
            self._moveFile()
        self._generateAdditionalFolder()
        self._generateBibFile() # Blank file
        self._generateCommentFile()
        self._generateInfoFile()
        G.logger_rbm.info("File generated at: {}".format(self.dst_dir))
        return True

    @classmethod
    def moveDocument(cls, src_file: str, dst_file_base: str):
        """
        Move file to the database based on different data type
        - dst_file_base: file path without extension
        """
        _file_name = os.path.split(src_file)[-1]
        file_name, file_extension = os.path.splitext(_file_name)
        if file_extension == ".html":
            # pack html to single .hpack file
            dst_file = dst_file_base + ".hpack"
            packHtml(src_file, dst = dst_file)
        else:
            # single file, just change name
            shutil.copy2(src_file, dst_file_base + file_extension)
            #  os.remove(src_file)

    def _moveFile(self):
        if self.file_path is None:
            raise ValueError("file_path is None in file generator")

        file_fn = self.FILEPREFIX+self.base_name        # file base name
        dst_file_base = os.path.join(self.dst_dir, file_fn)
        self.moveDocument(self.file_path, dst_file_base)
        del self.file_path

    def _generateAdditionalFolder(self):
        os.mkdir(os.path.join(self.dst_dir, self.FOLDERNAME))

    def _generateCommentFile(self):
        comment_fn = self.COMMENTPREFIX+self.base_name+".md"
        fp = os.path.join(self.dst_dir, comment_fn)
        with open(fp, "w") as _:
            pass

    def _generateBibFile(self):
        bib_fn = self.BIBPREFIX+self.base_name+".bib"
        fp = os.path.join(self.dst_dir, bib_fn)
        with open(fp, "w") as _:
            pass

    def _generateInfoFile(self):
        info_fn = self.INFOPREFIX+self.base_name+".json"
        fp = os.path.join(self.dst_dir, info_fn)
        default_info = {
            "device_import": platform.node(),
            "device_modify": platform.node(),
            "time_import": TimeUtils.nowStamp(),
            "time_modify": TimeUtils.nowStamp(),
            "tags": [],
            "uuid": str(uuid.uuid4()),
            "version_import": VERSION,
            "version_modify": VERSION,
            "url": ""
        }
        with open(fp, "w") as f:
            json.dump(default_info, f)

class FileManipulator:
    """
    Tools to manipulate single data directory
    """
    logger = G.logger_rbm
    LOG_TOLERANCE_INTERVAL = 0.5
    try:
        _WATCHING_EXT = getConfV("accepted_extensions") + [".json", ".md", ".bib"]
        WATCHING_EXT = list(set(["*{}".format(i) for i in _WATCHING_EXT]))
    except FileNotFoundError:
        # when generating configuration file
        pass
    def __init__(self, data_path):
        self.path = data_path
        self.base_name: str = os.path.split(data_path)[-1]
        self._file_extension: str = ""     # extension of the main document, "" for undefined / No file

        # a switch to trigger the logging of file modification time
        self._enable_log_modification_timestamp = True

        self.init()

    def init(self):
        # Common init for subclasses
        self._time_last_log = 0
        self.folder_p: str
        self.bib_p: str
        self.comments_p: str
        self.info_p: str
        self.file_p: Union[str, None]

    @property
    def file_names(self) -> FileNameType:
        """
        To get file names without actually generate files
        """
        return {
            "bibtex": FileGenerator.BIBPREFIX+self.base_name+".bib",
            "document": FileGenerator.FILEPREFIX + self.base_name,           # name without extension
            "comment": FileGenerator.COMMENTPREFIX+self.base_name+".md",
            "info": FileGenerator.INFOPREFIX+self.base_name+".json",
            "misc": FileGenerator.FOLDERNAME
        }

    @property
    def file_extension(self) -> str:
        return self._file_extension
    
    @property
    def uuid(self) -> str:
        return self.getUuid()

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

        # Exclude info path and main directory to prevent circular call
        #  event_handler = PatternMatchingEventHandler(patterns = ["{}{}*".format(self.path, os.sep)], \
        #                                              ignore_patterns = [
        #                                                  "*{}".format(self.file_names["info"]),
        #                                              ], case_sensitive=True)
        event_handler = PatternMatchingEventHandler(patterns = self.WATCHING_EXT, 
                                                    ignore_patterns = ["*{}".format(self.file_names["info"]), ".DS_Store"], 
                                                    case_sensitive=True)
        event_handler.on_created = _onCreated
        event_handler.on_deleted = _onDeleted
        event_handler.on_modified = _onModified
        event_handler.on_moved = _onMoved
        observer = Observer()
        observer.schedule(event_handler, self.path, recursive=True)
        self.logger.debug(f"_createFileOB (fm): Created file observer for: {self.uuid}")
        return observer
    
    def screen(self) -> bool:
        """
        To decided if the path contains all necessary files
        Initialize the following attributes:
            self.folder_p
            self.bib_p
            self.comments_p
            self.info_p
        Maybe initialize:
            self.file_p
        """
        all_files = os.listdir(self.path)
        comments_f = self.file_names["comment"]
        info_f = self.file_names["info"]
        bib_f = self.file_names["bibtex"]
        folder_f = self.file_names["misc"]
        for ext in getConf()["accepted_extensions"]:
            # search if legitimate document exists in the self.path
            file_f_candidate = self.file_names["document"] + ext
            if file_f_candidate in all_files:
                file_f = file_f_candidate
                self._file_extension = ext
                break
        self.folder_p = os.path.join(self.path, folder_f)
        self.bib_p = os.path.join(self.path, bib_f)
        self.comments_p = os.path.join(self.path, comments_f)
        self.info_p = os.path.join(self.path, info_f)
        try:
            self.file_p = os.path.join(self.path, file_f)
            if not os.path.exists(self.file_p): warnings.warn("The file does not exists")
        except NameError:
            # No file served
            self.file_p = None
        if os.path.exists(self.bib_p) and os.path.exists(self.info_p) and \
            not os.path.exists(self.folder_p):
            self.logger.debug("Miscellaneous folder for does not exists, and is now created: {}"\
                .format(self.folder_p))
            os.mkdir(self.folder_p)
        if not os.path.exists(self.bib_p): self.logger.debug("Bibliography file ({}) does not exists".format(self.base_name))
        if not os.path.exists(self.comments_p): self.logger.debug("Comments file ({}) does not exists".format(self.base_name))
        if not os.path.exists(self.info_p): self.logger.debug("Info file ({}) does not exists".format(self.base_name))

        if not set([comments_f, info_f, bib_f]).issubset(set(all_files)):
            self.logger.error(str(self.path)+" doesn't have enough files in the directory and is neglected")
            return False

        return True

    def changeBasename(self, new_basename: str) -> bool:
        """
        Change file base name, should be called when changing bibtex
        i.e. together with wirteBib, **It is unsafe to call this method alone**.
        """
        if self.base_name == new_basename:
            return False
        self.base_name = new_basename
        # change file names
        shutil.move(self.folder_p, os.path.join(self.path, self.file_names["misc"]))
        shutil.move(self.bib_p, os.path.join(self.path, self.file_names["bibtex"]))
        shutil.move(self.comments_p, os.path.join(self.path, self.file_names["comment"]))
        shutil.move(self.info_p, os.path.join(self.path, self.file_names["info"]))
        if self.file_p is not None:
            ext = self.file_p.split(".")[-1]
            shutil.move(self.file_p, os.path.join(self.path, self.file_names["document"] + "." + ext))
        # change dir name
        root_path = str(Path(self.path).parent)
        new_path = os.path.join(root_path, new_basename)
        shutil.move(self.path, os.path.join(root_path, new_basename))
        self.path = new_path
        # reload
        return self.screen()
    
    def hasFile(self):
        return not self.file_p is None
    
    def addFile(self, extern_file_p):
        if self.hasFile():
            return False
        _file_name = os.path.split(extern_file_p)[-1]
        file_name, file_extension = os.path.splitext(_file_name)
        if not file_extension in getConf()["accepted_extensions"]:
            warnings.warn("Incorrect file type, check extensions.")
            return False
        self._file_extension = file_extension
        fn_base = FileGenerator.FILEPREFIX + self.base_name
        dst_base = os.path.join(self.path, fn_base)
        FileGenerator.moveDocument(extern_file_p, dst_base)
        del extern_file_p
        return True
    
    def getDocSize(self) -> float:
        if not self.hasFile():
            return 0.0
            # return None
        size = os.path.getsize(self.file_p)
        size = size/(1048576)   # byte to M
        return round(size, 2)
    
    def readBib(self) -> str:
        with open(self.bib_p, "r", encoding="utf-8") as f:
            data = f.read()
        return data

    def writeBib(self, bib: str):
        """
        Change bibtex file,
        should call changeBasename if base_name has to be changed.
        """
        with open(self.bib_p, "w", encoding="utf-8") as f:
            f.write(bib)

    def readComments(self) -> str:
        with open(self.comments_p, "r", encoding="utf-8") as f:
            data = f.read()
        return data

    def writeComments(self, comments: str):
        with open(self.comments_p, "w", encoding="utf-8") as f:
            f.write(comments)
    
    def getUuid(self) -> str:
        # uuid is not going to change, so just read once
        if not hasattr(self, "_uuid"):
            with open(self.info_p, "r", encoding = "utf-8") as f:
                self._uuid = json.load(f)["uuid"]
        return self._uuid

    def getTags(self) -> typing.List[str]:
        with open(self.info_p, "r", encoding = "utf-8") as f:
            data = json.load(f)
        return data["tags"]
    
    def getTimeAdded(self) -> float:
        with open(self.info_p, "r", encoding = "utf-8") as f:
            data = json.load(f)
        record_added = data["time_import"]
        if isinstance(record_added, str):
            # old version compatable (< 0.6.0)
            return TimeUtils.strLocalTimeToDatetime(record_added).timestamp()
        else:
            return float(record_added)
    
    def getTimeModified(self) -> float:
        with open(self.info_p, "r", encoding = "utf-8") as f:
            data = json.load(f)
        record_modified = data["time_modify"]
        if isinstance(record_modified, str):
            # old version compatable (< 0.6.0)
            return TimeUtils.strLocalTimeToDatetime(record_modified).timestamp()
        else:
            return float(record_modified)
        # get document modification time
        #  __modified_time = os.path.getmtime(self.file_p)
        #  __modified_time = time.localtime(__modified_time)
        #  modified_time = time.strftime("%Y-%m-%d %H:%M:%S", __modified_time)
        #
        #  _modified_time = datetime.datetime.strptime(modified_time, "%Y-%m-%d %H:%M:%S")
        #  _record_modified = strtimeToDatetime(record_modified)
        #  if _record_modified > _modified_time:
        #      return record_modified
        #  else:
        #      self.logger.debug("Using modified_time - {} ()".format(modified_time, self.uuid))
        #      return modified_time
    
    def getWebUrl(self) -> str:
        with open(self.info_p, "r", encoding = "utf-8") as f:
            data = json.load(f)
        if not "url" in data:
            # Older version compatable
            data["url"] = ""
        return data["url"]
    
    def setWebUrl(self, url: str):
        with open(self.info_p, "r", encoding = "utf-8") as f:
            data = json.load(f)
        data["url"] = url
        with open(self.info_p, "w", encoding = "utf-8") as f:
            json.dump(data, f)
        self._log()     # keep this as it info_p will not be monitored by watchdog
        return

    def writeTags(self, tags: list):
        if not isinstance(tags, list):
            tags = list(tags)
        with open(self.info_p, "r", encoding = "utf-8") as f:
            data = json.load(f)
        data["tags"] = tags
        with open(self.info_p, "w", encoding = "utf-8") as f:
            json.dump(data, f)
        self._log()     # keep this as it info_p will not be monitored by watchdog
        return

    def openFile(self):
        if self.file_p is None:
            warnings.warn("The file is not existing, add the file into the database with right click menu")
            return False
        if self.file_extension == ".hpack":
            openTmp_hpack(self.file_p)
        else:
            # Open file in MacOS will be treated as a file modification
            # so temporarily ban file observer log modification time
            if sys.platform == "darwin":
                self._enable_log_modification_timestamp = False

            openFile(self.file_p)

            # maybe re-enable file observer log modification time
            def _restartLoggingModification():
                # relax some time to open the file
                time.sleep(3)
                self._enable_log_modification_timestamp = True
            if sys.platform == "darwin":
                threading.Thread(target=_restartLoggingModification, args=(), daemon=True).start()
        return True

    def openMiscDir(self):
        openFile(self.folder_p)

    def openComments(self):
        openFile(self.comments_p)

    def openBib(self):
        openFile(self.bib_p)
    
    def deleteDocument(self) -> bool:
        self.setWatch(True)     # initial observer
        if self.file_p is not None:
            os.remove(self.file_p)
            self.file_p = None
            return True
        else:
            return False

    def setWatch(self, status: bool = False):
        if hasattr(self, "file_ob"):
            self.file_ob.stop()
            self.file_ob.join()
            del self.file_ob
            if not status:
                self.logger.debug(f"setWatch (fm): Stopped file observer for {self.uuid}")
        if status:
            self.file_ob = self._createFileOB()
            self.file_ob.start()
            self.logger.debug(f"setWatch (fm): Started file observer for {self.uuid}")

    def _log(self) -> bool:
        """log the modification time to the info file"""
        if not self._enable_log_modification_timestamp:
            return False
        time_now = time.time()
        if time_now - self._time_last_log < self.LOG_TOLERANCE_INTERVAL:
            # Prevent multiple log at same time
            return False
        with open(self.info_p, "r", encoding="utf-8") as f:
            info = json.load(f)
        info["time_modify"] = TimeUtils.nowStamp()
        info["device_modify"] = platform.node()
        info["version_modify"] = VERSION
        with open(self.info_p, "w", encoding="utf-8") as f:
            json.dump(info, f)

        self._time_last_log = time_now
        self.logger.debug("_log (fm): {}".format(self.uuid))
        return True
