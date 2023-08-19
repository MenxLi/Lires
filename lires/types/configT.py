from __future__ import annotations
from typing import Literal, Optional, Tuple, TypedDict, List, Union

class _ConfServerPresetT(TypedDict):
    host: str
    port: str
    access_key: str

class _ConfFontSizeT(TypedDict):
    data: Tuple[str, int]
    tag: Tuple[str, int]

class _ConfGUIStatusT(TypedDict):
    show_toolbar: bool
    tag_uncollapsed: List[str]

class _ConfProxyT(TypedDict):
    proxy_config: _ProxyT
    enable_requests: bool
    enable_qt: bool

class _ProxyT(TypedDict):
    proxy_type: Optional[Literal["socks5", "http", ""]]
    host: str
    port: Union[str, int]

class LiresConfT(TypedDict):
    """
    Refer to lrs-resetconf 
    for the generation of default configuration file
    """
    """CORE SETTINGS"""
    accepted_extensions: List[str]
    database: str
    # Server settings
    host: str
    port: str
    access_key: str

    # PDFjs viewer for pdf render in qwebengine and webui
    # the path is suppose to be the viewer.html
    pdfjs_viewer_path: str

    """GUI SETTINGS"""
    server_preset: List[_ConfServerPresetT]
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

    proxies: _ConfProxyT
