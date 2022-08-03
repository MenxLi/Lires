import os
from typing import Dict
from datetime import date
from PyQt6.QtWidgets import QButtonGroup, QDialog, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QWidget, QRadioButton, QComboBox
from PyQt6 import QtCore
from .widgets import WidgetBase

from ..confReader import DOC_PATH, BIB_TEMPLATE_PATH
from ..core.utils import sssUUID
from ..core.bibReader import BibConverter

class TemplateChoice(WidgetBase, QDialog):
    template_selected = QtCore.pyqtSignal(str)
    def __init__(self, parent = None):
        super().__init__(parent)
        self.template_name_path: Dict[str, str] = {}
        for template in os.listdir(BIB_TEMPLATE_PATH):
            if template.endswith(".bib"):
                t_name = template.split(".")[0]
                self.template_name_path[t_name] = os.path.join(BIB_TEMPLATE_PATH, template)
        self.initUI()

    def initUI(self):
        vlayout = QVBoxLayout()
        self.buttons = QButtonGroup(self)
        for name, t_path in self.template_name_path.items():
            btn = QRadioButton(name)
            if btn.text() == "article":
                btn.setChecked(True)
            vlayout.addWidget(btn)
            self.buttons.addButton(btn)

        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.confirm)

        vlayout.addWidget(self.ok_btn)
        self.setLayout(vlayout)

    def confirm(self):
        curr_btn = self.buttons.checkedButton()
        if curr_btn is None:
            return
        name = curr_btn.text()
        t_path = self.template_name_path[name]
        with open(t_path, "r") as f:
            bib_template = f.read()
        bib_template = bib_template.replace("<Identifier>", sssUUID())
        bib_template = bib_template.replace("<today>", str(date.today()))
        self.template_selected.emit(bib_template)
        self.close()
        return

class PlainTextInput(QDialog, WidgetBase):
    on_ok = QtCore.pyqtSignal(str)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Input")
        self.txt_edit = QTextEdit()
        self.txt_edit.setMinimumSize(300,200)
        self.ok_btn = QPushButton("OK")
        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(self.txt_edit)
        self.vlayout.addWidget(self.ok_btn)
        self.ok_btn.clicked.connect(self.ok)
        self.setLayout(self.vlayout)

    def ok(self):
        out = self.txt_edit.toPlainText()
        self.on_ok.emit(out)
        self.close()

class BibEditor(QDialog, WidgetBase):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.connectFuncs()
        
    def initUI(self):
        self.txt_edit = QTextEdit()
        self.txt_edit.setMinimumSize(300,200)
        self.insert_template_button = QPushButton("Use bibtex template")
        self.from_other_format_btn = QPushButton("Convert from")
        self.format_cb = QComboBox(self)
        self.format_cb.addItem("nbib")

        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(self.txt_edit)
        self.vlayout.addWidget(self.insert_template_button)

        self._hlayout = QHBoxLayout()
        self._hlayout.addWidget(self.from_other_format_btn)
        self._hlayout.addWidget(self.format_cb)
        self.vlayout.addLayout(self._hlayout)
        self.setLayout(self.vlayout)

    def connectFuncs(self):
        self.insert_template_button.clicked.connect(self.insertBibTemplate)
        self.from_other_format_btn.clicked.connect(self.insertFromOtherFormat)

    def insertBibTemplate(self):
        self.logger.debug("Open Bibtex TemplateChoice")
        self.choices = TemplateChoice()
        self.choices.template_selected.connect(lambda t: self.txt_edit.setText(t))
        self.choices.show()

    def insertFromOtherFormat(self):
        txt_query = PlainTextInput(self)
        txt_query.on_ok.connect(lambda t: 
                                self.txt_edit.setText(
                                    self._convert(t, self.format_cb.currentText())
                                ))
        txt_query.show()

    def _convert(self, txt, bib_type: str) -> str:
        converter = BibConverter()
        if bib_type == "nbib":
            return converter.fromNBib(txt)
        else:
            return ""

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
