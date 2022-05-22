"""
Virtual (Remote) file tools
"""
from __future__ import annotations
import os, typing
from typing import TYPE_CHECKING, Union, overload
from .fileTools import FileGenerator, FileManipulator
from ..confReader import getConfV, TMP_DB

if TYPE_CHECKING:
    from RBMWeb.backend.rbmlibs import DataPointInfo

class FileManipulatorVirtual(FileManipulator):
    """
    Virtual file manipulator | Local file manipulator
    Provide some API at start
    To download from server and pass control to local FileManipulator
    """
    def __init__(self, v: Union[DataPointInfo, str]):
        """
         - v [DataPointInfo]: dictionary datapoint info,
                to construct vitrual file manipulator
         - v [str]: local data path, 
                to construct local file manipulator
        """
        if isinstance(v, str):
            super().__init__(v)
        else:
            assert not self.offline
            self.base_name = v["base_name"]
            self._file_extension = v["file_type"]
            self.path = os.path.join(TMP_DB, self.base_name)

            self._v_info = v    # a backup of the Datapoint Info
    
    @property
    def v_info(self) -> Union[DataPointInfo, dict]:
        """ Virtual file info """
        if hasattr(self, "_v_info"):
            return self._v_info
        else:
            return dict()

    @property
    def offline(self) -> bool:
        """ check if remote server has been set """
        return getConfV("host") == ""

    @property
    def has_local(self) -> bool:
        """
        check if has synchronized local file
        """
        if self.offline:
            return True
        else:
            return os.path.exists(self.path)

    @property
    def is_uptodate(self) -> bool:
        """
        Check if a local file is up to date with remote,
        """
        if not self.has_local:
            return False

        pass

    def sync(self) -> bool:
        """
        Download if not local
        Upload if has local file
        """
        # Check is_uptodate when uploading
        pass
    
    def _upload(self) -> bool:
        pass

    def _download(self) -> bool:
        pass

    #=========================== Below emulate local manipulator class

    def screen(self) -> bool:
        if self.has_local:
            return super().screen()
        else:
            return True

    def changeBasename(self, new_basename: str) -> bool:
        if self.has_local:
            return super().changeBasename(new_basename)    
        else:
            ...
    
    def hasFile(self):
        if self.has_local:
            return super().hasFile()
        else:
            return self.v_info["has_file"]
    
    def addFile(self, extern_file_p):
        if self.has_local:
            return super().addFile(extern_file_p)
        else:
            ...
    
    def getDocSize(self) -> float:
        if self.has_local:
            return super().getDocSize()
        else:
            return self.v_info["doc_size"]
    
    def readBib(self) -> str:
        if self.has_local:
            return super().readBib()
        else:
            return self.v_info["bibtex"]
    
    def writeBib(self, bib: str):
        if self.has_local:
            return super().writeBib(bib)
        else:
            ...
    
    def readComments(self) -> str:
        if self.has_local:
            return super().readComments()
        else:
            ...
    
    def writeComments(self, comments: str):
        if self.has_local:
            return super().writeComments(comments)
        else:
            ...
    
    def getUuid(self) -> str:
        if self.has_local:
            return super().getUuid()
        else:
            return self.v_info["uuid"]
    
    def getTags(self) -> typing.List[str]:
        if self.has_local:
            return super().getTags()
        else:
            return self.v_info["tags"]
    
    def getTimeAdded(self) -> str:
        if self.has_local:
            return super().getTimeAdded()
        else:
            return self.v_info["time_added"]
    
    def getTimeModified(self) -> str:
        if self.has_local:
            return super().getTimeModified()
        else:
            return self.v_info["time_modified"]
    
    def getWebUrl(self) -> str:
        if self.has_local:
            return super().getWebUrl()
        else:
            return self.v_info["url"]
    
    def setWebUrl(self, url: str):
        if self.has_local:
            return super().setWebUrl(url)
        else:
            ...
    
    def writeTags(self, tags: list):
        if self.has_local:
            return super().writeTags(tags)
        else:
            ...
    
    def openFile(self):
        if self.has_local:
            return super().openFile()
        else:
            ...
    
    def openMiscDir(self):
        if self.has_local:
            return super().openMiscDir()
        else:
            ...
    
    def openComments(self):
        if self.has_local:
            return super().openComments()
        else:
            ...
    
    def openBib(self):
        if self.has_local:
            return super().openBib()
        else:
            ...

    def deleteDocument(self) -> bool:
        if self.has_local:
            return super().deleteDocument()
        else:
            ...
    
    def _log(self):
        if self.has_local:
            return super()._log()
        else:
            ...