"""
Interface for server connections,
refer to lires.server for more information
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Literal, TypedDict
from abc import abstractproperty
import deprecated
import requests, json
from . import globalVar as G
import sys
if sys.version_info < (3, 9):
    from typing import Iterator
else:
    from collections.abc import Iterator

if TYPE_CHECKING:
    from lires.user import UserInfo
    from lires.core.dataSearcher import StringSearchT
    from lires.core.dataClass import DataTagT, DataPointSummary
    from lires.core.dbConn import DBFileInfo
    from lires_ai.lmInterface import ConversationDictT, ChatStreamIterType

class ConnectionBase:
    @abstractproperty
    def hash_key(self) -> str:
        ...
    
    @property
    def logger(self):
        return G.logger_lrs

    def _checkRes(self, res: requests.Response) -> bool:
        """
        Check if response is valid
        """
        status_code = res.status_code
        if status_code != 200:
            self.logger.debug("Get response {}".format(res.status_code))
        if status_code == 403:
            self.logger.warning("Unauthorized access")
        G.last_status_code = res.status_code
        return res.ok


class ServerConn(ConnectionBase):
    """
    Connection to lires.server
    This class is highly unfinished and untested, 
    More features will be added in the future.
    
    **
        There used to be an online mode using this class, with a GUI written in PyQt6,
        now it is deprecated and the interface is not actively maintained.
    **

    """

    def __init__(self, api_url: str, hash_key: str = "") -> None:
        self.__hash_key = hash_key
        self.__api_url = api_url
    
    @property
    def hash_key(self) -> str:
        return self.__hash_key
    
    @property
    def SERVER_URL(self):
        if self.__api_url.endswith("/"):
            return self.__api_url[:-1]
        return self.__api_url

    def permission(self) -> Optional[UserInfo]:
        post_url = self.SERVER_URL + "/auth"
        post_args = { "key": self.hash_key, }
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
    
    def summaries(self, tags: DataTagT = []) -> Optional[List[DataPointSummary]]:
        post_url = self.SERVER_URL + "/filelist"
        post_args = {
            "key": self.hash_key,
            "tags": json.dumps([ t for t in tags])
        }
        res = requests.post(post_url, data = post_args, timeout=5)
        if not self._checkRes(res):
            return None
        else:
            return json.loads(res.text)
    
    def reloadDB(self) -> bool:
        post_url = self.SERVER_URL + "/reload-db"
        res = requests.post(post_url, data = {"key": self.hash_key}, timeout=5)
        if not self._checkRes(res):
            return False
        else:
            return True
        
    def deleteTag(self, tag_to_be_deleted: str) -> bool:
        post_url = self.SERVER_URL + "/dataman/tag-delete"
        post_args = {
            "key": self.hash_key,
            "tag": tag_to_be_deleted
        }
        res = requests.post(post_url, data = post_args)
        return self._checkRes(res)

    def renameTag(self, src_tag: str, dst_tag: str) -> bool:
        post_url = self.SERVER_URL + "/dataman/tag-rename"
        post_args = {
            "key": self.hash_key,
            "oldTag": src_tag,
            "newTag": dst_tag
        }
        res = requests.post(post_url, data = post_args)
        return self._checkRes(res)
    
    def getDocURL(self, uid: str, dtype: Literal["pdf, hpack"]) -> str:
        if dtype == "pdf":
            return self.SERVER_URL + "/doc/{}".format(uid)
        elif dtype == "hpack":
            return self.SERVER_URL + "/hdoc/{}/".format(uid)
        else:
            raise NotImplementedError

    def getNoteURL(self, uid: str) -> str:
        return self.SERVER_URL + "/comment/{}/".format(uid)
    
class IServerConn(ConnectionBase):
    """Connection to lires_ai.server"""

    def __init__(self, host: str = "", port: str|int = "") -> None:
        super().__init__()
        if host == "":
            if G.iserver_host:
                host = G.iserver_host
            else:
                host = "127.0.0.1"

        if port == "":
            if G.iserver_port:
                port = G.iserver_port
            else:
                port = 8731

        self._host = host
        self._port = str(port)

    @property
    def url(self) -> str:
        return "http://{}:{}".format(self._host, self._port)
    
    _StatusReturnT = TypedDict("_StatusReturnT", {"status": bool, "device": str})
    @property
    def status(self) -> Optional[_StatusReturnT]:
        res = requests.get(self.url + "/status")
        if self._checkRes(res):
            return res.json()
        else:
            return None
    
    def featurize(
            self, 
            text: str,
            # word_chunk: int = 256,
            # model_name: EncoderT = "bert-base-uncased",
            dim_reduce: bool = True
            ) -> Optional[list]:
        post_url = self.url + "/featurize"
        post_args = {
            "text": text,
            # "word_chunk": word_chunk,
            # "model_name": model_name,
            "dim_reduce": dim_reduce
        }
        res = requests.post(post_url, json = post_args)
        if self._checkRes(res):
            return res.json()["feature"]
        else:
            return None
    
    _qFeatIndexT = TypedDict("_qFeatIndexT", {"uids": List[str], "scores": List[float]})
    @deprecated.deprecated(version = "0.14.0", reason = "feature index should be stored via core module instead of iserver")
    def queryFeatureIndex(self, text: str, n_return: int = 10) -> Optional[_qFeatIndexT]:
        post_url = self.url + "/queryFeatureIndex"
        post_args = {
            "text": text,
            "n_return": n_return
        }
        res = requests.post(post_url, json = post_args)
        if self._checkRes(res):
            return res.json()
        else:
            return None
    
    _ChatReturnT = Iterator[str]
    def chat(
            self, 
            prompt: str, 
            conv_dict: Optional[ConversationDictT] = None, 
            model_name: Optional[ChatStreamIterType] = None,
            ) -> Optional[_ChatReturnT]:    # type: ignore
        post_url = self.url + "/chatbot"
        post_args = {
            "prompt": prompt
        }
        if conv_dict is not None:
            post_args["conv_dict"] = json.dumps(conv_dict)
        if model_name is not None:
            post_args["model_name"] = model_name

        res = requests.post(post_url, json = post_args, stream=True)
        if self._checkRes(res):
            for content in res.iter_content(chunk_size=128):
                if content:
                    chunk:str = content.decode("utf-8")
                    yield chunk
        else:
            return None
