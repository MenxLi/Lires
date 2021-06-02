"""
The tools that deals with file names in the database
"""
import os, shutil, json, platform, typing, uuid
from typing import List, Union
import warnings
from .utils import getDateTime, openFile
from ..confReader import conf, VERSION


FILE_EXTENSIONS = conf["accepted_extensions"]
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
        author = self.authors[0].replace(" ", "_").replace(",", "^")
        title = self.title.replace(" ", "_")
        base_name = "{}-{}-{}".format(year, author, title)
        return base_name

class FileGenerator(FileGeneratorBase):
    """
    To generate default files in the database when import the file
    """
    FOLDERNAME = "misc" # folder name for additional (Miscellaneous) files in the data folder
    COMMENTPREFIX = "comment@"
    FILEPREFIX = "file@"
    INFOPREFIX = "info@"
    BIBPREFIX = "bib@"
    def __init__(self, file_path: str, title: str, year: Union[int, str], authors: List[str]):
        """
        file_path: path to the original paper
        data_dir: database directory
        """
        super().__init__(title, year, authors)
        self.file_path = file_path

    def generateDefaultFiles(self, data_dir):
        self.data_dir = data_dir
        _file_name = os.path.split(self.file_path)[-1]
        file_name, self.file_extension = os.path.splitext(_file_name)
        if not self.file_extension in FILE_EXTENSIONS:
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
        
        self._copyFile()
        self._generateAdditionalFolder()
        self._generateBibFile() # Blank file
        self._generateCommentFile()
        self._generateInfoFile()
        print("File generated")
        return True

    def _copyFile(self):
        file_fn = self.FILEPREFIX+self.base_name+self.file_extension
        dst_file = os.path.join(self.dst_dir, file_fn)
        shutil.copy2(self.file_path, dst_file)

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
            "version_modify": VERSION
        }
        with open(fp, "w") as f:
            json.dump(default_info, f)

class FileManipulator:
    """
    Tools to manipulate single data directory
    """
    def __init__(self, data_path):
        self.path = data_path
        self.base_name = os.path.split(data_path)[-1]
    
    def screen(self):
        """To decided if the path contain only the 4 files and a dir"""
        all_files = os.listdir(self.path)
        if not len(all_files)==5:
            return False
        comments_f = FileGenerator.COMMENTPREFIX + self.base_name + ".md"
        info_f = FileGenerator.INFOPREFIX + self.base_name + ".json"
        bib_f = FileGenerator.BIBPREFIX + self.base_name + ".bib"
        folder_f = FileGenerator.FOLDERNAME
        for ext in FILE_EXTENSIONS:
            file_f = FileGenerator.FILEPREFIX + self.base_name + ext
            if file_f in all_files:
                break
        
        self.folder_p = os.path.join(self.path, folder_f)
        self.file_p = os.path.join(self.path, file_f)
        self.bib_p = os.path.join(self.path, bib_f)
        self.comments_p = os.path.join(self.path, comments_f)
        self.info_p = os.path.join(self.path, info_f)

        if not os.path.exists(self.folder_p): warnings.warn("Miscellaneous folder does not exists")
        if not os.path.exists(self.file_p): warnings.warn("The file does not exists")
        if not os.path.exists(self.bib_p): warnings.warn("Bibliography file does not exists")
        if not os.path.exists(self.comments_p): warnings.warn("Comments file does not exists")
        if not os.path.exists(self.info_p): warnings.warn("Info file does not exists")

        return True
    
    def readBib(self) -> str:
        with open(self.bib_p, "r") as f:
            data = f.read()
        return data

    def writeBib(self, bib: str):
        with open(self.bib_p, "w") as f:
            f.write(bib)
        self._log()

    def readComments(self) -> str:
        with open(self.comments_p, "r") as f:
            data = f.read()
        return data

    def writeComments(self, comments: str):
        with open(self.comments_p, "w") as f:
            f.write(comments)
        self._log()
    
    def getUuid(self) -> str:
        with open(self.info_p, "r") as f:
            data = json.load(f)
        return data["uuid"]

    def getTags(self) -> typing.List[str]:
        with open(self.info_p, "r") as f:
            data = json.load(f)
        return data["tags"]

    def writeTags(self, tags: typing.List[str]):
        pass

    def openFile(self):
        openFile(self.file_p)
        self._log()

    def openMiscDir(self):
        openFile(self.folder_p)
        self._log()

    def openComments(self):
        openFile(self.comments_p)
        self._log()

    def openBib(self):
        openFile(self.bib_p)
        self._log()

    def _log(self):
        """log the modification info into info file"""
        with open(self.info_p) as f:
            info = json.load(f)
        info["time_modify"] = getDateTime()
        info["device_modifky"] = platform.node()
        info["version_modify"] = VERSION
        with open(self.info_p, "w") as f:
            json.dump(info, f)
