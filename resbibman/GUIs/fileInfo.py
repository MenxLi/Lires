from os import curdir
import warnings
from PyQt5 import QtGui
from PyQt5.QtWidgets import QLabel, QPushButton, QTabWidget, QTextBrowser, QTextEdit, QVBoxLayout, QWidget, QFrame, QHBoxLayout
from .widgets import WidgetBase, MainWidgetBase
from .fileSelector import FileSelector
from ..backend.fileTools import FileManipulator
from ..backend.bibReader import BibParser
from ..backend.dataClass import DataPoint

from PyQt5.QtWebEngineWidgets import QWebEngineView
import markdown

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
        self.comment_lbl = QLabel("Comments: ")
        self.save_comment_btn = QPushButton("Save comments")
        self.refresh_btn = QPushButton("Refresh")
        self.open_commets_btn = QPushButton("Open comments")
        self.open_bib_btn = QPushButton("Open bibtex file")
        self.open_folder_btn = QPushButton("Inspect misc directory")

        self.mdTab = QTabWidget()
        self.tEdit = QTextEdit()
        self.mdBrowser = QWebEngineView()
        self.mdTab.addTab(self.tEdit, "Note.txt")
        self.mdTab.addTab(self.mdBrowser, "Note.md")

        frame_vbox = QVBoxLayout()

        self.info_frame = QFrame()
        self.info_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        info_frame_vbox = QVBoxLayout()
        info_frame_vbox.addWidget(self.info_lbl)
        self.info_frame.setLayout(info_frame_vbox)

        self.comment_frame = QFrame()
        comment_frame_vbox = QVBoxLayout()
        comment_frame_vbox.addWidget(self.comment_lbl, 0)
        # comment_frame_vbox.addWidget(self.tEdit,1)
        comment_frame_vbox.addWidget(self.mdTab,1)
        self.comment_frame.setLayout(comment_frame_vbox)

        self.btn_frame = QFrame()
        btn_frame_vbox = QVBoxLayout()
        btn_frame_hbox = QHBoxLayout()
        btn_frame_hbox.addWidget(self.save_comment_btn)
        btn_frame_hbox.addWidget(self.refresh_btn)
        btn_frame_vbox.addLayout(btn_frame_hbox)
        btn_frame_vbox.addWidget(self.open_commets_btn)
        btn_frame_vbox.addWidget(self.open_bib_btn)
        btn_frame_vbox.addWidget(self.open_folder_btn)
        self.btn_frame.setLayout(btn_frame_vbox)

        frame_vbox.addWidget(self.info_frame, 1)
        frame_vbox.addWidget(self.comment_frame, 3)
        frame_vbox.addWidget(self.btn_frame, 1)
        self.frame.setLayout(frame_vbox)

class FileInfo(FileInfoGUI):
    """
    Implement the functions for file info
    """
    def __init__(self, parent = None, **kwargs):
        super().__init__(parent)
        self.curr_data = None
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
    
    def clearPanel(self):
        self.curr_data = None
        self.info_lbl.setText("File info")
        self.tEdit.setText("")

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
        comment_html = markdown.markdown(comment)
        self.mdBrowser.setHtml(comment_html)
    
    def changeTab(self, index):
        if index == 1:
            self.saveComments()
            comment = self.tEdit.toPlainText()
            comment_html = markdown.markdown(comment)
            self.mdBrowser.setHtml(comment_html)

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
            self.getSelectPanel().addFileToCurrentSelection(fpath)
        return super().dropEvent(a0)
