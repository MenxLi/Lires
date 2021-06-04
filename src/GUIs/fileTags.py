import typing
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QTextBrowser, QVBoxLayout, QWidget, QFrame, QHBoxLayout, QListView
from PyQt5.QtWidgets import QSizePolicy
from PyQt5 import QtCore, QtGui
from .widgets import WidgetBase
from .tagEditor import TagEditorWidget
from .tagSelector import TagSelector
from ..backend.dataClass import DataPoint, DataTags
from ..confReader import conf, saveToConf

DEFAULT_TAGS = conf["default_tags"]
class FileTagGUI(WidgetBase):
    """
    Implement the GUI for file tree
    """
    def __init__(self, parent = None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.frame = QFrame()
        self.frame.setFrameStyle(QFrame.StyledPanel)
        vbox = QVBoxLayout()
        vbox.addWidget(self.frame)
        self.setLayout(vbox)
        vbox0 = QVBoxLayout()
        self.frame.setLayout(vbox0)

        self.tagselector_frame = QFrame()
        vbox1 = QVBoxLayout()
        self.tagselector_frame.setLayout(vbox1)
        self.tag_label = QLabel("Tags: ")
        self.tag_selector = TagSelector()
        self.clear_selection_btn = QPushButton("Clear selection")
        vbox1.addWidget(self.tag_label)
        vbox1.addWidget(self.tag_selector, 1)
        vbox1.addWidget(self.clear_selection_btn, 0)

        self.filetagselector_frame = QFrame()
        vbox2 = QVBoxLayout()
        self.filetagselector_frame.setLayout(vbox2)
        self.tag_label2 = QLabel("Tags for this file:")
        self.file_tag_label = QLabel("<File tags>")
        self.edit_tag_btn = QPushButton("Edit tags")
        vbox2.addWidget(self.tag_label2)
        vbox2.addWidget(self.file_tag_label)
        vbox2.addWidget(self.edit_tag_btn)

        vbox0.addWidget(self.tagselector_frame, 5)
        vbox0.addWidget(self.filetagselector_frame, 0)


class FileTag(FileTagGUI):
    """
    Implement the functions for file tree
    """
    tag_changed = QtCore.pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)
    
    def initTags(self, tag_total: DataTags):
        tag_data = DataTags([])
        for t in DEFAULT_TAGS:
            if t in tag_total:
                tag_data.add(t)
        self.tag_selector.constructDataModel(tag_data, tag_total)
        saveToConf(default_tags = tag_data.toOrderedList())
    
    def connectFuncs(self):
        self.edit_tag_btn.clicked.connect(self.openTagEditor)
        self.clear_selection_btn.clicked.connect(self.clearSelection)
        self.tag_selector.tag_view.clicked.connect(self.onTagSelectionChanged)
        self.parent.file_selector.selection_changed.connect(self.updateTagLabel)
    
    def openTagEditor(self):
        curr_tags = self._getTagFromCurrSelection()
        if curr_tags is None: return False
        total_tags = self.tag_selector.getTotalTags()
        self.tag_editor = TagEditorWidget(curr_tags, total_tags)
        self.tag_editor.tag_accepted.connect(self.acceptNewTags)
        self.tag_editor.show()
    
    def acceptNewTags(self, new_tags: DataTags):
        uuid = self.parent.getCurrentSelection().uuid
        self.parent.db[uuid].changeTags(new_tags)
        for i in self.parent.file_selector.data_model.datalist:
            if i.uuid == uuid:
                i.reload()
        self.initTags(self.parent.getTotalTags())
    
    def saveCurrentTagsAsDefault(self):
        curr_tags = self.tag_selector.getSelectedTags()
        saveToConf(default_tags = curr_tags.toOrderedList())
        global DEFAULT_TAGS
        DEFAULT_TAGS = list(curr_tags)
    
    def clearSelection(self):
        self.tag_selector.tag_model.setAllStatusToFalse()
        self.onTagSelectionChanged()
    
    def onTagSelectionChanged(self):
        self.saveCurrentTagsAsDefault()
        self.parent.file_selector.loadValidData(self.tag_selector.getSelectedTags())
    
    def updateTagLabel(self, data: DataPoint):
        if isinstance(data, DataPoint):
            self.file_tag_label.setText(data.tags.toStr())
    
    def _getTagFromCurrSelection(self) -> DataTags:
        data = self.parent.getCurrentSelection()
        if isinstance(data, DataPoint):
            return data.tags
        else: return None


