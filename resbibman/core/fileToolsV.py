"""
Virtual (Remote) file tools
"""
from __future__ import annotations
import os, typing, requests, zipfile, shutil
from typing import TYPE_CHECKING, Union, overload, Literal

from . import globalVar as G
from .utils import strtimeToDatetime
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
        self.init()
    
    def _forceOffline(self):
        self.__force_offline = True
    
    @property
    def v_info(self) -> Union[DataPointInfo, dict]:
        """ Virtual file info (from remote) """
        if hasattr(self, "_v_info"):
            return self._v_info
        else:
            return dict()

    @v_info.setter
    def v_info(self, v_info_update: DataPointInfo):
        # Maybe update v_info when synchronized
        self._v_info = v_info_update

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
    def is_uptodate(self) -> Literal["behind", "same", "advance"]:
        """
        Check if a local file is up to date with remote,
        """
        if not self.has_local:
            return "same"

        local_time_modified = strtimeToDatetime(self.getTimeModified())
        remote_time_modified = strtimeToDatetime(self.v_info["time_modified"])

        if local_time_modified == remote_time_modified:
            return "same"
        elif local_time_modified > remote_time_modified:
            return "advance"
        else:
            return "behind"

    def _sync(self) -> bool:
        """
        Sync with remote, data is assumed to be both local (may in virtual form) and remote
        use self._uploadRemote to upload a new file
        Please use DataPoint.sync()
        """
        if self.offline:
            return False
        if self.offline:
            self.logger.info("Set host to enable online mode")
            return False
        if not self.has_local:
            # download if not loacl
            return self._downloadRemote()
        # Check is_uptodate when uploading
        update_status = self.is_uptodate
        if update_status == "advance":
            self.logger.info("sync (fm): uploading {}".format(self.uuid))
            return self._uploadRemote()
        elif update_status == "behind":
            self.logger.warning("sync (fm): Remote file may have been changed, failed uploading {}".format(self.uuid))
            return False
        else:
            # same
            self.logger.debug("sync (fm): remote unchanged {}".format(self.uuid))
            return True
    
    def _uploadRemote(self) -> bool:
        if self.offline:
            return False
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
            #  try:
            #      res = requests.post(self.POST_URL, params = post_args, files=file_args)
            #  except requests.exceptions.ConnectionError:
            #      self.logger.info("uploadRemote (fm): Connection error")
            #      G.last_status_code = 0
            #      return False

        if not self._checkRes(res):
            return False
        else:
            return True

    def _downloadRemote(self) -> bool:
        if self.offline:
            return False
        uuid = self.uuid
        post_args = {
            "key": generateHexHash(getConfV("access_key")),
            "cmd": "download",
            "uuid": uuid
        }
        res = requests.post(self.POST_URL, params = post_args)
        #  try:
        #      res = requests.post(self.POST_URL, params = post_args)
        #  except requests.exceptions.ConnectionError:
        #      self.logger.info("downloadRemote (fm): Connection error")
        #      G.last_status_code = 0
        #      return False
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
        self.logger.debug("Request remote delete {}".format(uuid))
        res = requests.post(self.POST_URL, params = post_args)
        #  try:
        #      res = requests.post(self.POST_URL, params = post_args)
        #  except requests.exceptions.ConnectionError:
        #      self.logger.info("deleteRemote (fm): Connection error")
        #      G.last_status_code = 0
        #      return False
        if not self._checkRes(res):
            self.logger.warning("Remote delete failed for {}".format(uuid))
            return False
        return True
    
    def _checkRes(self, res: requests.Response) -> bool:
        """
        Check if response is valid
        """
        status_code = res.status_code
        if status_code != 200:
            self.logger.debug("Get response {}".format(res.status_code))
        if status_code == 401:
            self.logger.warning("Unauthorized access")
        G.last_status_code = res.status_code
        return res.ok

    #=========================== Below emulate local manipulator class

    def _createFileOB(self):
        if self.has_local:
            return super()._createFileOB()
        else:
            raise ValueError("File not local")

    def screen(self) -> bool:
        if self.has_local:
            return super().screen()
        else:
            return True

    def changeBasename(self, new_basename: str) -> bool:
        if self.has_local:
            name_changed = super().changeBasename(new_basename)    
            # delete remote old
            if name_changed and not self.offline:
                self._deleteRemote()
            return name_changed
        else:
            raise NotImplementedError
    
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
            return ""
    
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
            raise NotImplementedError

    def setWatch(self, status: bool):
        if self.has_local:
            return super().setWatch(status)
        else:
            ...
    
    def _log(self):
        if self.has_local:
            return super()._log()
        else:
            ...
