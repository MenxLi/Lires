"""
To expose the interfaces as a server,
thus the client don't need to install the heavy packages...
"""
import asyncio, json

import fastapi
from fastapi.responses import StreamingResponse

import logging
from pydantic import BaseModel
import deprecated

from . import initLogger
from .utils import autoTorchDevice

from .lmTools import EncoderT, _default_encoder
from .lmTools import featurize as lmFeaturize
from .lmTools import structuredSummerize as lmStructuredSummerize
from .lmInterface import ChatStreamIterType, getStreamIter

from . import globalConfig as config

logger = logging.getLogger("iLires")

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
    model_name: ChatStreamIterType = "gpt-3.5-turbo"
    temperature: float = 0.7
    conv_dict: str = '{\
        "system": "A conversation between a human and an AI assistant.",\
        "conversations": []\
    }'
@app.post("/chatbot")
def chatbot(req: ChatBotRequest):
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
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8731)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--log-level", type=str, default="info")
    parser.add_argument("--openai-api-base", type=str, default=config.openai_api_base)
    parser.add_argument("--fastchat-api-base", type=str, default=config.fastchat_api_base)
    args = parser.parse_args()

    initLogger(args.log_level)
    logger.info("Using device: {}".format(autoTorchDevice()))

    config.openai_api_base = args.openai_api_base
    config.fastchat_api_base = args.fastchat_api_base

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level=args.log_level,
        )

if __name__ == "__main__":
    logger.info("Starting iLires server...")
    main()