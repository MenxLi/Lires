from __future__ import annotations
import os
from typing import Callable, Optional, Sequence, Union, List, overload, Dict

from PyQt6.QtWidgets import QListView, QHBoxLayout, QInputDialog, QVBoxLayout, QWidget, QPushButton
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

        self.act_rename_tag = QAction("Rename tag", self)
        self.act_delete_tag = QAction("Delete tag", self)
        self.ccl.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.ActionsContextMenu)
        self.ccl.addAction(self.act_rename_tag)
        self.ccl.addAction(self.act_delete_tag)

        self.act_rename_tag.triggered.connect(self.renameTag)
        self.act_delete_tag.triggered.connect(self.deleteTag)

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
    
    def renameTag(self):
        def _onConfirm(t: DataTags):
            if len(t) == 0:
                return
            tag = list(t)[0]
            data = self.getMainPanel().db.getDataByTags(DataTags([tag]))
            n_online = len(["" for d in data if not d.is_local])
            # confirm
            text, ok = QInputDialog.getText(self, "Edit tag".format(len(data)), \
                                            "Enter new tag for {} files ({} remote)".format(len(data), n_online), text = tag)
            if not ok:
                return 

            with self.getMainPanel().freeze():
                if self.getMainPanel().db.renameTag(tag, text):
                    curr_tags = self.getSelectedTags()
                    maybe_change_sel_tags = TagRule.renameTag(curr_tags, tag, text)
                    if maybe_change_sel_tags is not None:
                        new_selected_tags = maybe_change_sel_tags
                        saveToConf(default_tags = new_selected_tags.toOrderedList())
                    self.getMainPanel().reloadData()
                else:
                    self.statusBarInfo("Failed, check log for more info.", 5, bg_color = "red")

        total_tags = self.data_model.total_tags
        self.prompt = TagSelectPrompt(None, 
                total_tags, 
                onConfirm=_onConfirm,
                single_select=True)
        self.prompt.show()

    def deleteTag(self):
        def _onConfirm(tags: DataTags):
            if len(data) == 0:
                return
            data = self.getMainPanel().db.getDataByTags(tags)
            n_online = len(["" for d in data if not d.is_local])
            # confirm
            if not self.warnDialog("Delete tag: {}".format(tags), info_msg="For {} files ({})".format(len(data), n_online)):
                return
            if not self.warnDialog("Warning again, deleting tag: ***{}***".format(tags), info_msg="For {} files, Sure??".format(len(data))):
                return
            # do
            with self.getMainPanel().freeze():
                for tag in tags:
                    if self.getMainPanel().db.deleteTag(tag):
                        curr_tags = self.getSelectedTags()
                        maybe_deleted_sel_tags = TagRule.deleteTag(curr_tags, tag)
                        if maybe_deleted_sel_tags is not None:
                            saveToConf(default_tags = maybe_deleted_sel_tags.toOrderedList())
                        self.getMainPanel().reloadData()
                    else:
                        self.statusBarInfo("Failed, check log for more info.", 5, bg_color = "red")
                        break

        total_tags = self.data_model.total_tags
        self.prompt = TagSelectPrompt(None, 
                total_tags, 
                onConfirm=_onConfirm,
                single_select=False)
        self.prompt.show()
    
    def getCurrentHoveringTag(self) -> Optional[str]:
        return self.data_model.hovering_tag

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
    
    def _getTagStr(self, i: TagDataModel.TagDataItem):
        for k, v in self._item_pool.items():
            if i.dataitem_uid == v.dataitem_uid:
                return k
        raise ValueError("Tagitem not in tag pool")
    
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


class TagSelectPrompt(RefWidgetBase):

    def __init__(self, parent, 
            total_tags: DataTags, 
            onConfirm: Callable[[DataTags], None],
            single_select = False
            ) -> None:
        super().__init__(parent)
        self.tag_sel = TagSelector(self, tag_data = DataTags(), tag_total= total_tags)
        layout = QVBoxLayout()
        layout.addWidget(self.tag_sel)
        self.btn = QPushButton("OK")
        layout.addWidget(self.btn)
        self.setLayout(layout)

        def onDone():
            onConfirm(self._getSel())
            self.close()

        self.btn.clicked.connect(onDone)

        if single_select:
            self.tag_sel.ccl.onCheckItem.connect(self.deSelectOthers)
    
    def _getSel(self) -> DataTags:
        return self.tag_sel.getSelectedTags()
    
    def deSelectOthers(self, item: DataItemAbstract):
        for i in self.tag_sel.ccl.items_checked:
            if i.dataitem_uid != item.dataitem_uid:
                self.tag_sel.ccl.setItemChecked(i, False)