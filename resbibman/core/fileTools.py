"""
The tools that deals with files in the database
"""
from distutils import extension
from pathlib import Path
import os, shutil, json, platform, typing, uuid
from typing import List, Union, TypedDict
import warnings
from .utils import getDateTime, openFile
from ..confReader import getConf, VERSION

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
            "\\":"-"
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
        data_dir: database directory
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

    def generateDefaultFiles(self, data_dir):
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
        print("File generated")
        return True

    def _moveFile(self):
        file_fn = self.FILEPREFIX+self.base_name+self.file_extension
        dst_file = os.path.join(self.dst_dir, file_fn)
        shutil.copy2(self.file_path, dst_file)
        os.remove(self.file_path)
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
            "time_import": getDateTime(),
            "time_modify": getDateTime(),
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
    def __init__(self, data_path):
        self.path = data_path
        self.base_name: str = os.path.split(data_path)[-1]

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
    
    def screen(self):
        """To decided if the path contains all necessary files"""
        all_files = os.listdir(self.path)
        comments_f = self.file_names["comment"]
        info_f = self.file_names["info"]
        bib_f = self.file_names["bibtex"]
        folder_f = self.file_names["misc"]
        for ext in getConf()["accepted_extensions"]:
            file_f_candidate = self.file_names["document"] + ext
            if file_f_candidate in all_files:
                file_f = file_f_candidate
                break
        if not set([comments_f, info_f, bib_f, folder_f]).issubset(set(all_files)):
            warnings.warn(str(self.path)+" doesn't have enough files in the directory and is neglected")
            return False
        
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
        if not os.path.exists(self.folder_p): warnings.warn("Miscellaneous folder does not exists")
        if not os.path.exists(self.bib_p): warnings.warn("Bibliography file does not exists")
        if not os.path.exists(self.comments_p): warnings.warn("Comments file does not exists")
        if not os.path.exists(self.info_p): warnings.warn("Info file does not exists")

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
        fn = FileGenerator.FILEPREFIX + self.base_name + file_extension
        dst_file = os.path.join(self.path, fn)
        shutil.copy2(extern_file_p, dst_file)
        os.remove(extern_file_p)
        del extern_file_p
        return True
    
    def getFileSize(self) -> Union[None, float]:
        if not self.hasFile():
            return None
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
        self._log()

    def readComments(self) -> str:
        with open(self.comments_p, "r", encoding="utf-8") as f:
            data = f.read()
        return data

    def writeComments(self, comments: str):
        with open(self.comments_p, "w", encoding="utf-8") as f:
            f.write(comments)
        self._log()
    
    def getUuid(self) -> str:
        with open(self.info_p, "r", encoding = "utf-8") as f:
            data = json.load(f)
        return data["uuid"]

    def getTags(self) -> typing.List[str]:
        with open(self.info_p, "r", encoding = "utf-8") as f:
            data = json.load(f)
        return data["tags"]
    
    def getTimeAdded(self) -> str:
        with open(self.info_p, "r", encoding = "utf-8") as f:
            data = json.load(f)
        return data["time_import"]
    
    def getTimeModified(self) -> str:
        with open(self.info_p, "r", encoding = "utf-8") as f:
            data = json.load(f)
        return data["time_modify"]
    
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
        return

    def writeTags(self, tags: list):
        if not isinstance(tags, list):
            tags = list(tags)
        with open(self.info_p, "r", encoding = "utf-8") as f:
            data = json.load(f)
        data["tags"] = tags
        with open(self.info_p, "w", encoding = "utf-8") as f:
            json.dump(data, f)
        return

    def openFile(self):
        if self.file_p is not None:
            openFile(self.file_p)
            # self._log()
            return True
        else:
            warnings.warn("The file is not existing, add the file into the database with right click menu")
            return False

    def openMiscDir(self):
        openFile(self.folder_p)
        # self._log()

    def openComments(self):
        openFile(self.comments_p)
        # self._log()

    def openBib(self):
        openFile(self.bib_p)
        # self._log()
    
    def deleteDocument(self) -> bool:
        if self.file_p is not None:
            os.remove(self.file_p)
            self.file_p = None
            return True
        else:
            return False

    def _log(self):
        """log the modification info info file"""
        with open(self.info_p, "r", encoding="utf-8") as f:
            info = json.load(f)
        info["time_modify"] = getDateTime()
        info["device_modify"] = platform.node()
        info["version_modify"] = VERSION
        with open(self.info_p, "w", encoding="utf-8") as f:
            json.dump(info, f)