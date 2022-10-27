from typing import Tuple, TypedDict, List

class _ConfServerPresetT(TypedDict):
    host: str
    port: str
    access_key: str

class _ConfFontSizeT(TypedDict):
    data: Tuple[str, int]
    tag: Tuple[str, int]

class _ConfGUIStatusT(TypedDict):
    show_toolbar: bool

class ResbibmanConfT(TypedDict):
    """
    Refer to rbm-resetconf 
    for the generation of default configuration file
    """
    accepted_extensions: List[str]
    database: str
    # Server settings
    server_preset: List[_ConfServerPresetT]
    host: str
    port: str
    access_key: str

    # Tag settings
    default_tags: List[str]
    table_headers: List[str]

    # GUI settings
    sort_method: str
    sort_reverse: bool

    font_sizes: _ConfFontSizeT
    stylesheet: str
    auto_save_comments: bool
    gui_status: _ConfGUIStatusT

