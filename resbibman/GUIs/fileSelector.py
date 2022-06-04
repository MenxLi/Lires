import webbrowser
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QHBoxLayout, QItemDelegate, QLineEdit, QMessageBox, QVBoxLayout, QFrame, QAbstractItemView, QTableView, QFileDialog
from PyQt6.QtGui import QAction, QShortcut
from PyQt6 import QtGui, QtCore
import typing, os, shutil, copy, functools
from typing import List, overload, Union, Literal, Callable

from .bibQuery import BibQuery
from .widgets import  MainWidgetBase
from .bibtexEditor import BibEditorWithOK
from ..core import globalVar as G
from ..core.fileTools import FileManipulator
from ..core.dataClass import  DataPoint, DataList, DataTags, DataTableList
from ..core.utils import copy2clip, openFile
from ..confReader import getConf, getConfV

class FileSelectorGUI(MainWidgetBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
        self.setAcceptDrops(True)
    
    def initUI(self):
        self.frame = QFrame()
        self.frame.setFrameStyle(QFrame.Shape.StyledPanel)
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
        self.act_sync_datapoint = QAction("Sync", self)
        self.act_edit_bib = QAction("Edit bibtex info", self)
        self.act_open_location = QAction("Open file location", self)
        self.act_delete_file = QAction("Delete", self)
        self.act_export_bib = QAction("Export as .bib", self)
        self.act_copy_bib = QAction("Copy bib", self)
        self.act_copy_citation = QAction("Copy citation", self)
        self.act_add_file = QAction("Add file", self)
        self.act_free_doc = QAction("Free document", self)

        self.data_view.addAction(self.act_sync_datapoint)
        self.data_view.addAction(self.act_edit_bib)
        self.data_view.addAction(self.act_open_location)
        self.data_view.addAction(self.act_copy_citation)
        self.data_view.addAction(self.act_copy_bib)
        self.data_view.addAction(self.act_add_file)
        self.data_view.addAction(self.act_free_doc)
        self.data_view.addAction(self.act_delete_file)
    

class FileSelector(FileSelectorGUI):
    selection_changed = QtCore.pyqtSignal(DataPoint)
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        for k,v in kwargs:
            setattr(self, k, v)

    @property
    def database(self):
        return self.getMainPanel().database
    
    def connectFuncs(self):
        self.data_view.selectionModel().currentChanged.connect(self.onRowChanged)
        self.data_view.doubleClicked.connect(self.doubleClickOnEntry)

        self.shortcut_delete_selection = QShortcut(QtGui.QKeySequence("Del"), self)
        self.shortcut_delete_selection.activated.connect(self.deleteCurrentSelected)
        self.shortcut_open_tagedit = QShortcut(QtGui.QKeySequence("Space"), self)
        self.shortcut_open_tagedit.activated.connect(lambda: self.getTagPanel().openTagEditor())

        self.search_edit.textChanged.connect(self.onSearchTextChange)

        self.act_sync_datapoint.triggered.connect(lambda: self.syncCurrentSelections_async())
        self.act_open_location.triggered.connect(self.openCurrFileLocation)
        self.act_copy_bib.triggered.connect(self.copyCurrentSelectionBib)
        self.act_copy_citation.triggered.connect(self.copyCurrentSelectionCitation)
        self.act_add_file.triggered.connect(lambda : self.addFileToCurrentSelection(fname = None))
        self.act_free_doc.triggered.connect(self.freeDocumentOfCurrentSelection)
        self.act_edit_bib.triggered.connect(self.editBibtex)
        self.act_delete_file.triggered.connect(self.deleteCurrentSelected)

    def offlineStatus(self, status: bool):
        super().offlineStatus(status)
        disable_wids = [
            self.act_edit_bib,
            self.act_open_location,
            self.act_delete_file,
            self.act_add_file,
            self.act_free_doc,
            self.shortcut_delete_selection,
            self.shortcut_open_tagedit,
        ]
        for wid in disable_wids:
            wid.setEnabled(status)
    
    def __syncCurrentSelections(self) -> bool:
        """Deprecated"""
        selections = self.getCurrentSelection(return_multiple=True)
        SUCCESS = True
        if selections is None:
            return False
        for d in selections:
            d: DataPoint
            if not d.sync():
                SUCCESS = False
        if len(selections) == 1 and selections[0].is_local:
            # only one selection and sync successed
            self.offlineStatus(True)
            self.getInfoPanel().offlineStatus(True)
            self.getTagPanel().offlineStatus(True)
        return SUCCESS

    def syncCurrentSelections_async(self, callback_on_finish: Callable[[bool], None] = lambda _ : None) -> None:
        """
         - callback_on_finish: additional callback to be called when sync is finished
        """
        selections = self.getCurrentSelection(return_multiple=True)
        if selections is None:
            return
        # only one selection and sync successed, do
        _only_one = len(selections) == 1
        def on_finish(success):
            self.setEnabled(True)
            if success and _only_one:
                self.offlineStatus(True)
                self.getInfoPanel().offlineStatus(True)
                self.getTagPanel().offlineStatus(True)
            callback_on_finish(success)

        self.setEnabled(False)   # Don't change data selection
        self.getMainPanel().syncData_async(selections, on_finish)
        return 

    def loadValidData(self, tags: DataTags, hint = False):
        """Load valid data by tags"""
        valid_data = self.getMainPanel().db.getDataByTags(tags)
        screen_pattern = self.search_edit.text()
        if screen_pattern != "":
            valid_data = DataList([i for i in valid_data if i.screenByPattern(screen_pattern)])
        sort_method = getConf()["sort_method"]
        valid_data.sortBy(sort_method)
        self.data_model.assignData(valid_data) 
        if hint:
            self.logger.debug("Data loaded, tags: {tags}, sorting method: {sort_method}, screen_pattern: {screen_pattern}".\
                format(tags = " | ".join(tags), sort_method = sort_method, screen_pattern = screen_pattern))
        return True

    def onSearchTextChange(self):
        text = self.search_edit.text()
        self.loadValidData(tags = set(getConf()["default_tags"]))
        curr_data = self.getCurrentSelection()
        if not curr_data is None:
            self.selection_changed.emit(curr_data)

    def reloadData(self):
        # self._clearList()
        self.loadValidData(tags = self.getMainPanel().getCurrentSelectedTags(), )
    
    def openCurrFileLocation(self):
        curr_data = self.getCurrentSelection()
        if not curr_data is None:
            openFile(curr_data.fm.path)
    
    def copyCurrentSelectionBib(self):
        selected = self.getCurrentSelection(return_multiple=True)
        bibs =[s.fm.readBib() for s in selected]  
        if len(bibs) > 1:
            bibs = ",\n".join(bibs)
        else:
            bibs = bibs[0]
        copy2clip("\""+bibs+"\"")

    def copyCurrentSelectionCitation(self):
        selected = self.getCurrentSelection(return_multiple=True)
        citations = [x.stringCitation() for x in selected]
        copy2clip("\""+"\n".join(citations)+"\"")

    def editBibtex(self):
        selected = self.getCurrentSelection(return_multiple=False)

        if selected is None:
            return
        selected: DataPoint
        self.logger.debug("Editing bibtex for {}".format(selected.uuid))
        def onConfirm(txt: str):
            new_base = selected.changeBib(txt)
            self.selection_changed.emit(selected)
            # debug
            if new_base:
                self.logger.debug("generate new base name")

        self.bib_edit = BibEditorWithOK()
        self.bib_edit.text = selected.fm.readBib()
        self.bib_edit.on_confirmed.connect(onConfirm)
        self.bib_edit.show()
    
    def freeDocumentOfCurrentSelection(self):
        selected = self.getCurrentSelection(return_multiple=True)
        if not selected:
            return None
        to_be_free = "\n".join(["* " + str(d) for d in selected])
        warnmsg = "This action will delete document file(s) in following item(s):\n{}\nContinue?".format(to_be_free)
        if self.queryDialog(warnmsg):
            for d in selected:
                d: DataPoint
                d.fm.deleteDocument()
                d.reload()
            self.getInfoPanel().refresh()
            self.reloadData()

    def addFileToCurrentSelection(self, fname = None):
        """Add file to a no-file entry point"""
        extensions = getConf()["accepted_extensions"]
        extension_filter = "({})".format(" ".join(["*"+i for i in extensions]))
        dp = self.getCurrentSelection(return_multiple=False)
        if dp is None:
            return False
        if dp.has_file:
            self.warnDialog("Adding failed, the file exists.")
            return False
        if fname is None:
            fname = QFileDialog.getOpenFileName(self, caption="Select file for {}".format(dp.title[:25]), filter=extension_filter)[0]
        if dp.fm.addFile(fname):
            dp.reload()
            QMessageBox.information(self, "Success", "File added")

    def addToDatabase(self, file_path:str):
        """ will be called by signal from bibQuery
        actual file manipulation is implemented in bibQuery
        """
        dp = self.getMainPanel().db.add(file_path)
        self.data_model.add(dp)
    
    def _deleteFromDatabase(self, data: DataPoint):
        if data.uuid in self.getMainPanel().db.keys():
            self.getMainPanel().db.delete(data.uuid)
    
    def deleteCurrentSelected(self):
        query_line = "Delete this entry?"
        if not self.getMainPanel().database.offline:
            query_line += "\n(Will delete remote file as well)"
        if not self.queryDialog(query_line):
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
        # self._info_panel._saveComments()
        row = current.row()
        data: DataPoint = self.data_model.datalist[row]

        # decide if un-saved comments
        if self.getInfoPanel().queryCommentSaveStatus() == "changed":
            self.statusBarInfo("You may have un-saved changes lost...", 3.5, bg_color = "red")
        # may fail because file may not be in local
        # sync with fm.setWatch(True) when finished is used to make sure files are watched
        self.database.watchFileChange([data])   

        self.selection_changed.emit(data)       # info panel will change here
        self.offlineStatus(data.is_local)

    def doubleClickOnEntry(self):
        data = self.getCurrentSelection()
        def _open(dp: DataPoint):
            """
            Open a data point locally
            """
            web_url = dp.fm.getWebUrl()
            if not dp.fm.openFile() and dp.is_local:
                if web_url == "":
                    self.warnDialog("The file is missing", "To add the paper, right click on the entry -> add file")
                elif os.path.exists(web_url):
                    openFile(web_url)
                else:
                    webbrowser.open(web_url)
        def _onSyncDone(success, to_open):
            if not success and G.last_status_code == 401:
                self.statusBarInfo("Unauthorized access", 5, bg_color = "red")
            if success:
                _open(to_open)

        if isinstance(data, DataPoint):
            if not data.is_local:
                self.syncCurrentSelections_async(functools.partial(_onSyncDone, to_open = data))
            else:
                _open(data)

    @overload
    def getCurrentSelection(self, return_multiple: Literal[True]) -> Union[None, DataList]: ...

    @overload
    def getCurrentSelection(self, return_multiple: Literal[False] = False) -> Union[None, DataPoint]: ...
    
    def getCurrentSelection(self, return_multiple = False) -> Union[None, DataPoint, DataList]:
        indexes = self.data_view.selectedIndexes()
        if indexes == [] or not indexes:
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
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
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
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return self.datalist.getTableItem(row = index.row(), col = index.column())

    def rowCount(self, parent: QtCore.QModelIndex) -> int:
        return len(self.datalist)
    
    def columnCount(self, parent: QtCore.QModelIndex) -> int:
        return len(getConfV("table_headers"))

class FileTableView(QTableView):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.ActionsContextMenu)
        self.setAutoScroll(False)
        # self.setFont(QtGui.QFont("Times New Roman", 12))
        self.setFont(QtGui.QFont("Times New Roman", 10))
        # self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(16)
    def initSettings(self):
        # https://stackoverflow.com/questions/38098763/pyside-pyqt-how-to-make-set-qtablewidget-column-width-as-proportion-of-the-a
        self.header = self.horizontalHeader()       
        self.header.setVisible(False)
        self.header.setMinimumSectionSize(1)
        for i in range(len(getConfV("table_headers"))):
            if getConfV("table_headers")[i] == DataTableList.HEADER_TITLE:
                self.header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.Stretch)
            else:
                self.header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

class CItemDelegate(QItemDelegate):
    pass
