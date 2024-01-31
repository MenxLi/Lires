"""
Interface for server connections,
"""

from __future__ import annotations
import aiohttp
from typing import TYPE_CHECKING, Optional, TypedDict, AsyncIterator
import json
from .common import LiresAPIBase
from .registry import RegistryConn

if TYPE_CHECKING:
    from lires_service.ai.lmInterface import ConversationDictT, ChatStreamIterType

class IServerConn(LiresAPIBase):
    """Connection to lires_ai.server"""

    def __init__(self, endpoint: Optional[str] = None) -> None:
        super().__init__()
        self._endpoint = endpoint
    
    def setEndpoint(self, endpoint: str) -> None:
        self._endpoint = endpoint

    async def url(self) -> str:
        if self._endpoint is None:
            return (await RegistryConn().get("ai"))["endpoint"]
        return self._endpoint
    
    _StatusReturnT = TypedDict("_StatusReturnT", {"status": bool, "device": str})
    @property
    async def status(self) -> _StatusReturnT:
        async with aiohttp.ClientSession() as session:
            async with session.get(await self.url() + "/status") as res:
                try:
                    self.ensureRes(res)
                    return await res.json()
                except self.Error.LiresConnectionError:
                    return {"status": False, "device": "unknown"}
    
    async def featurize(
            self, 
            text: str,
            # word_chunk: int = 256,
            # model_name: EncoderT = "bert-base-uncased",
            dim_reduce: bool = True
            ) -> list:
        post_url = await self.url() + "/featurize"
        post_args = {
            "text": text,
            # "word_chunk": word_chunk,
            # "model_name": model_name,
            "dim_reduce": dim_reduce
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(post_url, json = post_args) as res:
                self.ensureRes(res)
                return await res.json()
    
    async def chat(
            self, 
            prompt: str, 
            conv_dict: Optional[ConversationDictT] = None, 
            model_name: Optional[ChatStreamIterType] = None,
            ) -> AsyncIterator[str]:    # type: ignore
        """
        return empty string if error
        """
        post_url = await self.url() + "/chatbot"
        post_args = {
            "prompt": prompt
        }
        if conv_dict is not None:
            post_args["conv_dict"] = json.dumps(conv_dict)
        if model_name is not None:
            post_args["model_name"] = model_name

        async with aiohttp.ClientSession() as session:
            async with session.post(post_url, json = post_args) as res:
                try:
                    self.ensureRes(res)
                    async for chunk in res.content.iter_chunked(128):
                        if chunk:
                            yield chunk.decode("utf-8")
                except self.Error.LiresConnectionError:
                    yield ""
    
    async def tsne(self, 
        data: list[list[float]],
        n_components: int = 3,
        perplexity: int = 30,
        random_state: int = 100,
        n_iter: int = 1000,
        ) -> list[list[float]]:
        post_url = await self.url() + "/dim-reduce/tsne"
        post_args = {
            "data": data,
            "n_components": n_components,
            "perplexity": perplexity,
            "random_state": random_state,
            "n_iter": n_iter,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(post_url, json = post_args) as res:
                self.ensureRes(res)
                return await res.json()
    
    async def pca(self, 
        data: list[list[float]],
        n_components: int = 3,
        random_state: int = 100,
        ) -> list[list[float]]:
        post_url = await self.url() + "/dim-reduce/pca"
        post_args = {
            "data": data,
            "n_components": n_components,
            "random_state": random_state,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(post_url, json = post_args) as res:
                self.ensureRes(res)
                return await res.json()
            