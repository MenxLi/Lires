from PyQt5.QtWidgets import QStyle, QWidget, QMessageBox, QListView, QHBoxLayout, QVBoxLayout
from PyQt5 import QtCore
from PyQt5 import QtGui

from .widgets import WidgetBase
from ..backend.dataClass import DataTags

class TagSelector(WidgetBase):
    entry_added = QtCore.pyqtSignal(str)

    def __init__(self, tag_data = None, tag_total = None) -> None:
        super().__init__()
        self.initUI()
        if isinstance(tag_data, DataTags) and isinstance(tag_total, DataTags):
            self.constructDataModel(tag_data, tag_total)    

    def initUI(self):
        self.tag_view = QListView()
        hbox = QHBoxLayout()
        hbox.addWidget(self.tag_view)
        self.setLayout(hbox)
        self.tag_view.clicked.connect(self.checkCurrentTag)

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
    
    def changeSelectedTags(self, new_tags: DataTags):
        pass

    def addNewSelectedEntry(self, tag: str):
        self.tag_model.datalist.append([True, tag])
        self.tag_model.sortByAplhabet()
        self.tag_model.layoutChanged.emit()
    
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

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            status, tag = self.datalist[index.row()]
            return tag
        if role == QtCore.Qt.DecorationRole:
            status, _ = self.datalist[index.row()]
            if status:
                tick = QtGui.QColor("Green")    # or QImage
            else:
                tick = QtGui.QColor("Gray")
            return tick

    def rowCount(self, index):
        return len(self.datalist)
    
    def sortByAplhabet(self):
        self.datalist.sort(key = lambda x: x[1])
    
    def setAllStatusToFalse(self):
        for i in self.datalist:
            i[0] = False
        self.layoutChanged.emit()
    