from __future__ import annotations
from typing import Literal, Optional, Tuple, TypedDict, List, Union

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
    proxies: _ConfProxyT