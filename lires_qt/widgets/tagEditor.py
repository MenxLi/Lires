from PyQt6 import QtCore
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QDialog

from .tagSelector import TagSelector
from .widgets import RefMixin, QUtilsMixin, WidgetMixin
from lires.core.dataClass import DataTags, TagRule, DataTagT
from lires.core import globalVar as G

class TagEditor(QDialog, RefMixin, QUtilsMixin, WidgetMixin):
    def __init__(self, tag_data: DataTags, tag_total: DataTags, parent = None) -> None:
        super().__init__(parent=parent)
        self.initUI()
        self.tag_selector.initDataModel(tag_data, tag_total)
        self.connectFuncs()
        self.setWindowTitle("Tag editor")
    
    def initUI(self):
        self.tag_selector = TagSelector(self)
        self.line_edit = QLineEdit()
        self.add_btn = QPushButton("Add")
        self.vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.line_edit)
        hbox.addWidget(self.add_btn)
        self.vbox.addWidget(self.tag_selector)
        self.vbox.addWidget(QLabel("(Ctrl+C to input a hovering tag)"))
        self.vbox.addLayout(hbox)
        self.setLayout(self.vbox)
        self.installEventFilter(self)
        self.tag_selector.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
    
    def connectFuncs(self):
        self.add_btn.clicked.connect(self.addCurrTag)
    
    def addCurrTag(self):
        tag = self.line_edit.text()
        # not allow blank tag
        tag_sp = tag.split(TagRule.SEP)
        for t in tag_sp:
            if t.strip() == "":
                self.warnDialog("No blank tag allowed")
                return
        if tag:
            self.tag_selector.addNewSelectedEntry(tag)
            self.line_edit.setText("")
    
    def getSelectedTags(self):
        return self.tag_selector.getSelectedTags()
    
    def eventFilter(self, obj, event: QtCore.QEvent) -> bool:
        if event.type() == QtCore.QEvent.Type.KeyPress:
            if event.key() == QtCore.Qt.Key.Key_C:  # type: ignore
                if self.keyModifiers("Control"):
                    curr_hovering_tag = self.tag_selector.data_model.hovering_tag
                    self.logger.debug(f"Detected input hovering tag: {curr_hovering_tag}")
                    if curr_hovering_tag:
                        self.line_edit.setText(curr_hovering_tag + TagRule.SEP)
                        return True
        return super().eventFilter(obj, event)


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
