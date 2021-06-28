"""
The quary dialog for bibtex input
"""
import os
from PyQt5.QtWidgets import QLabel, QWidget, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFrame
from PyQt5.QtWidgets import QSizePolicy
from PyQt5 import QtCore

from ..backend.dataClass import DataTags
from .tagEditor import TagEditor
from ..backend.bibReader import BibParser
from ..backend.fileTools import FileGenerator, FileManipulator
from ..confReader import getConf

class BibQueryGUI(QWidget):
    def __init__(self, parent, tag_data: DataTags, tag_total: DataTags):
        """
        file_path: path to the original paper
        """
        super().__init__()
        self.parent = parent
        self.init_tag_data = tag_data
        self.init_tag_total = tag_total
        self.initUI()
    
    def initUI(self):
        # self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setWindowTitle("Input bibtex and tag info")
        self.resize(420, 600)
        self.filename_lbl = QLabel()
        self.bib_edit = QTextEdit()
        self.bib_edit.setMinimumSize(300,200)
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Canel")

        self.tag_prompt_lbl = QLabel("Edit tags for this file:")
        self.tag_edit = TagEditor(tag_data= self.init_tag_data, tag_total=self.init_tag_total)
        self.tag_edit.setMinimumSize(300, 200)

        main_hox = QHBoxLayout()
        vlayout = QVBoxLayout()
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.ok_button)
        hlayout.addWidget(self.cancel_button)
        vlayout.addWidget(self.filename_lbl, 0)
        vlayout.addWidget(self.bib_edit, 1)
        vlayout.addLayout(hlayout)

        vlayout_R = QVBoxLayout()
        vlayout_R.addWidget(self.tag_prompt_lbl)
        vlayout_R.addWidget(self.tag_edit)

        main_hox.addLayout(vlayout)
        main_hox.addLayout(vlayout_R)

        self.setLayout(main_hox)


class BibQuery(BibQueryGUI):
    file_added = QtCore.pyqtSignal(str)
    def __init__(self, parent, file_path: str, tag_data: DataTags, tag_total:DataTags):
        super().__init__(parent, tag_data=tag_data, tag_total=tag_total)
        self.file_path = file_path

        file_name = os.path.split(self.file_path)[-1]
        self.filename_lbl.setText(file_name)

        self.connectMethods()
    
    def connectMethods(self):
        self.ok_button.clicked.connect(self.confirm)
        self.cancel_button.clicked.connect(self.close)

    def confirm(self):
        parser = BibParser(mode = "single")
        bib_txt = self.bib_edit.toPlainText()
        bib = parser(bib_txt)[0]
        tag_list = self.tag_edit.getSelectedTags().toOrderedList()
        fg = FileGenerator(
            file_path = self.file_path,
            title = bib["title"],
            year = bib["year"],
            authors = bib["authors"]
        )
        if not fg.generateDefaultFiles(data_dir=getConf["database"]):
            return 
        dst_dir = fg.dst_dir
        fm = FileManipulator(dst_dir)
        fm.screen()
        fm.writeBib(bib_txt)
        fm.writeTags(tag_list)
        self.file_added.emit(dst_dir)
        self.close()

