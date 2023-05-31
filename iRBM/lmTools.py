
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
async def structuredSummerize(txt: str, model: StreamIterType = "openai-gpt3.5", print_func: Callable = dummy_print) -> str:
    PRINT = True
    if print_func is dummy_print:
        PRINT = False

    ai = getStreamIter(model)

    prompt = "I'm going to ask you to summarize the following paper, "\
        "in the following three aspects: background and motivations, methods and contributions. "\
        "Your summary should be in academic literature style. Don't exagerate the significance. "\
        f"Here is the paper: {txt}"
    
    # if PRINT: print("Background and Motivations: ", end="")
    prompt += "\n\n Now please summarize the paper's background and motivations in 100 words. "\
        "Your response should start with \'Background and Motivations: \'"
    background = streamOutput(ai(prompt), print_func)

    # if PRINT: print("Methods: ", end="")
    prompt = "Now please summarize the paper's methods in 100 words. "\
        "Your response should start with \'Methods: \'"
    methods = streamOutput(ai(prompt), print_func)

    # if PRINT: print("Contributions: ", end="")
    prompt = "Now please summarize the paper's contributions in 100 words. "\
        "Your response should start with \'Contributions: \'"
    contributions = streamOutput(ai(prompt), print_func)

    return f"Background and Motivations: {background}\n{methods}\n{contributions}"


bert_tokenizer = None
bert_model = None
# reference: https://towardsdatascience.com/feature-extraction-with-bert-for-text-classification-533dde44dc2f
@torch.inference_mode()
async def vectorize(txt: str, max_len: int = 2048) -> np.ndarray:
    global bert_tokenizer, bert_model
    device = autoTorchDevice()
    txt = txt.replace("\n", " ")
    txt = " ".join(txt.split())

    if bert_tokenizer is None or bert_model is None:
        bert_tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        bert_model = AutoModel.from_pretrained("distilbert-base-uncased").to(device)

    inputs = bert_tokenizer(txt, return_tensors="pt", padding=True, truncation=True, max_length=max_len).to(device)
    hidden = bert_model(**inputs).last_hidden_state[:, 0, :].detach().cpu().numpy()  # [1, 768]
    return hidden
