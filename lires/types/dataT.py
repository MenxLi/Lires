from typing import Any, List, Optional, Literal, TypeAlias
from dataclasses import dataclass

# FileTypeT = Literal['.pdf', '.html']     # should be one of the accepted extensions at config.py
FileTypeT: TypeAlias = Literal['', '.pdf', '.html']

@dataclass
class DataPointSummary():
    has_file: bool
    file_type: FileTypeT
    year: Any
    title: str
    author: str
    authors: List[str]
    publication: Optional[str]
    tags: List[str]
    uuid: str
    url: str
    time_added: float
    time_modified: float
    bibtex: str
    doc_size: float # in M.
    note_linecount: int
    has_abstract: bool

    def json(self):
        return {
            "has_file": self.has_file,
            "file_type": self.file_type,
            "year": self.year,
            "title": self.title,
            "author": self.author,
            "authors": self.authors,
            "publication": self.publication,
            "tags": self.tags,
            "uuid": self.uuid,
            "url": self.url,
            "time_added": self.time_added,
            "time_modified": self.time_modified,
            "bibtex": self.bibtex,
            "doc_size": self.doc_size,
            "note_linecount": self.note_linecount,
            "has_abstract": self.has_abstract
        }