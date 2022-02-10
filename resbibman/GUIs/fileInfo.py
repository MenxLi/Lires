from os import curdir
import os, shutil, uuid
from typing import Union
import warnings
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QLabel, QPushButton, QTabWidget, QTextBrowser, QTextEdit, QVBoxLayout, QWidget, QFrame, QHBoxLayout, QLineEdit
from .widgets import WidgetBase, MainWidgetBase
from .fileSelector import FileSelector
from ..confReader import ICON_PATH, getConfV
from ..backend.fileTools import FileManipulator
from ..backend.bibReader import BibParser
from ..backend.dataClass import DataPoint
from ..backend.pdfTools import getPDFCoverAsQPixelmap

from PyQt5.QtWebEngineWidgets import QWebEngineView
import markdown
from .mdHighlighter import MarkdownSyntaxHighlighter

from ..backend.utils import copy2clip

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
        self.save_comment_btn = QPushButton("Save comments")
        self.refresh_btn = QPushButton("Refresh")
        self.open_commets_btn = QPushButton("Open comments")
        self.open_bib_btn = QPushButton("Open bibtex file")
        self.open_folder_btn = QPushButton("Inspect misc directory")

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
        # comment_frame_vbox.addWidget(self.tEdit,1)
        comment_frame_vbox.addWidget(self.mdTab,1)
        self.comment_frame.setLayout(comment_frame_vbox)

        self.weburl_frame = QFrame()
        weburl_hbox = QHBoxLayout()
        weburl_hbox.addWidget(QLabel("URL/DOI: "))
        weburl_hbox.addWidget(self.weburl_edit)
        self.weburl_frame.setLayout(weburl_hbox)

        self.btn_frame = QFrame()
        btn_frame_vbox = QVBoxLayout()
        # btn_frame_hbox = QHBoxLayout()
        # btn_frame_hbox.addWidget(self.save_comment_btn)
        # btn_frame_hbox.addWidget(self.refresh_btn)
        # btn_frame_vbox.addLayout(btn_frame_hbox)
        btn_frame_vbox.addWidget(self.open_commets_btn)
        btn_frame_vbox.addWidget(self.open_bib_btn)
        btn_frame_vbox.addWidget(self.open_folder_btn)
        self.btn_frame.setLayout(btn_frame_vbox)

        frame_vbox.addWidget(self.info_frame, 3)
        frame_vbox.addWidget(self.comment_frame, 7)
        frame_vbox.addWidget(self.weburl_frame, 1)
        frame_vbox.addWidget(self.btn_frame, 2)
        self.frame.setLayout(frame_vbox)

class FileInfo(FileInfoGUI):
    """
    Implement the functions for file info
    """
    def __init__(self, parent = None, **kwargs):
        super().__init__(parent)
        self.curr_data = None
        self.tEdit.setParent(self)
        for k, v in kwargs:
            setattr(self, k, v)
    
    def connectFuncs(self):
        self.getSelectPanel().selection_changed.connect(self.load)
        self.open_folder_btn.clicked.connect(self.openMiscDir)
        self.open_bib_btn.clicked.connect(self.openBib)
        self.open_commets_btn.clicked.connect(self.openComments)
        self.save_comment_btn.clicked.connect(self.saveComments)
        self.refresh_btn.clicked.connect(self.refresh)
        self.mdTab.currentChanged.connect(self.changeTab)
        self.tEdit.textChanged.connect(self.saveComments)
        self.weburl_edit.textChanged.connect(self.saveWebURL)
    
    def clearPanel(self):
        self.curr_data = None
        self.info_lbl.setText("File info")
        self.tEdit.setText("")
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
        self.curr_data = data
        self.info_lbl.setText(data.stringInfo())
        comment = self.curr_data.fm.readComments()
        self.tEdit.setText(comment)
        self.weburl_edit.setText(data.fm.getWebUrl())
        self.__updateCover(data.fm.file_p)
        self.__renderMarkdown()
    
    def changeTab(self, index):
        if index == 1:
            self.saveComments()
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
    
    def saveComments(self):
        if not self.curr_data is None:
            comment = self.tEdit.toPlainText()
            self.curr_data.fm.writeComments(comment)
    
    def saveWebURL(self):
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

    
    def __renderMarkdown(self):
        comment = self.tEdit.toPlainText()
        # if comment == "":
            # return

        misc_f = self.curr_data.fm.folder_p
        misc_f = misc_f.replace(os.sep, "/")
        comment = comment.replace("./misc", misc_f)

        comment_html = markdown.markdown(comment)
        self.mdBrowser.setHtml(comment_html, baseUrl=QtCore.QUrl.fromLocalFile("/"))
    
    def __updateCover(self, fpath: Union[str,None]):
        if fpath is None or not fpath.endswith(".pdf"):
            self.cover_label.setScaledContents(False)
            cover = QtGui.QPixmap(os.path.join(ICON_PATH, "error-48px.png"))
        else:
            self.cover_label.setScaledContents(False)
            cover = getPDFCoverAsQPixelmap(fpath)
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
                    shutil.copy2(fpath, self._parent.curr_data.fm.folder_p)
                    # line = f"<img src=\"./misc/{fname}\" alt=\"drawing\" width=\"100%\"/>"
                    line = f"![](./misc/{fname})"
                    self.insertPlainText(line)
                    self._parent.saveComments()
                    return
        else:
            super().insertFromMimeData(source)