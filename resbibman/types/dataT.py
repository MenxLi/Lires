from typing import TypedDict, Any, List

class DataPointSummary(TypedDict):
    has_file: bool
    file_status: str
    file_type: str
    year: Any
    title: str
    author: str
    authors: List[str]
    tags: List[str]
    uuid: str
    url: str
    time_added: float
    time_modified: float
    bibtex: str
    doc_size: float # in M.
    base_name: str  # for directory name

    note_linecount: int