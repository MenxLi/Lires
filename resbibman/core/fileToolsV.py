"""
Virtual (Remote) file tools
"""
from __future__ import annotations
import os, typing, requests, zipfile, shutil
from typing import TYPE_CHECKING, Union, overload

from .fileTools import FileGenerator, FileManipulator
from .encryptClient import generateHexHash
from .compressTools import decompressDir, compressDir
from ..confReader import getConfV, TMP_DB, getConf, TMP_DIR

if TYPE_CHECKING:
    from RBMWeb.backend.rbmlibs import DataPointInfo

class FileManipulatorVirtual(FileManipulator):
    """
    Virtual file manipulator | Local file manipulator
    Provide some API at start
    To download from server and pass control to local FileManipulator
    """
    HOST_URL = "http://{}:{}".format(getConfV("host"), getConfV("port"))
    POST_URL = f"{HOST_URL}/file"
    INTERM_ZIP_DIR = os.path.join(TMP_DIR, "fm_zips")
    if not os.path.exists(INTERM_ZIP_DIR):
        os.mkdir(INTERM_ZIP_DIR)
    def __init__(self, v: Union[DataPointInfo, str]):
        """
         - v [DataPointInfo]: dictionary datapoint info,
                to construct vitrual file manipulator
         - v [str]: local data path, 
                to construct local file manipulator
        """
        self.__force_offline = False
        if isinstance(v, str):
            super().__init__(v)
        else:
            assert not self.offline
            self.base_name = v["base_name"]
            self._file_extension = v["file_type"]
            self.path = os.path.join(TMP_DB, self.base_name)

            self._v_info = v    # a backup of the Datapoint Info
    
    def _forceOffline(self):
        self.__force_offline = True
    
    @property
    def v_info(self) -> Union[DataPointInfo, dict]:
        """ Virtual file info """
        if hasattr(self, "_v_info"):
            return self._v_info
        else:
            return dict()

    @property
    def offline(self) -> bool:
        if self.__force_offline:
            return True
        return getConfV("host") == ""

    @property
    def has_local(self) -> bool:
        """
        check if has (synchronized) local file
        """
        if self.offline:
            return True
        return os.path.exists(self.path)

    @property
    def is_uptodate(self) -> bool:
        """
        Check if a local file is up to date with remote,
        """
        if not self.has_local:
            return False

        # To change later
        # ...

        return True

    def _sync(self, v_info_update: DataPointInfo) -> bool:
        """
        Download if not local
        Upload if has local file and uptodate
        """
        if self.offline:
            return
        print(v_info_update)
        # Check is_uptodate when uploading
        if self.offline:
            self.logger.info("Set host to enable online mode")
            return False
        if not self.has_local:
            return self._downloadRemote()
    
    def _uploadRemote(self) -> bool:
        if self.offline:
            return
        uuid = self.uuid
        interm_file_p = os.path.join(self.INTERM_ZIP_DIR, uuid + ".zip")
        compressDir(self.path, interm_file_p)
        post_args = {
            "key": generateHexHash(getConfV("access_key")),
            "cmd": "upload",
            "uuid": uuid
        }
        with open(interm_file_p, "rb") as fp:
            file_args = {
                "filename": self.base_name.encode("utf-8"),
                "file": fp
            }
            res = requests.post(self.POST_URL, params = post_args, files=file_args)

        if not self._checkRes(res):
            return False
        else:
            return True

    def _downloadRemote(self) -> bool:
        if self.offline:
            return
        uuid = self.uuid
        post_args = {
            "key": generateHexHash(getConfV("access_key")),
            "cmd": "download",
            "uuid": uuid
        }
        res = requests.post(self.POST_URL, params = post_args)
        if not self._checkRes(res):
            return False
        out_file = os.path.join(self.INTERM_ZIP_DIR, uuid + ".zip")
        # intermediate zip file
        with open(out_file, "wb") as fp:
            fp.write(res.content)
        # delete old data
        if os.path.exists(self.path):
            shutil.rmtree(self.path)
        # unzip
        decompressDir(out_file, self.path)
        self.logger.info("Downloaded {}".format(uuid))
        return self.screen()
    
    def _deleteRemote(self) -> bool:
        if self.offline:
            return False
        uuid = self.uuid
        post_args = {
            "key": generateHexHash(getConfV("access_key")),
            "cmd": "delete",
            "uuid": uuid
        }
        res = requests.post(self.POST_URL, params = post_args)
        if not self._checkRes(res):
            return False
        return True
    
    def _checkRes(self, res: requests.Response) -> bool:
        """
        Check if response is valid
        """
        status_code = res.status_code
        if status_code == 401:
            self.logger.info("Unauthorized access")
        return res.ok

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
            # delete remote old
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