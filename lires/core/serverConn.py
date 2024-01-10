"""
Interface for server connections,
"""

from __future__ import annotations
from lires.core.base import LiresBase
from lires.core import globalVar as G
from typing import TYPE_CHECKING, Optional, TypedDict
import requests, json
import sys
if sys.version_info < (3, 9):
    from typing import Iterator
else:
    from collections.abc import Iterator

if TYPE_CHECKING:
    from lires_ai.lmInterface import ConversationDictT, ChatStreamIterType

class ConnectionBase(LiresBase):

    @property
    def logger(self):
        return LiresBase.loggers().core

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
