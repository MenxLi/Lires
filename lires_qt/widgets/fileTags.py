from typing import Optional
from PyQt6.QtGui import QFont, QPainter
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QFrame, QWidget
from PyQt6 import QtCore

from QFlowLayout import FlowLayout

from .widgets import  MainWidgetBase, RefWidgetBase
from .tagEditor import TagEditorWidget
from .tagSelector import TagSelector
from lires.core.dataClass import DataPoint, DataTags, DataTagT
from lires_qt.config import _ConfFontSizeT, getGUIConf, saveToGUIConf
# from lires.confReader import getConf, saveToConf

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
        self.tag_selector = TagSelector(self)
        self.clear_selection_btn = QPushButton("Clear selection")
        vbox1.addWidget(self.tag_label)
        vbox1.addWidget(self.tag_selector, 1)
        vbox1.addWidget(self.clear_selection_btn, 0)
        vbox1.setContentsMargins(0,0,0,0)

        self.filetagselector_frame = QFrame()
        vbox2 = QVBoxLayout()
        self.filetagselector_frame.setLayout(vbox2)

        self.file_tag_wid = FileTagWidget(self)
        self.edit_tag_btn = QPushButton("Edit tags")
        vbox2.addWidget(self.file_tag_wid)
        vbox2.addWidget(self.edit_tag_btn)
        vbox2.setContentsMargins(0,0,0,0)

        vbox0.addWidget(self.tagselector_frame, 5)
        vbox0.addWidget(self.filetagselector_frame, 0)

    def applyFontConfig(self, font_config: _ConfFontSizeT):
        font = QFont(*font_config["tag"])
        self.tag_selector.ccl.setFont(font)
        self.file_tag_wid.applyFontConfig(font_config)
    
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
    
    def initTags(self, tag_total: DataTags, mandatory_tags: Optional[DataTagT] = None):
        tag_data = DataTags([])
        for t in getGUIConf()["default_tags"]:
            if t in tag_total:
                tag_data.add(t)
        self.tag_selector.initDataModel(tag_data, tag_total, mandatory_tags=mandatory_tags)
        saveToGUIConf(default_tags = tag_data.toOrderedList())

    @property
    def selected_tags(self):
        return self.tag_selector.getSelectedTags()
    
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
        def on_done(success: bool):
            if success:
                curr_data = self.getSelectPanel().getCurrentSelection()
                if curr_data:
                    self.updateTagLabel(curr_data)
        self.getSelectPanel().loadValidData_async(on_done)
    
    def saveCurrentTagsAsDefault(self):
        curr_tags = self.tag_selector.getSelectedTags()
        saveToGUIConf(default_tags = curr_tags.toOrderedList())
    
    def clearSelection(self):
        self.tag_selector.data_model.setAllStatusToFalse()
        self.onTagSelectionChanged()
    
    def onTagSelectionChanged(self):
        self.saveCurrentTagsAsDefault()
        curr_sel_tags = self.tag_selector.getSelectedTags()
        self.logger.debug("onTagSelectionChanged - {}".format(curr_sel_tags))
        def on_done(success):
            if success:
                self.getInfoPanel().clearPanel()
                curr_data = self.getSelectPanel().getCurrentSelection()
                self.updateTagLabel(curr_data)
                if curr_data is not None:
                    self.getInfoPanel().load(curr_data)
                else:
                    self.getInfoPanel().clearPanel()
        self.getSelectPanel().loadValidData_async(on_done)
    
    def updateTagLabel(self, data: Optional[DataPoint]):
        if isinstance(data, DataPoint):
            # self.file_tag_label.setText(data.tags.toStr())
            self.file_tag_wid.loadTags(data.tags, self.selected_tags)
            self.offlineStatus(data.is_local)
        else:
            self.file_tag_wid.loadTags(DataTags([]), self.selected_tags)
    
    def _getTagFromCurrSelection(self) -> Optional[DataTags]:
        data = self.getSelectPanel().getCurrentSelection()
        if isinstance(data, DataPoint):
            return data.tags
        else: return None

class Bubble(QLabel):
    def __init__(self, text):
        super(Bubble, self).__init__(text)
        self.word = text
        self._draw_rect = True
        self.setContentsMargins(5, 3, 5, 3)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        if self._draw_rect:
            painter.drawRoundedRect(
                0, 0, self.width() - 1, self.height() - 1, 5, 5)
        super(Bubble, self).paintEvent(event)

    def setStyleSheetBackgroundColor(self, s: str):
        self.setStyleSheet(f"background-color: {s}")

    def setNoRoundRect(self):
        self._draw_rect = False

class FileTagWidget(RefWidgetBase):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = FlowLayout(self)
        self.flayout = layout

    def loadTags(self, curr_data_tags: DataTags, selected_tags: DataTags):
        self.clearTags()
        loaded = []
        SELECTED_BG_COLOR = "rgba(0, 150, 150, 200)"
        SELECTED_INFER_BG_COLOR = "rgba(50, 50, 150, 100)"
        # tag in data
        for tag in curr_data_tags:
            bubble = Bubble(tag)
            loaded.append(tag)
            self.flayout.addWidget(bubble)
            if tag in selected_tags:
                # tag in data is selected
                bubble.setStyleSheetBackgroundColor(SELECTED_BG_COLOR)
            elif tag in selected_tags.withChildsFrom(curr_data_tags):
                # tag in data is a child from current selected tags
                bubble.setStyleSheetBackgroundColor(SELECTED_INFER_BG_COLOR)
            else:
                # tag in data but is not selected
                ...

        # tag not in data
        for sel_tag in selected_tags:
            if not sel_tag in loaded:
                bubble = Bubble(sel_tag)
                bubble.setNoRoundRect()
                if sel_tag in curr_data_tags.withParents():
                    # selected tag is a parent of the tag in data
                    bubble.setStyleSheetBackgroundColor(SELECTED_INFER_BG_COLOR)
                else:
                    # selected tag not shown in current data
                    ...
                self.flayout.addWidget(bubble)
    
    def clearTags(self):
        bubble_count = self.flayout.count()
        for i in range(bubble_count):
            wid = self.flayout.itemAt(i).widget()
            wid.deleteLater()
    
    def applyFontConfig(self, font_config: _ConfFontSizeT):
        bubble_count = self.flayout.count()
        for i in range(bubble_count):
            wid = self.flayout.itemAt(i).widget()
            if isinstance(wid, Bubble):
                ftype, size = font_config["tag"]
                font = QFont(ftype, size)
                wid.setFont(font)