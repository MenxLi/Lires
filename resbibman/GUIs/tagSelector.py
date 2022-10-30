from __future__ import annotations
import os
from typing import Optional, Sequence, Union, List, overload, Dict

from PyQt6.QtWidgets import QListView, QHBoxLayout, QInputDialog, QVBoxLayout
from PyQt6.QtGui import QAction, QFont
from PyQt6 import QtCore
from PyQt6 import QtGui

from QCollapsibleCheckList import CollapsibleCheckList, DataItemAbstract

from .widgets import RefWidgetBase
from ._styleUtils import qIconFromSVG_autoBW
from ..confReader import ICON_PATH, getConfV, saveToConf
from ..core.dataClass import DataTags, TagRule

class TagSelector(RefWidgetBase):
    entry_added = QtCore.pyqtSignal(str)

    def __init__(self, tag_data = Optional[DataTags], tag_total = Optional[DataTags]) -> None:
        super().__init__()
        self.initUI()
        if isinstance(tag_data, DataTags) and isinstance(tag_total, DataTags):
            self.constructDataModel(tag_data, tag_total)    

    @property
    def database(self):
        return self.getMainPanel().database
    
    def initUI(self):
        self.ccl = CollapsibleCheckList(
            self,
            hover_highlight_color="rgba(100, 100, 100, 100)",
            click_line_select=True,
            )
        self.data_model = TagDataModel(self, self.ccl)
        layout = QVBoxLayout()
        layout.addWidget(self.ccl)
        self.setLayout(layout)

    # May need renaming later... rename to initDataModel?
    def constructDataModel(self, tag_data: DataTags, tag_total: DataTags):
        """
        Load new data
        """
        self.data_model.initData(tag_data, tag_total)

    def getSelectedTags(self) -> DataTags:
        tags = self.data_model.selected_tags
        return tags

    def getTotalTags(self) -> DataTags:
        return self.data_model.total_tags

    def addNewSelectedEntry(self, tag: str):
        if not self.data_model.addNewData(tag, True, unfold=True):
            self.infoDialog("The tag already exists")


class TagDataModel(QtCore.QObject):
    """
    An interface to hide data communication with CollapsibleCheckList
    Only expose str and DataTags to outside
    """
    class TagDataItem(str, DataItemAbstract):
        def isParentOf(self, child: TagDataModel.TagDataItem) -> bool:
            child_sp = child.split(TagRule.SEP)
            self_sp = self.split(TagRule.SEP)
            if len(self_sp) != len(child_sp)-1:
                return False
            return self_sp == child_sp[:-1]
    
        def toString(self) -> str:
            # return f"{self.split(TagRule.SEP)[-1]}"
            return str(self)

    on_selection_change = QtCore.pyqtSignal(DataTags)    

    def __init__(self, parent: Optional[QtCore.QObject], wid: CollapsibleCheckList):
        super().__init__(parent)
        self.ccl: CollapsibleCheckList[self.TagDataItem] = wid
        self._item_pool: Dict[str, self.TagDataItem] = {}
        self._connectSignal()
    
    def _connectSignal(self):
        self.ccl.onCheckItem.connect(lambda _: self.on_selection_change.emit(self.selected_tags))
        self.ccl.onUnCheckItem.connect(lambda _: self.on_selection_change.emit(self.selected_tags))
    
    def _getItem(self, n: str) -> TagDataModel.TagDataItem:
        """
        Make sure we get same object with same name
        """
        if not n in self._item_pool.keys():
            self._item_pool[n] = self.TagDataItem(n)
        return self._item_pool[n]
    
    def initData(self, tag_data: DataTags, tag_total: DataTags):
        assert tag_total.withParents().issuperset(tag_data.withParents())
        tag_items = []
        selected = []

        for t in tag_total.withParents():
            selected.append(t in tag_data)
            tag_items.append(self._getItem(t))
        
        self.ccl.initData(tag_items, selected)
        return
    
    def addNewData(self, tag: str, status: bool, unfold = True) -> bool:
        new_item = self._getItem(tag)
        if self.ccl.addItem(new_item, status):
            # add parent as well
            for p in TagRule.allParentsOf(tag):
                it = self._getItem(p)
                self.ccl.addItem(it, False)
            if unfold:
                parent_nodes =  self.ccl.graph.getNodeByItem(new_item).parents
                if parent_nodes:
                    for p_node in parent_nodes:
                        self.ccl.setCollapse(p_node.value, False)
            return True
        else:
            return False
    
    def setAllStatusToFalse(self):
        for i in self.ccl.items_checked:
            self.ccl.setItemChecked(i, False)

    @property
    def total_tags(self) -> DataTags:
        all_items = self.ccl.items_all
        return DataTags([str(i) for i in all_items])

    @property
    def selected_tags(self) -> DataTags:
        all_items = self.ccl.items_checked
        return DataTags([str(i) for i in all_items])

# from .tagSelector_old import TagSelector