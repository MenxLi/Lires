from PyQt5.QtWidgets import QWidget, QFrame, QHBoxLayout, QListView
from PyQt5 import QtCore, QtGui
from .widgets import WidgetBase
from ..backend.dataClass import DataTags

class FileTagGUI(WidgetBase):
    """
    Implement the GUI for file tree
    """
    def __init__(self, parent = None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.frame = QFrame()
        self.frame.setFrameStyle(QFrame.StyledPanel)
        hbox = QHBoxLayout()
        hbox.addWidget(self.frame)
        self.setLayout(hbox)

class FileTag(FileTagGUI):
    """
    Implement the functions for file tree
    """
    def __init__(self, parent = None):
        super().__init__(parent)
    
    def connectFuncs(self):
        pass

class TagSelector(WidgetBase):
    entry_added = QtCore.pyqtSignal(str)

    def __init__(self, tag_data: DataTags, tag_total: DataTags) -> None:
        super().__init__()
        self.tag_data = tag_data
        self.tag_total = tag_total
        self.initUI()

    def initUI(self):
        self.tag_view = QListView()
        self.tag_model = TagListModel(self.tag_data, self.tag_total)
        self.tag_view.setModel(self.tag_model)
        hbox = QHBoxLayout()
        hbox.addWidget(self.tag_view)
        self.setLayout(hbox)
        self.tag_view.clicked.connect(self.checkCurrentTag)
    
    def checkCurrentTag(self):
        indexes = self.tag_view.selectedIndexes()
        if indexes:
            index = indexes[0]
            row = index.row()
            self.tag_model.datalist[row][0] = not self.tag_model.datalist[row][0]
            self.tag_model.dataChanged.emit(index, index)
            # Clear the selection (as it is no longer valid).
            self.tag_view.clearSelection()

    def getCurrentTags(self) -> DataTags:
        tag_lis = [x[1] for x in self.tag_model.datalist if x[0] == True]
        return DataTags(tag_lis)

    def getAllTags(self) -> DataTags:
        tag_lis = [x[1] for x in self.tag_model.datalist]
        return DataTags(tag_lis)

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
    