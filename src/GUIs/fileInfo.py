import warnings
from PyQt5.QtWidgets import QLabel, QPushButton, QTextBrowser, QTextEdit, QVBoxLayout, QWidget, QFrame, QHBoxLayout
from ..fileUtils.fileTools import FileManipulator
from ..bibUtils.bibReader import BibParser

class FileInfoGUI(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
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
        self.open_folder_btn = QPushButton("Inspect externally")

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
    def __init__(self, parent = None):
        super().__init__(parent)
        # test
        # self.loadDir("/home/monsoon/Documents/Code/ResBibManager/Database/2020-Li^_Mengxun-Automated_integration_of_facial_a")

    def loadDir(self, dir_path: str):
        fm = FileManipulator(dir_path)
        if not fm.screen():
            warnings.warn("Data seems to be broken, please check the data externally")
            return False
        bib = fm.readBib()
        bib = BibParser()(bib)[0]
        info_txt = "【Title】\n>> {title}\n【Year】\n>> {year}\n【Authors】\n>> {authors}\n\
            ".format(title = bib["title"], year = bib["year"], authors = " | ".join(bib["authors"]))
        self.info_lbl.setText(info_txt)
        
