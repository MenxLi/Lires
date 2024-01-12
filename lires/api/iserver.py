"""
Interface for server connections,
"""

from __future__ import annotations
import aiohttp
from lires.core.base import LiresBase
from lires.core import globalVar as G
from typing import TYPE_CHECKING, Optional, TypedDict, AsyncIterator
import json
import sys
if sys.version_info < (3, 9):
    from typing import Iterator
else:
    from collections.abc import Iterator

if TYPE_CHECKING:
    from lires_ai.lmInterface import ConversationDictT, ChatStreamIterType

class IServerConn(LiresBase):
    """Connection to lires_ai.server"""

    logger = LiresBase.loggers().core

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
    
    def _checkRes(self, res: aiohttp.ClientResponse) -> bool:
        if res.status != 200:
            self.logger.error("Server returned {}".format(res.status))
            return False
        return True
    
    _StatusReturnT = TypedDict("_StatusReturnT", {"status": bool, "device": str})
    @property
    async def status(self) -> _StatusReturnT:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url + "/status") as res:
                if self._checkRes(res):
                    return await res.json()
                else:
                    return {"status": False, "device": "unknown"}
    
    async def featurize(
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
        async with aiohttp.ClientSession() as session:
            async with session.post(post_url, json = post_args) as res:
                if self._checkRes(res):
                    return await res.json()
                else:
                    return None
    
    _ChatReturnT = AsyncIterator[str]
    async def chat(
            self, 
            prompt: str, 
            conv_dict: Optional[ConversationDictT] = None, 
            model_name: Optional[ChatStreamIterType] = None,
            ) -> _ChatReturnT:    # type: ignore
        """
        return empty string if error
        """
        post_url = self.url + "/chatbot"
        post_args = {
            "prompt": prompt
        }
        if conv_dict is not None:
            post_args["conv_dict"] = json.dumps(conv_dict)
        if model_name is not None:
            post_args["model_name"] = model_name

        async with aiohttp.ClientSession() as session:
            async with session.post(post_url, json = post_args) as res:
                if self._checkRes(res):
                    async for chunk in res.content.iter_chunked(128):
                        if chunk:
                            yield chunk.decode("utf-8")
                else: yield ""