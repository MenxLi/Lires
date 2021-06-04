from PyQt5.QtWidgets import QHBoxLayout, QListView, QShortcut, QTableWidgetItem, QVBoxLayout, QWidget, QFrame, QTableWidget, QAbstractItemView, QHeaderView, QTableView
from PyQt5 import QtGui, QtCore
import typing, os, shutil, copy
from typing import Union, List 

from .bibQuery import BibQuery
from .widgets import WidgetBase
from ..backend.fileTools import FileManipulator
from ..backend.dataClass import DataBase, DataPoint, DataList, DataTags
from ..confReader import conf

DATA_PATH = conf["database"]

class FileSelectorGUI(WidgetBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
        self.setAcceptDrops(True)
    
    def initUI(self):
        self.frame = QFrame()
        self.frame.setFrameStyle(QFrame.StyledPanel)
        hbox = QHBoxLayout()
        hbox.addWidget(self.frame)
        self.setLayout(hbox)

        vbox = QVBoxLayout()
        self.data_view = QListView()
        self.data_model = FileListModel([])
        self.data_view.setModel(self.data_model)
        # self.data_view.setSelectionModel(QAbstractItemView.SingleSelection)

        vbox.addWidget(self.data_view)
        self.frame.setLayout(vbox)
    

class FileSelector(FileSelectorGUI):
    selection_changed = QtCore.pyqtSignal(DataPoint)
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        for k,v in kwargs:
            setattr(self, k, v)
    
    def connectFuncs(self):
        self.data_view.selectionModel().currentChanged.connect(self.onRowChanged)
        self.data_view.doubleClicked.connect(self.doubleClickOnEntry)
        self.shortcut_delete_selection = QShortcut(QtGui.QKeySequence("Del"), self)
        self.shortcut_delete_selection.activated.connect(self.deleteCurrentSelected)
    
    def loadValidData(self, tags: DataTags):
        """Load valid data by tags"""
        valid_data = DataList([])
        for d in self.parent.db.values():
            if tags.issubset(d.tags):
                valid_data.append(d)
        self.data_model.assignData(valid_data) 
        return True

    def getDataByTag(self, tags: list):
        pass

    def reloadData(self):
        self._clearList()
        self.getValidData()
    
    def _clearList(self):
        pass

    def addToDatabase(self, file_path:str):
        """ will be called by signal from bibQuery
        actual file manipulation is implemented in bibQuery
        """
        fm = FileManipulator(file_path)
        fm.screen()
        dp = DataPoint(fm)
        self.parent.db[dp.uuid] = dp
        self.data_model.add(dp)
    
    def _deleteFromDatabase(self, data: DataPoint):
        if data.uuid in self.parent.db.keys():
            shutil.rmtree(data.data_path)
            del self.parent.db[data.uuid]
    
    def deleteCurrentSelected(self):
        if not self.queryDialog("Delete this entry?"):
            return 
        indexes = self.data_view.selectedIndexes()
        if indexes:
            index = indexes[0]
        else:return False
        data = self.data_model.datalist[index.row()]
        self._deleteFromDatabase(data)
        del self.data_model.datalist[index.row()]
        self.data_model.layoutChanged.emit()
        # self.data_view.clearSelection()
    
    def onRowChanged(self, current, previous):
        row = current.row()
        data = self.data_model.datalist[row]
        self.selection_changed.emit(data)

    def doubleClickOnEntry(self):
        data = self.getCurrentSelection()
        if data is not None:
            data.fm.openFile()
    
    def getCurrentSelection(self) -> typing.Union[None, DataPoint]:
        indexes = self.data_view.selectedIndexes()
        if indexes:
            index = indexes[0]
        else: return None
        data = self.data_model.datalist[index.row()]
        return data

    def selectChange(self):
        pass
    
    def dragEnterEvent(self, a0: QtGui.QDragEnterEvent) -> None:
        if a0.mimeData().hasUrls():
            a0.accept()
        else:
            a0.ignore()
        return super().dragEnterEvent(a0)
    
    def dropEvent(self, a0: QtGui.QDropEvent) -> None:
        files = [u.toLocalFile() for u in a0.mimeData().urls()]
        for f in files:
            self.bib_quary = BibQuery(self, f)
            self.bib_quary.file_added.connect(self.addToDatabase)
            self.bib_quary.show()
        return super().dropEvent(a0)


class FileListModel(QtCore.QAbstractListModel):
    delete_current_selected = QtCore.pyqtSignal(DataPoint)
    def __init__(self, datalist: DataList) -> None:
        super().__init__()
        self.datalist = copy.deepcopy(datalist)
    
    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            data = self.datalist[index.row()]
            if len(data.authors) == 1:
                author = data.authors[0]
            else:
                author = data.authors[0] + " et al."
            text_to_display = "{year} - {author} >> {title}".format(
                year = data.year, author = author, title = data.title
            )
            return text_to_display
    
    def rowCount(self, index) -> int:
        return len(self.datalist)
    
    def add(self, dp: DataPoint):
        self.datalist.append(dp)
        self.layoutChanged.emit()
    
    def assignData(self, datalist: typing.List[DataPoint]):
        self.datalist = copy.deepcopy(datalist)
        self.layoutChanged.emit()
