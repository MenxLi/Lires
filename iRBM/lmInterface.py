
"""Language Model Interface"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any, TypedDict, Literal, Type
import dataclasses, json

# check python version
import sys, os
if sys.version_info < (3, 9):
    from typing import Iterator
else:
    from collections.abc import Iterator

import openai
from . import globalConfig as config


ConvRole = Literal["user", "assistant"]
ConvContent = str
ConversationDictT = TypedDict("ConversationDictT", {
    "system": str,
    "conversations": list[tuple[ConvRole, ConvContent]]
})
@dataclasses.dataclass
class Conversation:
    system: str
    conversations: list[tuple[ConvRole, ConvContent]]
    def add(self, role: ConvRole, content: str):
        self.conversations.append((role, content))
    def clear(self):
        self.conversations = []
    def __str__(self) -> str:
        template = "[system]\n> {}\n".format(self.system)
        return template + "\n".join(["[{}]\n> {}".format(c[0], c[1]) for c in self.conversations])
    def toDict(self) -> ConversationDictT:
        return {
            "system": self.system,
            "conversations": self.conversations
        }
    def setFromDict(self, dict: ConversationDictT):
        self.system = dict["system"]
        self.conversations = dict["conversations"]
        return self
    @property
    def openai_conversations(self):
        system = [{"role": "system", "content": self.system}]
        conv = [{"role": c[0], "content": c[1]} for c in self.conversations]
        return system + conv

def streamOutput(output_stream: Iterator[StreamData], print_callback: Any = lambda x, end=" ", flush=True: ...):
    """
    Obtain the output from the stream, and maybe print it to stdout
    print_callback: a function that takes a string and print it to stdout, \
        should have the same interface as print (i.e. print_callback("hello", end=" ", flush=True))
    """
    try:
        print_callback("", end="", flush=True)
    except TypeError:
        raise TypeError("print_func should have the same interface as print, i.e. contains end and flush")

    pre = 0
    output_text = ""
    for outputs in output_stream:
        output_text = outputs["text"]
        output_text = output_text.strip().split(" ")
        now = len(output_text) - 1
        if now > pre:
            print_callback(" ".join(output_text[pre:now]), end=" ", flush=True)
            pre = now
    print_callback(" ".join(output_text[pre:]), flush=True)
    return " ".join(output_text)

class StreamData(TypedDict):
    """a class to represent the data returned by the model output stream"""
    text: str
    error_code: int

class StreamIter(ABC):
    """Abstract class for language model interface"""
    temperature = 0.8
    max_response_length = 1024
    conversations: Conversation

    # whether to return the pieces of the output stream or return the concatenated whole output stream
    return_pieces: bool = False     

    @abstractmethod
    def call(self, message: str, temperature: float, max_len: int = 1024) -> Iterator[StreamData]:
        ...
    def __call__(self, prompt) -> Iterator[StreamData]:
        return self.call(prompt, self.temperature, self.max_response_length)

class OpenAIStreamIter(StreamIter):

    def __init__(self, model: str = "gpt-3.5-turbo") -> None:
        super().__init__()
        self.model = model
        self.conversations = Conversation(system="A conversation between a human and an AI assistant.", conversations=[])
        if model in ["vicuna-13b"]:
            assert config.fastchat_api_base, "fastchat_api_base is not set"
    
    def generateMessages(self, prompt: str):
        self.conversations.add(role = "user", content = prompt)
        return self.conversations.openai_conversations
    
    @property
    def openai_base(self):
        if self.model in ["vicuna-13b"]:
            return config.fastchat_api_base
        else:
            return config.openai_api_base

    def call(self, prompt: str, temperature: float, max_len: int = 1024) -> Iterator[StreamData]:
        openai.api_base = self.openai_base      # set the api base according to the model

        res = openai.ChatCompletion.create(
            model=self.model, messages=self.generateMessages(prompt), temperature=temperature, stream=True
        )
        text = ""
        for chunk in res:
            piece: str = chunk["choices"][0]["delta"].get("content", "") # type: ignore
            text += piece
            data: StreamData = {
                "text": piece if self.return_pieces else text,
                "error_code": 0
            }
            yield data
        self.conversations.add(role = "assistant", content = text)

StreamIterType = Literal["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "vicuna-13b", "gpt-4", "gpt-4-32k"]
def getStreamIter(itype: StreamIterType = "gpt-3.5-turbo") -> StreamIter:
    if itype in ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "vicuna-13b", "gpt-4", "gpt-4-32k"]:
        return OpenAIStreamIter(model=itype)
    else:
        raise ValueError("Unknown interface type: {}".format(itype))
