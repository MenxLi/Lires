
"""Language Model Tools"""

import asyncio

from typing import Callable
from .lmInterface import StreamData, Iterator
from .lmInterface import getStreamIter, streamOutput, StreamIterType
from .utils import autoTorchDevice, MuteEverything

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel

def summarize(txt: str) -> Iterator[StreamData]:
    from .lmInterface import OpenAIStreamIter
    prompt = f"Summarize the following paper, "\
        "your summary should focus on the motivation, methods and contributions of the paper. "\
        "Your summary should be in academic literature style. Don't exagerate the significance. "\
        f"Here is the paper: {txt}"
    return OpenAIStreamIter()(prompt)

dummy_print = lambda x, end = " ", flush = True: ...
async def structuredSummerize(txt: str, model: StreamIterType = "gpt-3.5-turbo", print_func: Callable = dummy_print) -> str:
    PRINT = True
    if print_func is dummy_print:
        PRINT = False

    ai = getStreamIter(model)
    ai.conversations.system = "A conversation between a human and an AI research assistant. "\
        "The human is asking the AI to summarize a paper."\
        "The AI gives short and conscise response in academic literature style. "\

    prompt = "Please summarize the following paper in about 200 words, "\
        "your summary should be 3 paragraphs, each paragraph should start with \'Background and Motivations: \', "\
        "\'Methods: \' and \'Contributions: \' respectively. "\
        "No need to mention the title in your summary."\
        f"Here is the paper: {txt}"
    return streamOutput(ai(prompt), print_func)


bert_tokenizer = None
bert_model = None
# reference: https://towardsdatascience.com/feature-extraction-with-bert-for-text-classification-533dde44dc2f
@torch.inference_mode()
async def vectorize(txt: str, max_len: int = 512, verbose = False) -> torch.Tensor:
    """
    take a long text and return a vector of shape [1, d_feature]
    """
    global bert_tokenizer, bert_model
    device = autoTorchDevice()
    txt = txt.replace("\n", " ")
    txt = " ".join(txt.split())

    if bert_tokenizer is None or bert_model is None:
        bert_tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        bert_model = AutoModel.from_pretrained("distilbert-base-uncased").to(device)

    inputs = bert_tokenizer(txt, return_tensors="pt", padding=True, truncation=True, max_length=max_len).to(device)
    hidden = bert_model(**inputs).last_hidden_state[:, 0, :].detach()  # [1, 768]

    with MuteEverything(enable=not verbose):
        if len(inputs['input_ids'][0]) == 512:   # type: ignore
            print("Warning<vectorize>: input text is too long, truncated.")
    return hidden

async def featurize(txt: str, word_chunk: int = 256, verbose = False, supress_last = True, dim_reduct = False) -> torch.Tensor:
    """
    take a long text and return a vector of shape [n, d_feature]
    if supress_last is True, the last chunk will be weighted by the ratio of the number of words in the last chunk to word_chunk
    if dim_reduct is True, the output will be of shape [1, d_feature]
    """
    if txt == "":
        txt = " "
    txt_split = txt.split()
    txt_chunks = [" ".join(txt_split[i:i+word_chunk]) for i in range(0, len(txt_split), word_chunk)]
    if supress_last:
        last_chunk_weight = len(txt_chunks[-1].split()) / word_chunk
    else:
        last_chunk_weight = 1.
    _vec_chunk_tasks = [vectorize(chunk, verbose=verbose) for chunk in txt_chunks]
    vec_chunks: list[torch.Tensor] = await asyncio.gather(*_vec_chunk_tasks)
    vec_chunks[-1] = vec_chunks[-1] * last_chunk_weight
    feats = torch.cat(vec_chunks, dim=0)    # [n, d_feature]
    if not dim_reduct:
        return feats
    else:
        feat = torch.sum(feats, dim=0, keepdim=False)  # [d_feature]
        feat = feat / (feats.shape[0] - 1 + last_chunk_weight)
        return feat
