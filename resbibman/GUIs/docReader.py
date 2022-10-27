from __future__ import annotations
import os
from typing import TYPE_CHECKING, Optional, TypedDict
import webbrowser
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView

from PyQt6.QtWidgets import QHBoxLayout, QSplitter

from .widgets import MainWidgetBase
from .fileInfo import FileInfo

if TYPE_CHECKING:
    from .mainWindow import MainWindow

class DocumentReaderStatusT(TypedDict):
    doc_uid: Optional[str]
    splitter_size_initialized: bool

class DocumentReader(MainWidgetBase):
    def __init__(self, parent: MainWindow) -> None:
        super().__init__(parent)
        parent.passRefTo(self)
        self.initUI()
        self._status: DocumentReaderStatusT = {
            "doc_uid": None,
            "splitter_size_initialized": False
        }

    def initUI(self):
        self.webview = QWebEngineView(self)
        self.webview.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        self.webview.settings().setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)
        self.info_panel = FileInfo(self)
        self.passRefTo(self.info_panel)
        self.info_panel.connectFuncs()

        self.splitter = QSplitter()
        self.splitter.addWidget(self.webview)
        self.splitter.addWidget(self.info_panel)

        layout = QHBoxLayout()
        layout.addWidget(self.splitter)
        self.setLayout(layout)

    @property
    def doc_uid(self) -> str:
        assert self._status["doc_uid"]
        return self._status["doc_uid"]

    def maybeInitSpliterSize(self):
        # The curr_width can only be correctly obtained when the window is rendered
        if self._status["splitter_size_initialized"]:
            return
        curr_width = self.frameGeometry().width()
        info_panel_w_init = self.getInfoPanel().frameGeometry().width()
        self.splitter.setSizes([curr_width - info_panel_w_init, info_panel_w_init])
        self._status["splitter_size_initialized"] = True


    def loadDataByUid(self, uid: str) -> bool:
        """
        return if successfully opened in webview
        """
        dp = self.database[uid]
        self.info_panel.load(dp)

        if not dp.is_local or not dp.fm.file_p:
            url = dp.fm.getWebUrl()
            if not url:
                # No file and no url
                return False
            elif os.path.exists(url):
                # has url but redirect to other files in the local computer
                return False
            else:
                self.webview.setUrl(QUrl(url))
                self._status["doc_uid"] = uid
                return True

        if dp.fm.file_p.endswith(".pdf"):
            self._loadPDF(dp.fm.file_p)
            self._status["doc_uid"] = uid
            return True
        return False

    def _loadPDF(self, fpath: str):
        assert fpath.endswith(".pdf")
        file_url = "file://"+fpath
        self.webview.setUrl(QUrl(file_url))
