from __future__ import annotations
import os
from typing import TYPE_CHECKING, Optional, TypedDict
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineDownloadRequest, QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView

from PyQt6.QtWidgets import QHBoxLayout, QSplitter

from .widgets import MainWidgetBase
from .fileInfo import FileInfo
from ..core.dataClass import DataPoint
from ..core.htmlTools import unpackHtmlTmp
from ..confReader import getConf

if TYPE_CHECKING:
    from .mainWindow import MainWindow

class DocumentReaderStatusT(TypedDict):
    doc_uid: Optional[str]
    splitter_size_initialized: bool

class CustomWebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        # Prevent error messages from being printed to the console
        if level == QWebEnginePage.JavaScriptConsoleMessageLevel.WarningMessageLevel or level == QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel:
            return True
        return super().javaScriptConsoleMessage(level, message, lineNumber, sourceID)

class DocumentReader(MainWidgetBase):
    def __init__(self, parent: MainWindow) -> None:
        super().__init__(parent)
        parent.passRefTo(self)
        self.initUI()
        self._status: DocumentReaderStatusT = {
            "doc_uid": None,
            "splitter_size_initialized": False
        }
        self.dp: Optional[DataPoint] = None

    def initUI(self):
        self.webview = QWebEngineView(self)
        self.webview.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        self.webview.settings().setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)
        self.webview.setPage(CustomWebEnginePage())     # Somehow not working ??
        self.info_panel = FileInfo(self, less_content = True)
        self.passRefTo(self.info_panel)
        self.info_panel.connectFuncs(load_on_sel_change=False)

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
        self.logger.debug(f"Loading {uid} to DocumentReader")
        dp = self.database[uid]
        self.info_panel.load(dp)
        self.dp = dp

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
        if dp.fm.file_p.endswith(".hpack"):
            self._loadHpack(dp.fm.file_p)
            self._status["doc_uid"] = uid
            return True
        return False

    def _loadPDF(self, fpath: str):
        assert fpath.endswith(".pdf")
        viewer_path = getConf()["pdfjs_viewer_path"]
        if not os.path.exists(viewer_path):
            self.warnDialog("Pdf.js viewer not installed", 
                "Download and place it in: {}".format(viewer_path))
            return
        viewer_url = QUrl.fromLocalFile(viewer_path)
        file_url = QUrl.fromLocalFile(fpath)
        qurl = QUrl.fromUserInput("%s?file=%s"%(viewer_url.toString(),file_url.toString()))
        self.logger.debug("Loading url: {}".format(qurl))
        self.webview.load(qurl)
        self.webview.page().profile().downloadRequested.connect(self._on_downloadPDF)
    
    def _loadHpack(self, fpath: str):
        assert fpath.endswith(".hpack")
        unpacked = unpackHtmlTmp(fpath)
        file_url = "file://"+unpacked
        self.webview.setUrl(QUrl(file_url))
        self.webview.page().profile().downloadRequested.connect(lambda _: ...)

    def _on_downloadPDF(self, download_req: QWebEngineDownloadRequest):
        assert self.dp      # type assertion
        self.logger.debug("Downloading {}:{}".format(self.dp.uuid, self.dp))
        def on_stateChange(state: QWebEngineDownloadRequest.DownloadState):
            if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
                self.statusBarInfo("Saved!", time = 3)
            if state == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted \
                or state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled:
                self.logger.error(f"Download state: {state}")
                self.warnDialog("Failed", "file not saved, check log.")
        assert self.dp is not None
        assert self.dp.fm.file_p is not None
        assert self.dp.fm.file_p.endswith(".pdf")
        dir_path, fname = os.path.split(self.dp.fm.file_p)
        self.logger.debug(f"set download path to: {self.dp.fm.file_p}")
        download_req.setDownloadDirectory(dir_path)
        download_req.setDownloadFileName(fname)
        download_req.stateChanged.connect(on_stateChange)
        download_req.accept()
