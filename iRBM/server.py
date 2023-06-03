"""
To expose the interfaces as a server,
thus the client don't need to install the heavy packages...
"""
import asyncio

import fastapi
from fastapi.responses import StreamingResponse

import logging
from pydantic import BaseModel

from . import initLogger
from .utils import autoTorchDevice

from .lmTools import EncoderT, _default_encoder
from .lmTools import featurize as lmFeaturize
from .lmTools import structuredSummerize as lmStructuredSummerize

from .lmInterface import Conversation, ConvRole, ConvContent, StreamIterType, getStreamIter, ConversationDictT

from .textFeature import queryFeatureIndex as tfQueryFeatureIndex

logger = logging.getLogger("iRBM")

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

class QueryFeatureIndexRequest(BaseModel):
    text: str
    n_return: int = 16
@app.post("/queryFeatureIndex")
def queryFeatureIndex(req: QueryFeatureIndexRequest):
    res = tfQueryFeatureIndex(req.text, req.n_return)
    return{
        "uids": res["uids"],
        "scores": res["scores"],
    }

class ChatBotRequest(BaseModel):
    prompt: str
    model_name: StreamIterType = "vicuna-13b"
    temperature: float = 0.7
    conv_dict: ConversationDictT = {
        "system": "A conversation between a human and an AI assistant.",
        "conversations": []
    }
@app.post("/chatbot")
def chatbot(req: ChatBotRequest):
    def _chatbot():
        ai = getStreamIter(req.model_name)
        ai.temperature = req.temperature
        ai.return_pieces = True
        ai.conversations.setFromDict(req.conv_dict)
        for piece in ai(req.prompt):
            yield piece["text"]
    return StreamingResponse(_chatbot(), media_type="text/plain")


def main():
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8731)
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--log-level", type=str, default="info")
    args = parser.parse_args()

    initLogger(args.log_level)

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level=args.log_level,
        )

if __name__ == "__main__":
    logger.info("Starting iRBM server...")
    main()