from __future__ import annotations
import sys
from abc import ABC, abstractmethod
from typing import Union
if sys.version_info.minor >= 11:
    from typing import TypedDict, NotReqired
else:
    from typing_extensions import NotRequired, TypedDict  # for Python <3.11 with (Not)Required

class RefDict(TypedDict):
    type: str
    title: str
    author: str
    year: Union[int,str]

    journal: NotRequired[str]
    authors: NotRequired[list[str]]
    pages: NotRequired[str]
    doi: NotRequired[str]
    volume: NotRequired[str]
    issue: NotRequired[str]
    abstract: NotRequired[str]
    publisher: NotRequired[str]
    keywords: NotRequired[str]
    editor: NotRequired[str]
    label: NotRequired[str]
    secondary_title: NotRequired[str]
    place_published: NotRequired[str]



class ParserBase(ABC):
    def __init__(self) -> None:
        ...
    
    @abstractmethod
    def checkFormat(self, entry: str) -> bool:
        ...
    
    @abstractmethod
    def parseEntry(self, entry: str) -> dict:
        ...