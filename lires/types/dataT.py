from typing import TypedDict, Any, List, Optional

class DataPointSummary(TypedDict):
    has_file: bool
    file_type: str
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