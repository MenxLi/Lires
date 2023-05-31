
"""Language Model Interface"""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any, TypedDict, Literal
import dataclasses

# check python version
import sys, os
if sys.version_info < (3, 9):
    from typing import Iterator
else:
    from collections.abc import Iterator

try: import openai
except: Warning("openai not installed")

ConvRole = Literal["user", "assistant"]
ConvContent = str
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
    @property
    def openai_conversations(self):
        system = [{"role": "system", "content": self.system}]
        conv = [{"role": c[0], "content": c[1]} for c in self.conversations]
        return system + conv

class StreamData(TypedDict):
    """a class to represent the data returned by the model output stream"""
    text: str
    error_code: int

class StreamIter(ABC):
    """Abstract class for language model interface"""
    temperature = 0.8
    max_response_length = 1024
    conversations: Conversation
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
    
    def generateMessages(self, prompt: str):
        self.conversations.add(role = "user", content = prompt)
        return self.conversations.openai_conversations

    def call(self, prompt: str, temperature: float, max_len: int = 1024) -> Iterator[StreamData]:
        res = openai.ChatCompletion.create(
            model=self.model, messages=self.generateMessages(prompt), temperature=temperature, stream=True
        )
        text = ""
        for chunk in res:
            text += chunk["choices"][0]["delta"].get("content", "") # type: ignore
            data: StreamData = {
                "text": text,
                "error_code": 0
            }
            yield data
        self.conversations.add(role = "assistant", content = text)