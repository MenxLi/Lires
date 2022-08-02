import os
import typing
from typing import Union, List

from PyQt6.QtWidgets import QListView, QHBoxLayout, QInputDialog
from PyQt6.QtGui import QAction, QFont
from PyQt6 import QtCore
from PyQt6 import QtGui

from .widgets import RefWidgetBase
from ._styleUtils import qIconFromSVG_autoBW
from ..confReader import ICON_PATH, getConfV, saveToConf
from ..core.dataClass import DataTags

class TagSelector(RefWidgetBase):
    entry_added = QtCore.pyqtSignal(str)

    def __init__(self, tag_data = None, tag_total = None) -> None:
        super().__init__()
        self.initUI()
        self.initActions()
        self.connetFuncs()
        if isinstance(tag_data, DataTags) and isinstance(tag_total, DataTags):
            self.constructDataModel(tag_data, tag_total)    

    @property
    def database(self):
        return self.getMainPanel().database

    def initUI(self):
        self.tag_view = QListView()
        self.tag_view.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.ActionsContextMenu)
        hbox = QHBoxLayout()
        hbox.addWidget(self.tag_view)
        self.setLayout(hbox)
    
    def initActions(self):
        self.act_rename_tag = QAction("Rename tag", self)
        self.act_delete_tag = QAction("Delete tag", self)
        self.tag_view.addAction(self.act_rename_tag)
        self.tag_view.addAction(self.act_delete_tag)
    
    def connetFuncs(self):
        self.tag_view.clicked.connect(self.checkCurrentTag)
        self.act_rename_tag.triggered.connect(self.changeSelectedTag)
        self.act_delete_tag.triggered.connect(self.deleteSelectedTag)

    def constructDataModel(self, tag_data: DataTags, tag_total: DataTags):
        self.tag_data = tag_data
        self.tag_total = tag_total
        self.tag_model = TagListModel(self.tag_data, self.tag_total)
        self.tag_view.setModel(self.tag_model)
    
    def checkCurrentTag(self):
        indexes = self.tag_view.selectedIndexes()
        if indexes:
            index = indexes[0]
            row = index.row()
            self.tag_model.datalist[row][0] = not self.tag_model.datalist[row][0]
            self.tag_model.dataChanged.emit(index, index)
            # Clear the selection (as it is no longer valid).
            self.tag_view.clearSelection()

    def getSelectedTags(self) -> DataTags:
        tag_lis = [x[1] for x in self.tag_model.datalist if x[0] == True]
        return DataTags(tag_lis)

    def getTotalTags(self) -> DataTags:
        tag_lis = [x[1] for x in self.tag_model.datalist]
        return DataTags(tag_lis)
    
    def changeSelectedTag(self):
        selection = self.getCurrentSelection()
        if selection:
            tag = selection[1]
        else:
            return
        data = self.getMainPanel().db.getDataByTags(DataTags([tag]))
        n_online = len(["" for d in data if not d.is_local])
        # confirm
        text, ok = QInputDialog.getText(self, "Edit tag".format(len(data)), \
                                        "Enter new tag for {} files ({} remote)".format(len(data), n_online), text = tag)
        if not ok:
            return 
        # do
        with self.getMainPanel().freeze():
            if self.getMainPanel().db.renameTag(tag, text):
                curr_tags = self.getSelectedTags()
                taglist = curr_tags.toOrderedList()
                taglist = [text if i == tag else i for i in taglist]
                saveToConf(default_tags = DataTags(taglist).toOrderedList())
                self.getMainPanel().reloadData()
            else:
                self.statusBarInfo("Failed, check log for more info.", 5, bg_color = "red")

    def deleteSelectedTag(self):
        selection = self.getCurrentSelection()
        if selection:
            tag = selection[1]
        else:
            return
        data = self.getMainPanel().db.getDataByTags(DataTags([tag]))
        n_online = len(["" for d in data if not d.is_local])
        # confirm
        if not self.warnDialog("Delete tag: {}".format(tag), info_msg="For {} files ({})".format(len(data), n_online)):
            return
        if not self.warnDialog("Warning again, deleting tag: ***{}***".format(tag), info_msg="For {} files, Sure??".format(len(data))):
            return
        # do
        with self.getMainPanel().freeze():
            if self.getMainPanel().db.deleteTag(tag):
                self.getMainPanel().reloadData()
            else:
                self.statusBarInfo("Failed, check log for more info.", 5, bg_color = "red")

    def addNewSelectedEntry(self, tag: str):
        self.tag_model.datalist.append([True, tag])
        self.tag_model.sortByAplhabet()
        self.tag_model.layoutChanged.emit()

    def getCurrentSelection(self) -> typing.Union[None, typing.Tuple[bool, str]]:
        indexes = self.tag_view.selectedIndexes()
        if not indexes:
            return None
        try:
            all_data = [self.tag_model.datalist[index.row()] for index in indexes]
        except:
            # When index is larger than the length of the data
            return None
        return all_data[0]
    
class TagListModel(QtCore.QAbstractListModel):
    def __init__(self, tag_data: DataTags, tag_total: DataTags) -> None:
        """
        tag_data - the tags to be marked as 1, subset of tag_total
        tag_total - total tags
        """
        super().__init__()
        if not tag_data.issubset(tag_total):
            raise Exception("Contains tag that not in total tag pool, check tags' info")
        datalist = [[False, d] for d in tag_total.toOrderedList()]
        for d in datalist:
            if d[1] in tag_data:
                d[0] = True
        self.datalist = datalist 

        self.TICK_CHECK = qIconFromSVG_autoBW(os.path.join(ICON_PATH, "check_circle-24px.svg"))
        self.TICK_UNCHECK = qIconFromSVG_autoBW(os.path.join(ICON_PATH, "check_circle_blank-24px.svg"))

    def data(self, index, role):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            status, tag = self.datalist[index.row()]
            return tag
        if role == QtCore.Qt.ItemDataRole.FontRole:
            return QFont(*getConfV("font_sizes")["tag"])
        if role == QtCore.Qt.ItemDataRole.DecorationRole:
            status, _ = self.datalist[index.row()]
            if status:
                # tick = QtGui.QColor("Green")    # or QImage
                tick = self.TICK_CHECK
            else:
                # tick = QtGui.QColor("Gray")
                tick = self.TICK_UNCHECK
            return tick

    def rowCount(self, index):
        return len(self.datalist)
    
    def sortByAplhabet(self):
        self.datalist.sort(key = lambda x: x[1])
    
    def setAllStatusToFalse(self):
        for i in self.datalist:
            i[0] = False
        self.layoutChanged.emit()
    
