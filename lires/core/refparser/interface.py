from __future__ import annotations
import sys
from abc import ABC, abstractmethod
from typing import Union, Optional
# if sys.version_info.minor >= 11:
#     from typing import TypedDict, NotReqired
# else:
from typing_extensions import NotRequired, TypedDict  # for Python <3.11 with (Not)Required

from lires.core import LiresError
from lires.utils import randomAlphaNumeric
from pybtex.database import BibliographyData, Entry

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
    number: NotRequired[str]
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
    
    def toBibtex(self, entry: str, key: Optional[str] = None):

        data = self.parseEntry(entry)
        if data['type'].lower() == "journal article":
            doc_type = "article"
        elif data['type'].lower() == "thesis":
            doc_type = "phdthesis"
        else:
            raise LiresError.LiresDocTypeNotSupportedError("Not supported document type {}".format(data['type']))
        del data["type"]

        if "issue" in data:
            data["number"] = data["issue"]
        if "authors" in data:
            del data["authors"]

        if key is None:
            key = f"{data['year']}_{randomAlphaNumeric(5)}"

        bib_data = BibliographyData({
            key: Entry(doc_type, data)
        })
        return bib_data.to_string("bibtex")
