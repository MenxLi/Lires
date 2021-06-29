from os import curdir
import warnings
from PyQt5.QtWidgets import QLabel, QPushButton, QTextBrowser, QTextEdit, QVBoxLayout, QWidget, QFrame, QHBoxLayout
from .widgets import WidgetBase, MainWidgetBase
from .fileSelector import FileSelector
from ..backend.fileTools import FileManipulator
from ..backend.bibReader import BibParser
from ..backend.dataClass import DataPoint

class FileInfoGUI(MainWidgetBase):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
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
        self.tEdit = QTextEdit()
        self.save_comment_btn = QPushButton("Save comments")
        self.refresh_btn = QPushButton("Refresh")
        self.open_commets_btn = QPushButton("Open comments")
        self.open_bib_btn = QPushButton("Open bibtex file")
        self.open_folder_btn = QPushButton("Inspect misc directory")

        frame_vbox = QVBoxLayout()

        self.info_frame = QFrame()
        self.info_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        info_frame_vbox = QVBoxLayout()
        info_frame_vbox.addWidget(self.info_lbl)
        self.info_frame.setLayout(info_frame_vbox)

        self.comment_frame = QFrame()
        comment_frame_vbox = QVBoxLayout()
        comment_frame_vbox.addWidget(self.comment_lbl, 0)
        comment_frame_vbox.addWidget(self.tEdit,1)
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
        self.getSelectPanel().selection_changed.connect(self.loadInfo)
        self.getSelectPanel().selection_changed.connect(self.loadComments)
        self.open_folder_btn.clicked.connect(self.openMiscDir)
        self.open_bib_btn.clicked.connect(self.openBib)
        self.open_commets_btn.clicked.connect(self.openComments)
        self.save_comment_btn.clicked.connect(self.saveComments)

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
    
    def loadInfo(self, data: DataPoint):
        self.curr_data = data
        bib = data.bib
        info_txt = \
        "\u27AA {title}\n\u27AA {year}\n\u27AA {authors}\n".format(title = bib["title"], year = bib["year"], authors = " \u2726 ".join(bib["authors"]))
        if "journal"  in bib:
            info_txt = info_txt + "\u27AA {journal}".format(journal = bib["journal"][0])
        self.info_lbl.setText(info_txt)
    
    def openMiscDir(self):
        self.curr_data.fm.openMiscDir()
    
    def openComments(self):
        self.curr_data.fm.openComments()
    
    def openBib(self):
        self.curr_data.fm.openBib()
    
    def saveComments(self):
        comment = self.tEdit.toPlainText()
        self.curr_data.fm.writeComments(comment)

    def loadComments(self, data: DataPoint):
        comment = data.fm.readComments()
        self.tEdit.setText(comment)
    
    def refresh(self):
        pass
