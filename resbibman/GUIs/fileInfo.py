import os, shutil, uuid, time, threading, string
from typing import Union, Literal
import warnings
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QLabel, QPushButton, QTabWidget, QTextEdit, QVBoxLayout, QFrame, QHBoxLayout, QLineEdit
from .widgets import MainWidgetBase
from ..confReader import ICON_PATH, getConfV
from ..core.fileTools import FileManipulator
from ..core.bibReader import BibParser
from ..core.dataClass import DataPoint
from ..core.pdfTools import getPDFCoverAsQPixelmap
from ..core.utils import HTML_TEMPLATE_RAW

from PyQt5.QtWebEngineWidgets import QWebEngineView
import markdown
from .mdHighlighter import MarkdownSyntaxHighlighter


class FileInfoGUI(MainWidgetBase):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
        self.setAcceptDrops(True)
        self.show()

    def initUI(self):
        self.frame = QFrame()
        self.frame.setFrameStyle(QFrame.StyledPanel)
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
        self.comment_lbl = QLabel("Comments: ")
        self.comment_save_indicate_lbl = QLabel("")
        self.save_comment_btn = QPushButton("Save")
        self.refresh_btn = QPushButton("Refresh")
        self.open_commets_btn = QPushButton("Comments")
        self.open_bib_btn = QPushButton("Open bibtex file")
        self.open_folder_btn = QPushButton("Misc")

        self.mdTab = QTabWidget()
        self.tEdit = MarkdownEdit()
        self.weburl_edit = QLineEdit()
        self.highlighter = MarkdownSyntaxHighlighter(self.tEdit)
        self.mdBrowser = QWebEngineView()
        self.mdTab.addTab(self.tEdit, "Note.md")
        self.mdTab.addTab(self.mdBrowser, "Note.html")

        frame_vbox = QVBoxLayout()

        self.info_frame = QFrame()
        self.info_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        info_frame_hbox = QHBoxLayout()
        info_frame_hbox.addWidget(self.info_lbl)
        info_frame_hbox.addWidget(self.cover_label)
        self.info_frame.setLayout(info_frame_hbox)

        self.comment_frame = QFrame()
        comment_frame_vbox = QVBoxLayout()
        comment_frame_vbox.addWidget(self.comment_lbl, 0)
        comment_frame_vbox.addWidget(self.mdTab,1)
        comment_frame_hbox = QHBoxLayout()
        if not getConfV("auto_save_comments"):
            comment_frame_hbox.addWidget(self.save_comment_btn,1)
        comment_frame_hbox.addWidget(self.comment_save_indicate_lbl,0)
        comment_frame_vbox.addLayout(comment_frame_hbox, 0)
        self.comment_frame.setLayout(comment_frame_vbox)

        self.weburl_frame = QFrame()
        weburl_hbox = QHBoxLayout()
        weburl_hbox.addWidget(QLabel("URL/DOI: "))
        weburl_hbox.addWidget(self.weburl_edit)
        self.weburl_frame.setLayout(weburl_hbox)

        self.btn_frame = QFrame()
        btn_frame_vbox = QVBoxLayout()
        btn_frame_hbox = QHBoxLayout()
        btn_frame_hbox.addWidget(self.open_commets_btn)
        btn_frame_hbox.addWidget(self.open_folder_btn)
        #  btn_frame_hbox.addWidget(self.open_bib_btn)
        btn_frame_vbox.addLayout(btn_frame_hbox)
        #  btn_frame_vbox.addWidget(self.open_folder_btn)
        self.btn_frame.setLayout(btn_frame_vbox)

        frame_vbox.addWidget(self.info_frame, 3)
        frame_vbox.addWidget(self.comment_frame, 7)
        frame_vbox.addWidget(self.weburl_frame, 0)
        frame_vbox.addWidget(self.btn_frame, 0)
        self.frame.setLayout(frame_vbox)

class FileInfo(FileInfoGUI):
    """
    Implement the functions for file info
    """
    COMMENT_SAVE_TOLERANCE_INTERVAL = 2
    COMMENT_HTML_TEMPLATE = string.Template(HTML_TEMPLATE_RAW)

    def __init__(self, parent = None, **kwargs):
        super().__init__(parent)
        self.curr_data = None
        self.tEdit.setParent(self)
        for k, v in kwargs:
            setattr(self, k, v)
        
        self.__cache = {
            "save_comment_time_prev" : 0,
            "save_comment_in_pending": False,
        }
    
    def connectFuncs(self):
        self.getSelectPanel().selection_changed.connect(self.load)
        self.open_folder_btn.clicked.connect(self.openMiscDir)
        self.open_bib_btn.clicked.connect(self.openBib)
        self.open_commets_btn.clicked.connect(self.openComments)
        self.save_comment_btn.clicked.connect(self._saveComments)
        self.refresh_btn.clicked.connect(self.refresh)
        self.mdTab.currentChanged.connect(self.changeTab)
        self.tEdit.textChanged.connect(self.onCommentChange)
        self.weburl_edit.textChanged.connect(self.saveWebURL)
    
    def clearPanel(self):
        self.curr_data = None
        self.info_lbl.setText("File info")
        self.tEdit.setText("")
        self.setCommentSaveStatusLbl("none")
        self.__updateCover(None)

    def loadDir(self, dir_path: str):
        """
        *****Deprecated, can be called while serve as standalone widget"""
        fm = FileManipulator(dir_path)
        if not fm.screen():
            warnings.warn("Data seems to be broken, please check the data externally")
            return False
        data = DataPoint(fm)
        bib = fm.bib
        bib = BibParser()(bib)[0]
        info_txt = "【Title】\n>> {title}\n【Year】\n>> {year}\n【Authors】\n>> {authors}\n\
            ".format(title = bib["title"], year = bib["year"], authors = " | ".join(bib["authors"]))
        self.info_lbl.setText(info_txt)
    
    def load(self, data: DataPoint):
        self.logger.debug("Load data point")
        self.curr_data = data
        self.info_lbl.setText(data.stringInfo())
        comment = self.curr_data.fm.readComments()
        self.tEdit.setText(comment)
        # To avoid status change when clicking on a new data point
        self.setCommentSaveStatusLbl("saved")
        self.weburl_edit.setText(data.fm.getWebUrl())
        self.__updateCover(data)
        self.__renderMarkdown()
    
    def changeTab(self, index):
        self.logger.debug("On tab change")
        if index == 1:
            self._saveComments()
            self.__renderMarkdown()

    def openMiscDir(self):
        if not self.curr_data is None:
            self.curr_data.fm.openMiscDir()
    
    def openComments(self):
        if not self.curr_data is None:
            self.curr_data.fm.openComments()
    
    def openBib(self):
        if not self.curr_data is None:
            self.curr_data.fm.openBib()
    
    def onCommentChange(self):
        self.setCommentSaveStatusLbl("changed")
        # Asynchronous saving
        if getConfV("auto_save_comments"):
            t = threading.Thread(target=self.__thread_saveComments, args=())
            t.start()
    
    def saveWebURL(self):
        if self.curr_data is None:
            self.warnDialog("No file selected.")
            return
        prev_url = self.curr_data.fm.getWebUrl()
        weburl = self.weburl_edit.text()
        if weburl != prev_url:
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
        saved_comments = data.fm.readComments()
        curr_comments = self.tEdit.toPlainText()
        if saved_comments == curr_comments:
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

    def __thread_saveComments(self):
        def _save_comments_thread():
            if self._saveComments():
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

    def _saveComments(self) -> bool:
        if not self.curr_data is None:
            comment = self.tEdit.toPlainText()
            self.curr_data.fm.writeComments(comment)
            self.setCommentSaveStatusLbl("saved")
            return True
        else:
            self.comment_save_indicate_lbl.setText("")
            return False
    
    def __renderMarkdown(self):
        comment = self.tEdit.toPlainText()
        if comment == "":
            return
        if self.curr_data is None:
            # shouldn't happen
            return
        misc_f = self.curr_data.fm.folder_p
        misc_f = misc_f.replace(os.sep, "/")
        comment = comment.replace("./misc", misc_f)

        comment_html = markdown.markdown(comment)
        comment_html = self.COMMENT_HTML_TEMPLATE.substitute(content = comment_html)

        self.mdBrowser.setHtml(comment_html, baseUrl=QtCore.QUrl.fromLocalFile("/"))

    def __updateCover(self, data: Union[DataPoint,None]):
        self.cover_label.setScaledContents(False)
        if data is None:
            cover = QtGui.QPixmap(os.path.join(ICON_PATH, "error-48px.png"))
        elif data.file_path is None:
            # No file or not PDF file
            if data.fm.getWebUrl() == "":
                cover = QtGui.QPixmap(os.path.join(ICON_PATH, "error-48px.png"))
            else:
                # if has url thus clickable
                cover = QtGui.QPixmap(os.path.join(ICON_PATH, "outline_cloud_black_48dp.png"))
        elif data.file_path.endswith(".pdf"):
            cover = getPDFCoverAsQPixelmap(data.fm.file_p)
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
        new_cover = cover.scaled(int(new_width), int(new_height), aspectRatioMode=QtCore.Qt.KeepAspectRatio, transformMode=QtCore.Qt.SmoothTransformation)##调整图片尺寸
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
        if source.hasImage():
            # Add img
            fname = f"{uuid.uuid4()}.png"
            fpath = os.path.join(self._parent.curr_data.fm.folder_p, fname)
            source.imageData().save(fpath)
            line = f"![](./misc/{fname})"
            # line = f"<img src=\"./misc/{fname}\" alt=\"drawing\" width=\"100%\"/>"
            self.insertPlainText(line)
            self._parent._saveComments()
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
                    shutil.copy2(fpath, self._parent.curr_data.fm.folder_p)
                    # line = f"<img src=\"./misc/{fname}\" alt=\"drawing\" width=\"100%\"/>"
                    line = f"![](./misc/{fname})"
                    self.insertPlainText(line)
                    self._parent._saveComments()
                    return
        else:
            super().insertFromMimeData(source)
