"""
To expose the interfaces as a server,
thus the client don't need to install the heavy packages...
"""
import asyncio, json

import fastapi, openai
from fastapi.responses import StreamingResponse

import logging
from pydantic import BaseModel

from . import initLogger
from .utils import autoTorchDevice

from .lmTools import EncoderT, _default_encoder
from .lmTools import featurize as lmFeaturize
from .lmInterface import ChatStreamIterType, getStreamIter

from . import globalConfig as config

logger = logging.getLogger("LiresAI")

app = fastapi.FastAPI()

@app.get("/status")
def status():
    return {
        "status": "ok",
        "device": autoTorchDevice(),
        }

class FeaturizeRequest(BaseModel):
    text: str
    word_chunk: int = 256
    model_name: EncoderT = _default_encoder
    dim_reduce: bool = False
@app.post("/featurize")
def featurize(req: FeaturizeRequest):
    feat = asyncio.run(lmFeaturize(req.text, req.word_chunk, req.model_name, req.dim_reduce))
    return {
        "feature": feat.tolist(),
    }

class ChatBotRequest(BaseModel):
    prompt: str
    model_name: ChatStreamIterType = "DEFAULT"
    temperature: float = 0.7
    conv_dict: str = '{\
        "system": "A conversation between a human and an AI assistant.",\
        "conversations": []\
    }'
@app.post("/chatbot")
def chatbot(req: ChatBotRequest):
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


def main():
    import argparse, threading, os
    import uvicorn
    from lires.parser import prepareIServerParser

    parser = argparse.ArgumentParser(description="LiresAI server")
    parser = prepareIServerParser(parser)
    args = parser.parse_args()

    initLogger("info")

    # load config into global config
    if args.local_llm_chat:
        config.local_llm_name = args.local_llm_chat
    if args.openai_models:
        config.openai_api_chat_models = args.openai_models
    
    if os.getenv("OPENAI_API_KEY") is None:
        logger.warning("OPENAI_API_KEY not set, please set it to use openai models")
        if os.getenv("OPENAI_API_BASE"):
            # set a dummy key, so that openai api will not raise error
            openai.api_key="sk-dummy__"

    def warmup():
        logger.info("Warming up...")
        asyncio.run(lmFeaturize("Hello world!"))
        if config.local_llm_name is not None:
            getStreamIter("LOCAL")

        logger.info("Warmup done!")
    threading.Thread(target = warmup, daemon=True).start()

    logger.info("Using device: {}".format(autoTorchDevice()))

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info",
        workers=1,
        )

if __name__ == "__main__":
    logger.info("Starting LiresAI server...")
    main()