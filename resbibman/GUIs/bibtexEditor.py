import os
from PyQt5.QtWidgets import QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout
from PyQt5 import QtCore
from .widgets import WidgetBase

from ..confReader import DOC_PATH
from ..core.utils import sssUUID

class BibEditor(WidgetBase):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.connectFuncs()
        
    def initUI(self):
        self.txt_edit = QTextEdit()
        self.txt_edit.setMinimumSize(300,200)
        self.insert_template_button = QPushButton("Use bibtex template")

        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(self.txt_edit)
        self.vlayout.addWidget(self.insert_template_button)
        self.setLayout(self.vlayout)

    def connectFuncs(self):
        self.insert_template_button.clicked.connect(self.insertBibTemplate)

    def insertBibTemplate(self):
        with open(os.path.join(DOC_PATH, "bibTemplate.bib"), "r") as f:
            bib_template = f.read()
        bib_template = bib_template.replace("<Identifier>", sssUUID())
        self.txt_edit.setText(bib_template)

    @property
    def text(self):
        return self.txt_edit.toPlainText()

    @text.setter
    def text(self, txt: str):
        self.txt_edit.setText(txt)

class BibEditorWithOK(BibEditor):
    on_confirmed = QtCore.pyqtSignal(str)
    def initUI(self):
        super().initUI()
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.ok_btn)
        hlayout.addWidget(self.cancel_btn)

        self.vlayout.addLayout(hlayout)

    def connectFuncs(self):
        super().connectFuncs()
        self.ok_btn.clicked.connect(self.confirm)
        self.cancel_btn.clicked.connect(self.cancel)

    def confirm(self):
        self.on_confirmed.emit(self.text)
        self.close()

    def cancel(self):
        self.close()
