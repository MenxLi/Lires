"""
To expose the interfaces as a server,
thus the client don't need to install the heavy packages...
"""
import uvicorn
import fastapi, openai
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import numpy as np
from sklearn.manifold import TSNE 
from sklearn.decomposition import PCA

import os, asyncio
import json

from .utils import autoTorchDevice

from .lmTools import EncoderT, _default_encoder
from .lmTools import featurize as lmFeaturize
from .lmInterface import ChatStreamIterType, getStreamIter

from . import globalConfig as config
from ..entry import startService

from lires.core.base import G
from lires.api import RegistryConn

logger = G.loggers.get("ai")
g_warmup = False
app = fastapi.FastAPI()
registry = RegistryConn()

@app.get("/status")
def status():
    return {
        "status": "ok" if g_warmup else "warming up",
        "device": autoTorchDevice(),
        }

class FeaturizeRequest(BaseModel):
    text: str
    word_chunk: int = 256
    model_name: EncoderT = _default_encoder
    dim_reduce: bool = False
@app.post("/featurize")
async def featurize(req: FeaturizeRequest):
    await logger.debug(f"Featurize request: {req.model_name} | {req.text[:20]}")
    feat = lmFeaturize(req.text, req.word_chunk, req.model_name, req.dim_reduce)
    return feat.tolist()

class ChatBotRequest(BaseModel):
    prompt: str
    model_name: ChatStreamIterType = "DEFAULT"
    temperature: float = 0.7
    conv_dict: str = '{\
        "system": "A conversation between a human and an AI assistant.",\
        "conversations": []\
    }'
@app.post("/chatbot")
async def chatbot(req: ChatBotRequest):
    await logger.debug(f"Chatbot request: {req.model_name} | {req.conv_dict[:20]}")
    if req.model_name == "DEFAULT":
        req.model_name = config.defaultChatModel()

    def _chatbot():
        ai = getStreamIter(req.model_name)
        ai.temperature = req.temperature
        ai.return_pieces = True
        conv_dict = json.loads(req.conv_dict)
        ai.conversations.setFromDict(conv_dict)
        for piece in ai(req.prompt):
            yield piece["text"]
    return StreamingResponse(_chatbot(), media_type="text/plain")


class DimReduceTSNERequest(BaseModel):
    data: list[list[float]]
    n_components: int = 3
    perplexity: int = 30
    random_state: int = 100
    n_iter: int = 5000
@app.get("/dim-reduce/tsne")
def tsne(req: DimReduceTSNERequest):
    asyncio.run(logger.info(f"TSNE request: data - {len(req.data)} "))
    res = TSNE(
        n_components=req.n_components, 
        random_state=req.random_state, 
        perplexity=req.perplexity, 
        n_jobs=None, 
        n_iter=5000
        ).fit_transform(np.array(req.data)).astype(np.float16)
    return res.tolist()

class DimReducePCARequest(BaseModel):
    data: list[list[float]]
    n_components: int = 3
    random_state: int = 100
@app.get("/dim-reduce/pca")
def pca(req: DimReducePCARequest):
    asyncio.run(logger.info(f"PCA request: data - {len(req.data)}"))
    res = PCA(
        n_components=req.n_components, 
        random_state=req.random_state, 
        ).fit_transform(np.array(req.data)).astype(np.float16)
    return res.tolist()

@app.on_event("shutdown")
async def shutdown():
    await registry.withdraw()

async def startServer(
    host: str = "0.0.0.0",
    port: int = 8731,
    local_llm_chat: str = "",
    openai_models: list[str] = [],
):
    if port <= 0:
        from .. import avaliablePort
        port = avaliablePort()

    import uuid
    await registry.register({
        "uid": uuid.uuid4().hex,
        "name": "ai",
        "endpoint": f"http://{host}:{port}",
        "description": "LiresAI server",
        "group": None
    })

    # load config into global config
    if local_llm_chat:
        config.local_llm_name = local_llm_chat
    if openai_models:
        config.openai_api_chat_models = openai_models
    
    if os.getenv("OPENAI_API_KEY") is None:
        await logger.warning("OPENAI_API_KEY not set, please set it to use openai models")
        if os.getenv("OPENAI_API_BASE"):
            # set a dummy key, so that openai api will not raise error
            openai.api_key="sk-dummy__"

    async def warmup():
        global g_warmup
        await logger.info("Warming up text encoder...")
        lmFeaturize("Hello world!")
        if config.local_llm_name is not None:
            getStreamIter("LOCAL")
        await logger.info("Warming up text encoder done!")
        g_warmup = True
    await logger.info("Using device: {}".format(autoTorchDevice()))
    await warmup()
    await startService(
        app = app,
        host = host,
        port = port,
        logger=logger,
    )

