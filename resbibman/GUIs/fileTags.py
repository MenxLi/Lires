from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QFrame
from PyQt6 import QtCore
from .widgets import  MainWidgetBase
from .tagEditor import TagEditorWidget
from .tagSelector import TagSelector
from ..core.dataClass import DataPoint, DataTags
from ..types.configT import _ConfFontSizeT
from ..confReader import getConf, saveToConf

class FileTagGUI(MainWidgetBase):
    """
    Implement the GUI for file tree
    """
    def __init__(self, parent = None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.frame = QFrame()
        self.frame.setFrameStyle(QFrame.Shape.StyledPanel)
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
        self.file_tag_label.setWordWrap(True)
        self.edit_tag_btn = QPushButton("Edit tags")
        vbox2.addWidget(self.tag_label2)
        vbox2.addWidget(self.file_tag_label)
        vbox2.addWidget(self.edit_tag_btn)

        vbox0.addWidget(self.tagselector_frame, 5)
        vbox0.addWidget(self.filetagselector_frame, 0)

    def applyFontConfig(self, font_config: _ConfFontSizeT):
        font = QFont(*font_config["tag"])
        # self.tag_selector.ccl.setFont(font)
    
    def offlineStatus(self, status: bool):
        super().offlineStatus(status)
        disable_wids = [
            self.edit_tag_btn
        ]
        for wid in disable_wids:
            wid.setEnabled(status)


class FileTag(FileTagGUI):
    """
    Implement the functions for file tree
    """
    tag_changed = QtCore.pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)
    
    def initTags(self, tag_total: DataTags):
        tag_data = DataTags([])
        for t in getConf()["default_tags"]:
            if t in tag_total:
                tag_data.add(t)
        self.tag_selector.constructDataModel(tag_data, tag_total)
        saveToConf(default_tags = tag_data.toOrderedList())
    
    def connectFuncs(self):
        self.edit_tag_btn.clicked.connect(self.openTagEditor)
        self.clear_selection_btn.clicked.connect(self.clearSelection)
        self.tag_selector.data_model.on_selection_change.connect(lambda _: self.onTagSelectionChanged())
        self.getSelectPanel().selection_changed.connect(self.updateTagLabel)

        self.tag_selector.setMainPanel(self.getMainPanel())
    
    def openTagEditor(self):
        curr_tags = self._getTagFromCurrSelection()
        if curr_tags is None: return False
        total_tags = self.tag_selector.getTotalTags()
        self.tag_editor = TagEditorWidget(curr_tags, total_tags)
        self.tag_editor.setMainPanel(self.getMainPanel())
        self.tag_editor.tag_accepted.connect(self.acceptNewTags)
        self.tag_editor.show()
    
    def acceptNewTags(self, new_tags: DataTags):
        data = self.getSelectPanel().getCurrentSelection()
        if data is None:
            return
        uuid = data.uuid
        self.getMainPanel().db[uuid].changeTags(new_tags)
        for i in self.getSelectPanel().data_model.datalist:
            if i.uuid == uuid:
                i.reload()
        self.initTags(self.database.total_tags)
    
    def saveCurrentTagsAsDefault(self):
        curr_tags = self.tag_selector.getSelectedTags()
        saveToConf(default_tags = curr_tags.toOrderedList())
    
    def clearSelection(self):
        self.tag_selector.data_model.setAllStatusToFalse()
        self.onTagSelectionChanged()
    
    def onTagSelectionChanged(self):
        self.saveCurrentTagsAsDefault()
        curr_sel_tags = self.tag_selector.getSelectedTags()
        self.logger.debug("onTagSelectionChanged - {}".format(curr_sel_tags))
        self.getSelectPanel().loadValidData(curr_sel_tags)
        self.getInfoPanel().clearPanel()
        curr_data = self.getSelectPanel().getCurrentSelection()
        if curr_data is not None:
            self.getInfoPanel().load(curr_data)
            self.updateTagLabel(curr_data)
    
    def updateTagLabel(self, data: DataPoint):
        if isinstance(data, DataPoint):
            self.file_tag_label.setText(data.tags.toStr())
            self.offlineStatus(data.is_local)
    
    def _getTagFromCurrSelection(self) -> DataTags:
        data = self.getSelectPanel().getCurrentSelection()
        if isinstance(data, DataPoint):
            return data.tags
        else: return None


