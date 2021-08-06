from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QAction, QHBoxLayout, QItemDelegate, QLineEdit, QListView, QMessageBox, QShortcut, QTableWidgetItem, QVBoxLayout, QWidget, QFrame, QTableWidget, QAbstractItemView, QHeaderView, QTableView, QFileDialog
from PyQt5 import QtGui, QtCore
import typing, os, shutil, copy
from typing import Union, List 

from .bibQuery import BibQuery
from .widgets import WidgetBase, MainWidgetBase
from ..backend.fileTools import FileManipulator
from ..backend.dataClass import DataBase, DataPoint, DataList, DataTags, DataTableList
from ..backend.utils import copy2clip
from ..confReader import getConf, getConfV

class FileSelectorGUI(MainWidgetBase):
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

        # self.data_view = QListView()
        # self.data_model = FileListModel(DataList([]))
        self.data_view = FileTableView()
        self.data_model = FileTableModel(DataList([]))
        self.data_view.setModel(self.data_model)
        self.data_view.initSettings()
        self.search_edit = QLineEdit()

        vbox = QVBoxLayout()
        vbox.addWidget(self.search_edit)
        vbox.addWidget(self.data_view)
        self.frame.setLayout(vbox)

        self._initActions()
    
    def _initActions(self):
        self.act_open_location = QAction("Open file location", self)
        self.act_delete_file = QAction("Delete", self)
        self.act_export_bib = QAction("Export as .bib", self)
        self.act_copy_bib = QAction("Copy bib", self)
        self.act_add_file = QAction("Add file", self)

        self.data_view.addAction(self.act_copy_bib)
        self.data_view.addAction(self.act_add_file)
    

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
        self.search_edit.textChanged.connect(self.onSearchTextChange)

        self.act_copy_bib.triggered.connect(self.copyCurrentSelectionBib)
        self.act_add_file.triggered.connect(self.addFileToCurrentSelection)

    def loadValidData(self, tags: DataTags, hint = False):
        """Load valid data by tags"""
        # valid_data = DataList([])
        # for d in self.getMainPanel().db.values():
            # if tags.issubset(d.tags):
                # valid_data.append(d)
        valid_data = self.getMainPanel().db.getDataByTags(tags)
        screen_pattern = self.search_edit.text()
        if screen_pattern != "":
            valid_data = DataList([i for i in valid_data if i.screenByPattern(screen_pattern)])
        sort_method = getConf()["sort_method"]
        valid_data.sortBy(sort_method)
        self.data_model.assignData(valid_data) 
        if hint:
            print("Data loaded, tags: {tags}, sorting method: {sort_method}, screen_pattern: {screen_pattern}".\
                format(tags = " | ".join(tags), sort_method = sort_method, screen_pattern = screen_pattern))
        return True

    def onSearchTextChange(self):
        text = self.search_edit.text()
        self.loadValidData(tags = set(getConf()["default_tags"]))

    def reloadData(self):
        # self._clearList()
        self.loadValidData(tags = self.getMainPanel().getCurrentSelectedTags(), )
    
    def copyCurrentSelectionBib(self):
        selected = self.getCurrentSelection(return_multiple=True)
        bibs =[s.fm.readBib() for s in selected]  
        if len(bibs) > 1:
            bibs = ",\n".join(bibs)
        else:
            bibs = bibs[0]
        copy2clip("\""+bibs+"\"")
        print(bibs)

    def addFileToCurrentSelection(self):
        """Add file to a no-file entry point"""
        extensions = getConf()["accepted_extensions"]
        extension_filter = "({})".format(" ".join(["*"+i for i in extensions]))
        dp = self.getCurrentSelection(return_multiple=False)
        if dp.has_file:
            self.warnDialog("Adding failed, the file exists.")
            return False
        fname = QFileDialog.getOpenFileName(self, caption="Select file for {}".format(dp.title[:25]), filter=extension_filter)[0]
        if dp.fm.addFile(fname):
            dp.reload()
            QMessageBox.information(self, "Success", "File added")

    def addToDatabase(self, file_path:str):
        """ will be called by signal from bibQuery
        actual file manipulation is implemented in bibQuery
        """
        fm = FileManipulator(file_path)
        fm.screen()
        dp = DataPoint(fm)
        self.getMainPanel().db[dp.uuid] = dp
        self.data_model.add(dp)
    
    def _deleteFromDatabase(self, data: DataPoint):
        if data.uuid in self.getMainPanel().db.keys():
            shutil.rmtree(data.data_path)
            del self.getMainPanel().db[data.uuid]
    
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
        #self.getMainPanel.refreshFileTagSelector()
        self.reloadData()
    
    def onRowChanged(self, current, previous):
        row = current.row()
        data = self.data_model.datalist[row]
        self.selection_changed.emit(data)

    def doubleClickOnEntry(self):
        data = self.getCurrentSelection()
        if data is not None:
            data.fm.openFile()
    
    def getCurrentSelection(self, return_multiple = False) -> typing.Union[None, DataPoint, DataList]:
        indexes = self.data_view.selectedIndexes()
        if not indexes:
            return None
        try:
            all_data = [self.data_model.datalist[index.row()] for index in indexes]
        except:
            # When index is larger than the length of the data
            return None

        if return_multiple:
            return DataList(set(all_data))
        else:
            return all_data[0]

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
        self.getMainPanel().addFilesToDatabaseByURL(files)
        return super().dropEvent(a0)
    
    def addFilesToDatabseByURL(self, urls: List[str]):
        """deprecated"""
        curr_selected_tags = self.getMainPanel().getCurrentSelectedTags()
        curr_total_tags = self.getMainPanel().getTotalTags()
        for f in urls:
            self.bib_quary = BibQuery(self, f, tag_data=curr_selected_tags, tag_total=curr_total_tags)
            self.bib_quary.tag_edit.setMainPanel(self.getMainPanel())
            self.bib_quary.file_added.connect(self.addToDatabase)
            self.bib_quary.file_added.connect(self.getMainPanel().refreshFileTagSelector)
            self.bib_quary.show()


class FileListModel(QtCore.QAbstractListModel):
    delete_current_selected = QtCore.pyqtSignal(DataPoint)
    def __init__(self, datalist: DataList) -> None:
        super().__init__()
        self.datalist = copy.deepcopy(datalist)
    
    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            data = self.datalist[index.row()]
            if len(data.authors) == 1:
                author = self._getFirstName(data.authors[0])
            else:
                author = self._getFirstName(data.authors[0]) + " et al."
            connection = "\u279C"
            text_to_display = "{year} - {author} {connect} {title}".format(
                year = data.year, connect = connection, author = author, title = data.title
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
    
    def sortBy(self, sort_method: str):
        """
        - sort_method: refer to static items in backend.dataClass.DataList
        """
        self.datalist.sortBy(sort_method)
    
    def _getFirstName(self, name: str):
        x = name.split(", ")
        return x[0]

class FileTableModel(QtCore.QAbstractTableModel):
    # https://gist.github.com/katmai1/75aa8b03846a94fa11b38daf656c6e93
    delete_current_selected = QtCore.pyqtSignal(DataPoint)
    def __init__(self, datalist: DataList) -> None:
        super().__init__()
        self.datalist = DataTableList(datalist)

    def assignData(self, datalist: typing.List[DataPoint]):
        self.datalist = DataTableList(datalist)
        self.layoutChanged.emit()

    def sortBy(self, sort_method: str):
        """
        - sort_method: refer to static items in backend.dataClass.DataList
        """
        self.datalist.sortBy(sort_method)

    def add(self, dp: DataPoint):
        self.datalist.append(dp)
        self.layoutChanged.emit()
    
    def data(self, index: QtCore.QModelIndex, role):
        if role == QtCore.Qt.DisplayRole:
            return self.datalist.getTableItem(row = index.row(), col = index.column())

    def rowCount(self, parent: QtCore.QModelIndex) -> int:
        return len(self.datalist)
    
    def columnCount(self, parent: QtCore.QModelIndex) -> int:
        return len(getConfV("table_headers"))

class FileTableView(QTableView):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.setAutoScroll(False)
    def initSettings(self):
        # https://stackoverflow.com/questions/38098763/pyside-pyqt-how-to-make-set-qtablewidget-column-width-as-proportion-of-the-a
        self.header = self.horizontalHeader()       
        self.header.setVisible(False)
        self.header.setMinimumSectionSize(1)
        for i in range(len(getConfV("table_headers"))):
            if getConfV("table_headers")[i] == DataTableList.HEADER_TITLE:
                self.header.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
            else:
                self.header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)

class CItemDelegate(QItemDelegate):
    pass
