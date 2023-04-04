
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List
import asyncio
import requests, json
from . import globalVar as G
from .encryptClient import generateHexHash
from ..confReader import getServerURL, getConfV

if TYPE_CHECKING:
    from resbibman.server.auth.account import AccountPermission
    from resbibman.core.dataSearcher import StringSearchT
    from resbibman.core.dataClass import DataTagT, DataPointSummary

class ServerConn:

    @property
    def hash_key(self):
        return generateHexHash(getConfV("access_key"))
    
    @property
    def logger(self):
        return G.logger_rbm
    
    @property
    def SERVER_URL(self):
        return getServerURL()

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

    def permission(self) -> Optional[AccountPermission]:
        post_url = self.SERVER_URL + "/auth"
        post_args = {
            "key": self.hash_key,
            "require_permission": True
        }
        res = requests.post(post_url, data = post_args)
        if not self._checkRes(res):
            return None
        else:
            return json.loads(res.text)
    
    def search(self, method: str, kwargs: dict) -> Optional[StringSearchT]:
        post_url = self.SERVER_URL + "/search"
        post_args = {
            "key": self.hash_key,
            "method":method,
            "kwargs": json.dumps(kwargs)
        }
        res = requests.post(post_url, data = post_args)
        if not self._checkRes(res):
            return None
        else:
            return json.loads(res.text)
    
    def filelist(self, tags: DataTagT = []) -> Optional[List[DataPointSummary]]:
        post_url = self.SERVER_URL + "/filelist"
        post_args = {
            "tags": json.dumps([ t for t in tags])
        }
        res = requests.post(post_url, data = post_args)
        if not self._checkRes(res):
            return None
        else:
            return json.loads(res.text)["data"]
    
    def reloadDB(self) -> bool:
        post_url = self.SERVER_URL + "/cmd/reloadDB"
        res = requests.get(post_url, timeout=5)
        if not self._checkRes(res):
            return False
        else:
            return True
    
    def deleteTag(self, tag_to_be_deleted: str):
        post_args = {
            "key": self.hash_key,
            "cmd": "deleteTagAll",
            "uuid": "_",
            "args": json.dumps([tag_to_be_deleted]),
            "kwargs": json.dumps({})
        }
        return self._remoteCMD(post_args)

    def renameTag(self, src_tag: str, dst_tag: str):
        post_args = {
            "key": self.hash_key,
            "cmd": "renameTagAll",
            "uuid": "_",
            "args": json.dumps([src_tag, dst_tag]),
            "kwargs": json.dumps({})
        }
        return self._remoteCMD(post_args)

    def _remoteCMD(self, post_args) -> bool:
        """
        post command to remote/cmdA
        """
        post_addr = "{}/cmdA".format(self.SERVER_URL) 
        res = requests.post(post_addr, params = post_args)
        if not self._checkRes(res):
            return False
        return True