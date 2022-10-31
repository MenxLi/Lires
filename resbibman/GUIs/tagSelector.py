from __future__ import annotations
from typing import Optional, Dict

from PyQt6.QtWidgets import QVBoxLayout
from PyQt6 import QtCore

from QCollapsibleCheckList import CollapsibleCheckList, DataItemAbstract

from .widgets import RefWidgetBase, WidgetBase
from ..confReader import saveToConf_guiStatus, getConf
from ..core.dataClass import DataTags, TagRule

class TagSelector(RefWidgetBase):
    entry_added = QtCore.pyqtSignal(str)

    def __init__(self, parent, tag_data = Optional[DataTags], tag_total = Optional[DataTags]) -> None:
        super().__init__(parent)
        self.initUI()
        if isinstance(tag_data, DataTags) and isinstance(tag_total, DataTags):
            self.initDataModel(tag_data, tag_total)    

    @property
    def database(self):
        return self.getMainPanel().database
    
    def initUI(self):
        self.ccl = CollapsibleCheckList(
            self,
            hover_highlight_color="rgba(100, 100, 100, 100)",
            click_line="check",
            )
        self.data_model = TagDataModel(self, self.ccl)
        layout = QVBoxLayout()
        layout.addWidget(self.ccl)
        self.setLayout(layout)

        # self.act_rename_tag = QAction("Rename tag", self)
        # self.act_delete_tag = QAction("Delete tag", self)
        # self.ccl.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.ActionsContextMenu)
        # self.ccl.addAction(self.act_rename_tag)
        # self.ccl.addAction(self.act_delete_tag)

    def initDataModel(self, tag_data: DataTags, tag_total: DataTags):
        """
        Load new data
        """
        self.data_model.initData(tag_data, tag_total)

    def getSelectedTags(self) -> DataTags:
        tags = self.data_model.selected_tags
        return tags

    def getTotalTags(self) -> DataTags:
        return self.data_model.total_tags
    
    def getCurrentHoveringTag(self) -> Optional[str]:
        return self.data_model.hovering_tag

    def addNewSelectedEntry(self, tag: str):
        if not self.data_model.addNewData(tag, True, unfold=True):
            self.infoDialog("The tag already exists")


class TagDataModel(QtCore.QObject, WidgetBase):
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
        
        def __ge__(self, __x: TagDataModel.TagDataItem) -> bool:
            return str(self) >= str(__x)
        
        def __lt__(self, __x: TagDataModel.TagDataItem) -> bool:
            return str(self) < str(__x)

    on_selection_change = QtCore.pyqtSignal(DataTags)    
    on_hover_tag = QtCore.pyqtSignal(str)

    def __init__(self, parent: Optional[QtCore.QObject], wid: CollapsibleCheckList):
        super().__init__(parent)
        self.ccl: CollapsibleCheckList[self.TagDataItem] = wid
        self._item_pool: Dict[str, self.TagDataItem] = {}
        self._connectSignal()
    
    def _connectSignal(self):
        self.ccl.onCheckItem.connect(lambda _: self.on_selection_change.emit(self.selected_tags))
        self.ccl.onUnCheckItem.connect(lambda _: self.on_selection_change.emit(self.selected_tags))

        self.ccl.onManualCollapseWidget.connect(lambda nodewid: self.setDefaultUnCollapseStatus(str(nodewid.data), False))
        self.ccl.onManualUnCollapseWidget.connect(lambda nodewid: self.setDefaultUnCollapseStatus(str(nodewid.data), True))
        self.ccl.onHoverEnter.connect(lambda item: self.on_hover_tag.emit(str(item)))
    
    def _getItem(self, n: str) -> TagDataModel.TagDataItem:
        """
        Make sure we get same object with same name
        """
        if not n in self._item_pool.keys():
            self._item_pool[n] = self.TagDataItem(n)
        return self._item_pool[n]
    
    def _getTagStr(self, i: TagDataModel.TagDataItem):
        for k, v in self._item_pool.items():
            if i.dataitem_uid == v.dataitem_uid:
                return k
        raise ValueError("Tagitem not in tag pool")
    
    def setDefaultUnCollapseStatus(self, tag: str, status: bool):
        """
        save to configuration
        """
        conf = getConf()
        uncollapse_status = conf["gui_status"]["tag_uncollapsed"]

        if status:
            if not tag in uncollapse_status:
                uncollapse_status.append(tag)
                self.logger.debug(f"Append {tag} to default uncollapse list")
        else:
            #remove both tag and it's subtags from uncollapsed
            potential_remove = DataTags([tag]).withChildsFrom(self.total_tags)
            for i in range(len(uncollapse_status))[::-1]:
                if uncollapse_status[i] in potential_remove:
                    self.logger.debug(f"Pop {uncollapse_status[i]} from default uncollapse list")
                    uncollapse_status.pop(i)
        saveToConf_guiStatus(tag_uncollapsed = uncollapse_status)

    def loadDefaultUnCollapseStatus(self):
        conf = getConf()
        uncollapse_status = conf["gui_status"]["tag_uncollapsed"]
        total_tags = self.total_tags
        for i in range(len(uncollapse_status))[::-1]:
            if not uncollapse_status[i] in total_tags:
                self.logger.info(f"Tag {uncollapse_status[i]} is not in total tags "
                "and is popped out of default uncollapse list "
                f"(Total tags: {total_tags})")
                uncollapse_status.pop(i)
            else:
                self.ccl.setCollapse(self._getItem(uncollapse_status[i]), False)
        saveToConf_guiStatus(tag_uncollapsed = uncollapse_status)
        return
    
    def initData(self, tag_data: DataTags, tag_total: DataTags):
        assert tag_total.withParents().issuperset(tag_data.withParents())
        tag_items = []
        selected = []

        for t in tag_total.withParents():
            selected.append(t in tag_data)
            tag_items.append(self._getItem(t))
        
        self.ccl.initData(tag_items, selected)
        self.loadDefaultUnCollapseStatus()
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
        print(self.ccl.items_checked)
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
    
    @property
    def hovering_tag(self) -> Optional[str]:
        i_hover = self.ccl.item_hover
        if i_hover:
            return self._getTagStr(i_hover)
        else:
            return None
