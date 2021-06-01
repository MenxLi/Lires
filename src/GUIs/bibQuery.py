"""
The quary dialog for bibtex input
"""
import os
from PyQt5.QtWidgets import QLabel, QWidget, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFrame
from PyQt5.QtWidgets import QSizePolicy
from PyQt5 import QtCore
from ..bibUtils.bibReader import BibParser
from ..fileUtils.fileTools import FileGenerator, FileManipulator
from ..confReader import conf

DATA_PATH = conf["database"]
class BibQueryGUI(QWidget):
    def __init__(self, parent):
        """
        file_path: path to the original paper
        """
        super().__init__()
        self.parent = parent
        self.initUI()
    
    def initUI(self):
        # self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setWindowTitle("Input bibtex info")
        self.resize(420, 300)
        self.filename_lbl = QLabel()
        self.bib_edit = QTextEdit()
        self.bib_edit.setMinimumSize(300,200)
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Canel")

        vlayout = QVBoxLayout()
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.ok_button)
        hlayout.addWidget(self.cancel_button)

        vlayout.addWidget(self.filename_lbl, 0)
        vlayout.addWidget(self.bib_edit, 1)
        vlayout.addLayout(hlayout)

        self.setLayout(vlayout)


class BibQuery(BibQueryGUI):
    def __init__(self, parent, file_path: str):
        super().__init__(parent)
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
        fg = FileGenerator(
            file_path = self.file_path,
            title = bib["title"],
            year = bib["year"],
            authors = bib["authors"]
        )
        if not fg.generateDefaultFiles(data_dir=DATA_PATH):
            return 
        dst_dir = fg.dst_dir
        print(dst_dir)
        fm = FileManipulator(dst_dir)
        fm.screen()
        fm.writeBib(bib_txt)

