from typing import Any, List, Optional, Literal, TypeAlias, get_args
from dataclasses import dataclass

# FileTypeT = Literal['.pdf', '.html']     # should be one of the accepted extensions at config.py
FileTypeT: TypeAlias = Literal['', '.pdf', '.html']

SortByT = Literal[ 'title', 'year', 'time_import', 'time_modify', 'last_read' ]
def validate_sort_type(sort_type: str | SortByT, error_class = ValueError) -> SortByT:
    """
    Validate the sort type.
    May raise error_class if the sort type is invalid.
    """
    if sort_type not in get_args(SortByT):
        raise error_class(f"Invalid sort type: {sort_type}")
    return sort_type    # type: ignore

@dataclass
class DataPointSummary():
    doc_type: str
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
            "doc_type": self.doc_type,
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