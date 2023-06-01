
"""Language Model Tools"""

import asyncio

from typing import Callable
from .lmInterface import StreamData, Iterator
from .lmInterface import getStreamIter, streamOutput, StreamIterType
from .utils import autoTorchDevice

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

    prompt = "I'm going to ask you to summarize the following paper, "\
        "in the following three aspects: background and motivations, methods and contributions, "\
        "each in a paragraph around 50 words. "\
        "Your summary should be in academic literature style. Don't exagerate the significance. "\
        f"Here is the paper: {txt}"
    
    # if PRINT: print("Background and Motivations: ", end="")
    prompt += "\n\n Now summarize the paper's background and motivations. "\
        "Your response should start with \'Background and Motivations: \'"
    background = streamOutput(ai(prompt), print_func)

    # if PRINT: print("Methods: ", end="")
    prompt = "Summarize the paper's methods. "\
        "Your response should start with \'Methods: \'"
    methods = streamOutput(ai(prompt), print_func)

    # if PRINT: print("Contributions: ", end="")
    prompt = "Summarize the paper's contributions. "\
        "Your response should start with \'Contributions: \'"
    contributions = streamOutput(ai(prompt), print_func)

    return f"{background}\n{methods}\n{contributions}".replace("\n", "  ")


bert_tokenizer = None
bert_model = None
# reference: https://towardsdatascience.com/feature-extraction-with-bert-for-text-classification-533dde44dc2f
@torch.inference_mode()
async def vectorize(txt: str, max_len: int = 512, verbose = False) -> torch.Tensor:
    """
    take a long text and return a vector of shape [1, 768]
    """
    global bert_tokenizer, bert_model
    device = autoTorchDevice()
    txt = txt.replace("\n", " ")
    txt = " ".join(txt.split())

    if bert_tokenizer is None or bert_model is None:
        bert_tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        bert_model = AutoModel.from_pretrained("distilbert-base-uncased").to(device)

    inputs = bert_tokenizer(txt, return_tensors="pt", padding=True, truncation=True, max_length=max_len).to(device)
    if verbose and len(inputs['input_ids'][0]) == 512:   # type: ignore
        print("Warning<vectorize>: input text is too long, truncated.")
    hidden = bert_model(**inputs).last_hidden_state[:, 0, :].detach().cpu()  # [1, 768]
    return hidden

async def featurize(txt: str, word_chunk: int = 256, verbose = False, ignore_last = True) -> torch.Tensor:
    """
    take a long text and return a vector of shape [n, 768]
    """
    txt_split = txt.split()
    txt_chunks = [" ".join(txt_split[i:i+word_chunk]) for i in range(0, len(txt_split), word_chunk)]
    if ignore_last and len(txt_chunks) > 1:
        txt_chunks = txt_chunks[:-1]
    _vec_chunk_tasks = [vectorize(chunk, verbose=verbose) for chunk in txt_chunks]
    vec_chunks: list[torch.Tensor] = await asyncio.gather(*_vec_chunk_tasks)
    return torch.cat(vec_chunks, dim=0)