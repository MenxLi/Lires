"""
The quary dialog for bibtex input
"""

from PyQt5.QtWidgets import QWidget, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFrame
from PyQt5.QtWidgets import QSizePolicy
from PyQt5 import QtCore
from ..bibUtils.bibReader import BibParser
from ..fileUtils.nameTools import fileGenerator

class BibQuary(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()
        self.show()
        self.setWindowTitle("Input bibtex info")
    
    def initUI(self):
        # self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.resize(420, 300)
        self.bib_edit = QTextEdit()
        self.bib_edit.setMinimumSize(300,200)
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Canel")

        vlayout = QVBoxLayout()
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.ok_button)
        hlayout.addWidget(self.cancel_button)

        vlayout.addWidget(self.bib_edit)
        vlayout.addLayout(hlayout)

        self.setLayout(vlayout)

        self.ok_button.clicked.connect(self.confirm)
        self.cancel_button.clicked.connect(self.close)
    
    def confirm(self):
        parser = BibParser(mode = "single")
        txt = self.bib_edit.toPlainText()
        bib = parser(txt)[0]
        fileGenerator(title = bib.title,
        year = bib.year,
        authors = bib.authors
        )

