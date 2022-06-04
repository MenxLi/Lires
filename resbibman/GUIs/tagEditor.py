from PyQt6 import QtCore
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton

from .tagSelector import TagSelector
from .widgets import MainWidgetBase
from ..core.dataClass import DataTags

class TagEditor(MainWidgetBase):
    def __init__(self, tag_data: DataTags, tag_total: DataTags, parent = None) -> None:
        super().__init__(parent=parent)
        self.initUI()
        self.tag_selector.constructDataModel(tag_data, tag_total)
        self.connectFuncs()
        self.setWindowTitle("Tag editor")
    
    def initUI(self):
        self.tag_selector = TagSelector()
        self.line_edit = QLineEdit()
        self.add_btn = QPushButton("Add")
        self.vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.line_edit)
        hbox.addWidget(self.add_btn)
        self.vbox.addWidget(self.tag_selector)
        self.vbox.addLayout(hbox)
        self.setLayout(self.vbox)
    
    def connectFuncs(self):
        self.add_btn.clicked.connect(self.addCurrTag)
    
    def addCurrTag(self):
        tag = self.line_edit.text()
        if tag:
            self.tag_selector.addNewSelectedEntry(tag)
            self.tag_selector.tag_model.layoutChanged.emit()
            self.line_edit.setText("")
    
    def getSelectedTags(self):
        return self.tag_selector.getSelectedTags()


class TagEditorWidget(TagEditor):
    tag_accepted = QtCore.pyqtSignal(DataTags)
    def __init__(self, tag_data: DataTags, tag_total: DataTags, parent = None) -> None:
        super().__init__(tag_data, tag_total, parent=parent)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.close)

    def initUI(self):
        super().initUI()
        self.ok_btn = QPushButton("Accept")
        self.cancel_btn = QPushButton("Cancel")
        hbox = QHBoxLayout()
        hbox.addWidget(self.ok_btn)
        hbox.addWidget(self.cancel_btn)
        self.vbox.addLayout(hbox)

    def accept(self):
        self.tag_accepted.emit(self.getSelectedTags())
        self.close()
