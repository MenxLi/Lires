import os, shutil, uuid, time, threading
from typing import Optional, Union, Literal
import warnings
import requests
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QLabel, QPushButton, QTabWidget, QTextEdit, QVBoxLayout, QFrame, QHBoxLayout, QLineEdit, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QKeySequence, QShortcut
from .widgets import MainWidgetBase
from ..confReader import ICON_PATH, getConfV, TMP_COVER, getServerURL
from ..core.dataClass import DataPoint
from ..core.serverConn import ServerConn
from ..core.pdfTools import getPDFCoverAsQPixelmap
from ..core.encryptClient import generateHexHash

from .mdHighlighter import MarkdownSyntaxHighlighter


class FileInfoGUI(MainWidgetBase):
    TEDIT_SYNC_PROPMT = "Sync to edit"

    # tab widget index
    TAB_INDEX_MDEDIT = 0
    TAB_INDEX_MDBROWSER= 1
    TAB_INDEX_DISCUSSBROWSER= 2

    def __init__(self, parent = None, less_content = False):
        super().__init__(parent)
        self.initUI(less_content)
        self.setAcceptDrops(True)
        self.show()

    def initUI(self, less_content: bool):
        self.frame = QFrame()
        self.frame.setFrameStyle(QFrame.Shape.StyledPanel)
        hbox = QHBoxLayout()
        hbox.addWidget(self.frame)
        self.setLayout(hbox)

        self.info_lbl = QLabel("File info")
        self.info_lbl.setWordWrap(True)
        self.cover_label = QLabel()
        self.cover_label.setScaledContents(True)
        # self.cover_label.setMaximumHeight(300)
        self.cover_label.setMaximumWidth(150)
        self.cover_label.setMinimumSize(100, 150)
        #  self.comment_lbl = QLabel("Comments: ")
        self.comment_save_indicate_lbl = QLabel("")
        self.save_comment_btn = QPushButton("Save")
        self.refresh_btn = QPushButton("Refresh")
        self.open_folder_btn = QPushButton("Misc")
        self.open_external_btn = QPushButton("Open")
        self.weburl_edit = QLineEdit()

        self.md_edit_wid = QWidget()
        self.tEdit = MarkdownEdit()
        _vlayout = QVBoxLayout()
        _vlayout.addWidget(self.tEdit)
        _hlayout = QHBoxLayout()
        if not getConfV("auto_save_comments"):
            _save_h_layout = QHBoxLayout()
            _save_h_layout.addWidget(self.save_comment_btn, 1)
            _save_h_layout.addWidget(self.comment_save_indicate_lbl, 0)
            _vlayout.addLayout(_save_h_layout)

        _hlayout.addWidget(self.open_folder_btn, 1)
        _hlayout.addWidget(self.open_external_btn, 1)
        _vlayout.addLayout(_hlayout)
        self.md_edit_wid.setLayout(_vlayout)

        self.highlighter = MarkdownSyntaxHighlighter(self.tEdit)
        self.mdBrowser = QWebEngineView()

        self.discuss_wid = QWidget()
        self.discussBrowser = QWebEngineView()
        self.btn_post_discuss = QPushButton("Post")
        self.discuss_line = QLineEdit()
        self.discuss_name = QLineEdit()
        _vlayout = QVBoxLayout()
        _hlayout = QHBoxLayout()
        _hlayout.addWidget(self.discuss_line, 5)
        _hlayout.addWidget(self.discuss_name, 2)
        _hlayout.addWidget(self.btn_post_discuss, 0)
        _vlayout.addWidget(self.discussBrowser)
        _vlayout.addLayout(_hlayout)
        self.discuss_wid.setLayout(_vlayout)

        self.tab_wid = QTabWidget()
        self.tab_wid.addTab(self.md_edit_wid, "Note.md")
        self.tab_wid.addTab(self.mdBrowser, "Note.html")
        self.tab_wid.addTab(self.discuss_wid, "Discussion")

        frame_vbox = QVBoxLayout()

        self.info_frame = QFrame()
        # self.info_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shape.Sunken)
        #  self.info_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        info_frame_hbox = QHBoxLayout()
        info_frame_hbox.addWidget(self.info_lbl)
        if not less_content:
            info_frame_hbox.addWidget(self.cover_label)
        self.info_frame.setLayout(info_frame_hbox)

        self.comment_frame = QFrame()
        comment_frame_vbox = QVBoxLayout()
        #  comment_frame_vbox.addWidget(self.comment_lbl, 0)
        comment_frame_vbox.addWidget(self.tab_wid,1)
        self.comment_frame.setLayout(comment_frame_vbox)

        self.weburl_frame = QFrame()
        weburl_hbox = QHBoxLayout()
        weburl_hbox.addWidget(QLabel("URL/DOI: "))
        weburl_hbox.addWidget(self.weburl_edit)
        self.weburl_frame.setLayout(weburl_hbox)

        # self.btn_frame = QFrame()
        # btn_frame_vbox = QVBoxLayout()
        # btn_frame_hbox = QHBoxLayout()
        # btn_frame_hbox.addWidget(self.open_folder_btn)
        # btn_frame_vbox.addLayout(btn_frame_hbox)
        # self.btn_frame.setLayout(btn_frame_vbox)

        frame_vbox.addWidget(self.info_frame, 2)
        frame_vbox.addWidget(self.comment_frame, 7)
        if not less_content:
            frame_vbox.addWidget(self.weburl_frame, 0)
            # frame_vbox.addWidget(self.btn_frame, 0)
        self.frame.setLayout(frame_vbox)

        comment_frame_vbox.setContentsMargins(0,0,0,0)
        # self.btn_frame.setContentsMargins(0,0,0,0)
        frame_vbox.setContentsMargins(0,0,0,0)

class FileInfo(FileInfoGUI):
    """
    Implement the functions for file info
    """
    COMMENT_SAVE_TOLERANCE_INTERVAL = 2
    #  COMMENT_HTML_TEMPLATE = string.Template(HTML_TEMPLATE_RAW)

    def __init__(self, parent = None, less_content = False):
        super().__init__(parent, less_content)
        self.curr_data = None
        self.tEdit.setParent(self)
        
        self.__cache = {
            "save_comment_time_prev" : 0,
            "save_comment_in_pending": False,
        }
        self.shortcut_save_comment = QShortcut(QKeySequence("ctrl+s"), self)

        self.__curr_data_uid: Optional[str] = None

    @property
    def is_offline(self):
        return self.getMainPanel().database.offline
    
    # curr_data must be implemented as a reference to the current database
    # (Here through uuid)
    # because we may re-construct the database with reload
    # If the curr_data is implemented as a ordinary property
    # it maybe un-linked from the database when re-construct database
    @property
    def curr_data(self) -> Optional[DataPoint]:
        if self.__curr_data_uid is not None:
            try:
                return self.database[self.__curr_data_uid]
            except Exception as e:
                self.logger.error("Un-caught error when getting curr_data: {}".format(e))
                return None
        else:
            return None

    @curr_data.setter
    def curr_data(self, dp: Optional[DataPoint]):
        if dp:
            self.__curr_data_uid = dp.uuid
        else:
            self.__curr_data_uid = None
    
    def connectFuncs(self, load_on_sel_change: bool = True):
        """
        - load_on_sel_change: whether to load new datapoint on file selector's selection change
        """
        if load_on_sel_change:
            self.getSelectPanel().selection_changed.connect(self.load)
        self.open_folder_btn.clicked.connect(self.openMiscDir)
        self.save_comment_btn.clicked.connect(self._saveCommentSlot)
        self.open_external_btn.clicked.connect(lambda: self.getMainPanel().openDocExternal(self.curr_data) if self.curr_data else None)
        self.refresh_btn.clicked.connect(self.refresh)
        self.tab_wid.currentChanged.connect(self.changeTab)
        self.tEdit.textChanged.connect(self.onCommentChange)
        self.weburl_edit.textChanged.connect(self.saveWebURL)
        self.shortcut_save_comment.activated.connect(self._saveCommentSlot)
        self.btn_post_discuss.clicked.connect(self.postDiscussion)
    
    def offlineStatus(self, status: bool = True):
        super().offlineStatus(status)
        if not status:
            self.tEdit.setText(self.TEDIT_SYNC_PROPMT)
        else:
            # Load comments when sync download
            if self.curr_data is not None:
                comment = self.curr_data.fm.readComments()
                self.tEdit.setText(comment)
            # To avoid status change when clicking on a new data point
            self.setCommentSaveStatusLbl("saved")
            self.__updateCover(self.curr_data)
            self.__renderMarkdown()

        self.tEdit.setEnabled(status)
        self.weburl_edit.setEnabled(status)
        #  self.mdBrowser.setEnabled(status)
        self.open_folder_btn.setEnabled(status)
        self.refresh_btn.setEnabled(status)
        #  self.mdTab.setEnabled(status)
    
    def clearPanel(self):
        self.logger.debug("Clear info panel")
        self.curr_data = None
        self.info_lbl.setText("File info")
        self.tEdit.setText("")
        self.weburl_edit.setText("")
        self.setCommentSaveStatusLbl("none")
        self.__updateCover(None)

    def load(self, data: DataPoint):
        self.logger.debug("Load data point to info panel: {}".format(data.uuid))
        self.curr_data = data
        self.info_lbl.setText(data.stringInfo())
        self.weburl_edit.setText(data.fm.getWebUrl())
        self.__updateCover(data)
        if self.tab_wid.currentIndex() == self.TAB_INDEX_MDBROWSER:
            self.__renderMarkdown()
        elif self.tab_wid.currentIndex() == self.TAB_INDEX_DISCUSSBROWSER:
            self.__updateDiscussion()

        if data.is_local:
            comment = self.curr_data.fm.readComments()
            self.offlineStatus(True)
            self.tEdit.setText(comment)
            # To avoid status change when clicking on a new data point
            self.setCommentSaveStatusLbl("saved")
        else:
            self.offlineStatus(False)
            self.setCommentSaveStatusLbl("none")

    def reload(self):
        if self.curr_data:
            self.load(self.curr_data)
    
    def changeTab(self, index):
        self.logger.debug("On tab change")
        if index == self.TAB_INDEX_MDBROWSER:
            # to the html render
            self.saveComments()
            self.__renderMarkdown()
        if index == self.TAB_INDEX_DISCUSSBROWSER and not self.is_offline:
            self.__updateDiscussion()

    def openMiscDir(self):
        if not self.curr_data is None:
            self.curr_data.fm.openMiscDir()
    
    def onCommentChange(self):
        # get previous comment
        if self.curr_data is None:
            return
        prev_comment = self.curr_data.fm.readComments()
        if prev_comment == self.tEdit.toPlainText():
            # has not changed
            # check this to avoid unnecessary saving if auto save is on
            return 

        self.setCommentSaveStatusLbl("changed")
        # Asynchronous saving
        if getConfV("auto_save_comments"):
            # synchronous saving for now...
            self.saveComments()

            ## Maybe adopt lazy saving in the future...
            # t = threading.Thread(target=self.__thread_saveComments, args=())
            # t.start()
    
    def saveWebURL(self):
        if self.curr_data is None:
            #  self.warnDialog("No file selected.")
            self.logger.info("No file selected")
            return
        weburl = self.weburl_edit.text()
        self.curr_data.fm.setWebUrl(weburl)
    
    def refresh(self):
        if not self.curr_data is None:
            self.curr_data.reload()
            self.load(self.curr_data)
    
    def dragEnterEvent(self, a0: QtGui.QDragEnterEvent) -> None:
        if a0.mimeData().hasUrls():
            a0.accept()
        else:
            a0.ignore()
        return super().dragEnterEvent(a0)
    
    def dropEvent(self, a0: QtGui.QDropEvent) -> None:
        files = [u.toLocalFile() for u in a0.mimeData().urls()]
        if len(files) > 1:
            warnings.warn("Supposed to add ONE file only.")
        else:
            fpath = files[0]
            # Add new entry
            for extension in getConfV("accepted_extensions"):
                if fpath.endswith(extension):
                    self.getSelectPanel().addFileToCurrentSelection(fpath)
                    return super().dropEvent(a0)

    def queryCommentSaveStatus(self) -> Literal["saved", "changed", "none"]:
        data = self.curr_data
        if data is None:
            return "none"
        # saved_comments = data.fm.readComments()
        # curr_comments = self.tEdit.toPlainText()
        # if saved_comments == curr_comments:
            # return "saved"
        # else:
            # return "changed"
        if self.comment_save_indicate_lbl.text() == "":
            return "none"
        elif self.comment_save_indicate_lbl.text() == "saved.":
            return "saved"
        else:
            return "changed"

    def setCommentSaveStatusLbl(self, status: Literal["saved", "changed", "none"]):
        """Set status indicator QLabel"""
        comment_save_indicate_lbl = self.comment_save_indicate_lbl
        if status == "none":
            comment_save_indicate_lbl.setText("")
        elif status == "saved":
            comment_save_indicate_lbl.setText("saved.")
            #  comment_save_indicate_lbl.setStyleSheet("QLabel { background-color : green; color : blue; }")
            comment_save_indicate_lbl.setStyleSheet("QLabel { color : #00aa33; }")
        elif status == "changed":
            comment_save_indicate_lbl.setText("changed.")
            comment_save_indicate_lbl.setStyleSheet("QLabel { background-color : #cc0000; color: white;}")

    def postDiscussion(self):
        name = self.discuss_name.text()
        content = self.discuss_line.text()
        if not name:
            self.warnDialog("Enter your name.")
            return
        if not content:
            self.warnDialog("Can't post without content.")
            return

        if self.curr_data is None:
            # shouldn't happen, for type checking purposes
            return
        uid = self.curr_data.uuid
        success = ServerConn().postDiscussion(uid = uid, name = name, content = content)
        if success:
            self.__updateDiscussion()

    def __thread_saveComments(self):
        def _save_comments_thread():
            if self.saveComments():
                self.__cache["save_comment_in_pending"] = False
                self.__cache["save_comment_time_prev"] = time.time()
                self.logger.debug("Comment saved")
            else:
                self.logger.debug("Comment save failed")
        time_after_prev_save = time.time() - self.__cache["save_comment_time_prev"] 
        if time_after_prev_save > self.COMMENT_SAVE_TOLERANCE_INTERVAL:
            # Save instantly after saving interval.
            _save_comments_thread()
        elif self.__cache["save_comment_in_pending"]:
            # During time.sleep
            self.logger.debug("Comment will be save later, saving pending")
        else:
            self.__cache["save_comment_in_pending"] = True
            sleeptime = self.COMMENT_SAVE_TOLERANCE_INTERVAL - time_after_prev_save
            self.logger.debug("Comment will be save later (after {}s), saving triggered".format(sleeptime))
            time.sleep(sleeptime)
            _save_comments_thread()

    def _saveCommentSlot(self):     # type checking purpose, have to return None
        self.saveComments()
    def saveComments(self) -> bool:
        if self.curr_data is None:
            self.setCommentSaveStatusLbl("none")
            return False
        if not self.curr_data.is_local:
            self.setCommentSaveStatusLbl("none")
            return False
        comment = self.tEdit.toPlainText()
        if comment == self.TEDIT_SYNC_PROPMT:
            # Don't save this...
            return False
        if self.queryCommentSaveStatus() != "changed":
            # no repeated save
            self.logger.debug("Skip unnecessary comment save.")
            return False
        self.curr_data.fm.writeComments(comment)
        self.setCommentSaveStatusLbl("saved")
        return True
    
    def __renderMarkdown(self):
        if self.curr_data is None:
            # shouldn't happen, for type checking purposes
            return

        if self.curr_data.is_local:
            comment = self.tEdit.toPlainText()
            if comment == "":
                return
            comment_html = self.curr_data.htmlComment()
            self.mdBrowser.setHtml(comment_html, baseUrl=QtCore.QUrl.fromLocalFile("/"))
        else:
            # set online url
            uid = self.curr_data.uuid
            md_url = ServerConn().getNoteURL(uid)
            self.logger.debug("requesting remote comment html: {}".format(md_url))
            self.mdBrowser.setUrl(QtCore.QUrl.fromUserInput(md_url))

    def __updateDiscussion(self):
        if self.curr_data is None:
            # shouldn't happen, for type checking purposes
            return
        uid = self.curr_data.uuid
        discuss_url = ServerConn().getDisscussionURL(uid)
        
        hex_key = generateHexHash(getConfV("access_key"))
        req = requests.get(discuss_url, cookies={"RBM_ENC_KEY": hex_key})
        self.discussBrowser.setHtml(req.text)
        self.discuss_line.setText("")

    def __updateCover(self, data: Union[DataPoint,None]):
        self.cover_label.setScaledContents(False)
        if data is None:
            cover = QtGui.QPixmap(os.path.join(ICON_PATH, "error-48px.png"))
        elif not data.is_local:
            # Unsynchronized
            cover = QtGui.QPixmap(os.path.join(ICON_PATH, "outline_cloud_black_48dp.png"))
        elif data.file_path is None:
            # No file
            if data.fm.getWebUrl() == "":
                cover = QtGui.QPixmap(os.path.join(ICON_PATH, "error-48px.png"))
            else:
                # if has url thus clickable
                cover = QtGui.QPixmap(os.path.join(ICON_PATH, "cloud_black_48dp.svg"))
        elif data.file_path.endswith(".pdf"):
            _tmp_cover = os.path.join(TMP_COVER, data.uuid + ".png")
            if os.path.exists(_tmp_cover):
                cover = QtGui.QPixmap(_tmp_cover)
            else:
                assert data.fm.file_p   # type assertion
                cover = getPDFCoverAsQPixelmap(data.fm.file_p)
                cover.save(_tmp_cover)
                self.logger.debug("Created temp cover file at: {}".format(_tmp_cover))
        else:
            cover = QtGui.QPixmap(os.path.join(ICON_PATH, "description_black_48dp.svg"))

        # https://blog.csdn.net/L114678/article/details/121457242
        width = cover.width()
        height = cover.height()
        if width / self.cover_label.width() >= height / self.cover_label.height(): ##比较图片宽度与label宽度之比和图片高度与label高度之比
            ratio = width / self.cover_label.width()
        else:
            ratio = height / self.cover_label.height()
        new_width = width / ratio  ##定义新图片的宽和高
        new_height = height / ratio 
        new_cover = cover.scaled(int(new_width), int(new_height), \
                                 aspectRatioMode= QtCore.Qt.AspectRatioMode.KeepAspectRatio, \
                                 transformMode=QtCore.Qt.TransformationMode.SmoothTransformation)##调整图片尺寸
        self.cover_label.setPixmap(new_cover)

class MarkdownEdit(QTextEdit):
    def setParent(self, parent: FileInfo):
        self._parent = parent

    def dragEnterEvent(self, a0: QtGui.QDragEnterEvent) -> None:
        if a0.mimeData().hasUrls():
            a0.accept()
        else:
            a0.ignore()
        return super().dragEnterEvent(a0)

    def dropEvent(self, a0: QtGui.QDropEvent) -> None:
        return super().dropEvent(a0)
    
    def canInsertFromMimeData(self, source: QtCore.QMimeData) -> bool:
        if source.hasImage():
            return True
        else:
            return super().canInsertFromMimeData(source)
    
    def insertHtml(self, text: str) -> None:
        """Not insert HTML!!!"""
        return super().insertPlainText(text)
    
    def insertFromMimeData(self, source: QtCore.QMimeData) -> None:
        # https://pyside.github.io/docs/pyside/PySide/QtGui/QTextEdit.html#PySide.QtGui.PySide.QtGui.QTextEdit.insertFromMimeData
        if self._parent.curr_data is None:
            self._parent.warnDialog("Failed", "No data selected")
            return
        if source.hasImage():
            # Add img
            fname = f"{uuid.uuid4()}.png"
            fpath = os.path.join(self._parent.curr_data.fm.getMiscDir(create=True), fname)
            source.imageData().save(fpath)
            line = f"![](./misc/{fname})"
            # line = f"<img src=\"./misc/{fname}\" alt=\"drawing\" width=\"100%\"/>"
            self.insertPlainText(line)
            self._parent.saveComments()
        elif source.hasUrls():
            # file
            files = [u.toLocalFile() for u in source.urls()]

            if len(files) > 1 or len(files) == 0:
                warnings.warn("Supposed to add ONE file only.")
                return super().insertFromMimeData(source)

            fpath = files[0]
            if self._parent.curr_data is None:
                return

            # Add img to comment
            for extension in [".jpg", ".png"]:
                if fpath.endswith(extension):
                    fname = os.path.basename(fpath)
                    shutil.copy2(fpath, self._parent.curr_data.fm.getMiscDir(create=True))
                    # line = f"<img src=\"./misc/{fname}\" alt=\"drawing\" width=\"100%\"/>"
                    line = f"![](./misc/{fname})"
                    self.insertPlainText(line)
                    self._parent.saveComments()
                    return
        elif source.hasText():
            # Paste plain text (without format)
            self.insertPlainText(source.text())
        else:
            super().insertFromMimeData(source)
