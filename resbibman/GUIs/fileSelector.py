import traceback, math, webbrowser
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QHBoxLayout, QItemDelegate, QMessageBox, QStyleOptionViewItem, QVBoxLayout, QFrame, QAbstractItemView, QTableView, QFileDialog, QStyledItemDelegate, QStyle
from PyQt6.QtGui import QAction, QShortcut, QColor
from PyQt6 import QtGui, QtCore
import typing, copy, functools
from typing import List, overload, Union, Literal, Callable, Optional, cast

from .bibQuery import BibQuery
from .widgets import  MainWidgetBase, LazyResizeMixin
from .searchBar import SearchBar
from .bibtexEditor import BibEditorWithOK
from ..perf.qtThreading import SearchWorker
from ..core import globalVar as G
from ..core.dataClass import  DataPoint, DataList, DataTags, DataTableList
from ..core.dataSearcher import StringSearchT, DataSearcher
from ..core.utils import copy2clip, openFile
from ..core.encryptClient import generateHexHash
from ..confReader import getConf, getConfV, getServerURL
from ..types.configT import _ConfFontSizeT

class FileSelectorGUI(MainWidgetBase):
    def __init__(self, parent):
        super().__init__(parent)
        self._parent = parent
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
        self.data_table_delegate = FileTableDelegate()
        self.data_view = FileTableView()
        self.data_view.setItemDelegate(self.data_table_delegate)
        self.data_model = FileTableModel(DataList([]))
        self.data_view.setModel(self.data_model)
        self.data_view.initSettings()
        self.search_bar = SearchBar()

        self.data_view.hoverIndexChanged.connect(self.data_table_delegate.onHoverIndexChanged)
        self.data_view.selectionModel().currentChanged.connect(self.data_table_delegate.onSelectionIndexChanged)

        vbox = QVBoxLayout()
        vbox.addWidget(self.search_bar)
        vbox.addWidget(self.data_view)
        self.frame.setLayout(vbox)

        self._initActions()
    
    def _initActions(self):
        self.act_sync_datapoint = QAction("Sync", self)
        self.act_add_file = QAction("Add file", self)
        self.act_edit_bib = QAction("Edit bibtex info", self)
        self.act_open_location = QAction("Open file location", self)
        self.act_delete_file = QAction("Delete", self)
        self.act_export_bib = QAction("Export as .bib", self)
        self.act_copy_bib = QAction("Copy bib", self)
        self.act_copy_citation = QAction("Copy citation", self)
        self.act_copy_uuid = QAction("Copy uuid", self)
        self.act_export_data = QAction("Export data", self)
        self.act_free_doc = QAction("Free document", self)
        self.act_share_doc = QAction("Copy share link", self)
        self.act_summarize = QAction("Summarize", self)

        def addSeparator():
            separator = QAction(self)
            separator.setSeparator(True)
            self.data_view.addAction(separator)

        self.data_view.addAction(self.act_sync_datapoint)
        self.data_view.addAction(self.act_add_file)
        self.data_view.addAction(self.act_free_doc)
        addSeparator()
        self.data_view.addAction(self.act_copy_citation)
        self.data_view.addAction(self.act_copy_bib)
        self.data_view.addAction(self.act_edit_bib)
        self.data_view.addAction(self.act_copy_uuid)
        addSeparator()
        self.data_view.addAction(self.act_share_doc)
        addSeparator()
        self.data_view.addAction(self.act_summarize)
        addSeparator()
        self.data_view.addAction(self.act_open_location)
        self.data_view.addAction(self.act_export_data)
        self.data_view.addAction(self.act_delete_file)

    def applyFontConfig(self, font_config: _ConfFontSizeT):
        data_view = self.data_view
        data_view.setFont(QtGui.QFont(*font_config["data"]))
        data_font_size = font_config["data"][1]
        data_view.verticalHeader().setDefaultSectionSize(math.ceil(data_font_size*1.5))

class FileSelector(FileSelectorGUI):
    selection_changed = QtCore.pyqtSignal(DataPoint)
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        for k,v in kwargs:
            setattr(self, k, v)

    @property
    def database(self):
        return self.getMainPanel().database
    
    def clearData(self):
        """
        Clear data in the file selector,
        Keep no reference to the data of the database, for database to be savely deleted
        """
        self.data_model.assignData(DataList([]))
    
    def connectFuncs(self):
        self.data_view.selectionModel().currentChanged.connect(self.onRowChanged)
        self.data_view.doubleClicked.connect(self.doubleClickOnEntry)

        self.shortcut_delete_selection = QShortcut(QtGui.QKeySequence("Del"), self)
        self.shortcut_delete_selection.activated.connect(self.deleteCurrentSelected)
        self.shortcut_open_tagedit = QShortcut(QtGui.QKeySequence("Space"), self)
        self.shortcut_open_tagedit.activated.connect(self.editTagForThisSelection)

        self.search_bar.updateSearch.connect(self.loadValidData_async)

        self.act_sync_datapoint.triggered.connect(lambda: self.syncCurrentSelections_async())
        self.act_open_location.triggered.connect(self.openCurrFileLocation)
        self.act_copy_bib.triggered.connect(self.copyCurrentSelectionBib)
        self.act_copy_citation.triggered.connect(self.copyCurrentSelectionCitation)
        self.act_copy_uuid.triggered.connect(self.copyCurrentSelectionUUID)
        self.act_add_file.triggered.connect(lambda : self.addFileToCurrentSelection(fname = None))
        self.act_free_doc.triggered.connect(self.freeDocumentOfCurrentSelection)
        self.act_edit_bib.triggered.connect(self.editBibtex)
        self.act_delete_file.triggered.connect(self.deleteCurrentSelected)
        self.act_export_data.triggered.connect(self.exportData)
        self.act_summarize.triggered.connect(self.summarizeCurrentSelection)

        self.act_share_doc.triggered.connect(self.copyCurrentSelectionShareLink)

    def offlineStatus(self, status: bool):
        super().offlineStatus(status)
        disable_wids = [
            self.act_edit_bib,
            self.act_open_location,
            self.act_delete_file,
            self.act_add_file,
            self.act_free_doc,
            self.act_export_data,
            self.shortcut_delete_selection,
            # self.shortcut_open_tagedit,
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
        _only_one = len(selections) == 1
        def on_finish(success):
            self.setEnabled(True)   # Enable changing data selection when done
            if success and _only_one:
                # only one selection and sync successed, do
                self.offlineStatus(True)
                self.getInfoPanel().offlineStatus(True)
                self.getTagPanel().offlineStatus(True)
            callback_on_finish(success)

        self.setEnabled(False)      # Disable changing data selection when sync current selection
        self.getMainPanel().syncData_async(selections, on_finish)
        return 

    def loadValidData(
            self, 
            tags: DataTags, 
            from_uids: Optional[List[str]] = None, 
            sort_uids: Optional[List[str]] = None,
            hint = False
            ):
        """
        Load valid data by tags
        - tags: tags selected
        - from_uids: if not None, only load data from these uids, can be used to load data from search result
        - sort_uids: if not None, sort data by this order
        - hint: if True, print debug info
        """
        valid_data = self.getMainPanel().db.getDataByTags(tags, from_uids=from_uids)
        # if screen_pattern != "":
        #     valid_data = DataList([i for i in valid_data if i.screenByPattern(screen_pattern)])
        sort_method = getConf()["sort_method"]
        sort_reverse = getConf()["sort_reverse"]
        if sort_uids is not None:
            valid_data.sortBy(sort_uids, reverse=False)
        else:
            valid_data.sortBy(sort_method, reverse=sort_reverse)
        self.data_model.assignData(valid_data) 
        if hint:    # debuggin purpose
            screen_pattern = self.search_bar.text()
            self.logger.debug("Data loaded, tags: {tags}, sorting method: {sort_method}, screen_pattern: {screen_pattern}".\
                format(tags = " | ".join(tags), sort_method = sort_method, screen_pattern = screen_pattern))
        return True

    def loadValidData_async(self, callback: Callable[[bool], None] = lambda success: None):
        """
        Loads valid data by current search keyword and selected tags
        """
        def onFinish(signal):
            if signal["id"] != self.__working_search_id:
                # not updating the panel if the signal was not sent 
                # from the latest search worker
                callback(False)
                return
            res: StringSearchT = signal["res"]
            vaild_uids = cast(List[str], res.keys())

            # maybe create a temporary sort_uids here
            sort_uids = None
            if len(res)>0:
                _test_key = next(iter(res.keys()))  # get the first key, to determine if the res contains score
                _test_res_obj = res[_test_key]
                if _test_res_obj is not None and _test_res_obj["score"] is not None:
                    # if res contains score, sort by score
                    sort_uids = [i for i, _ in sorted(res.items(), key=lambda x: x[1]["score"], reverse=True)] # type: ignore

            self.loadValidData(
                tags = DataTags(getConf()["default_tags"]), 
                from_uids=vaild_uids,
                sort_uids=sort_uids
                )
            curr_data = self.getCurrentSelection()
            if not curr_data is None:
                self.selection_changed.emit(curr_data)
            callback(True)
        
        searcher = DataSearcher(self.database)
        self.search_bar.prepareSearcher(searcher)
        worker = SearchWorker(searcher)
        worker.signals.finished.connect(onFinish)
        self.__working_search_id = id(worker)
        self.thread_pool.start(worker)

    def reloadData(self):
        self.loadValidData_async()
    
    def openCurrFileLocation(self):
        curr_data = self.getCurrentSelection()
        if not curr_data is None:
            openFile(curr_data.fm.path)
    
    def editTagForThisSelection(self):
        """
        Edit tag for current selected single data entry,
        will sync before opening tag editor, if the data is not in local
        """
        def _openTagEditor(success_sync: bool):
            if success_sync:
                self.getTagPanel().openTagEditor()
        curr_data = self.getCurrentSelection(return_multiple=False)
        if curr_data:
            if curr_data.is_local:
                _openTagEditor(True)
            else:
                self.syncCurrentSelections_async(callback_on_finish=_openTagEditor)
    
    def copyCurrentSelectionBib(self):
        selected = self.getCurrentSelection(return_multiple=True)
        if not selected:
            self.logger.debug("Can't copy bib of selected: None")
            return
        bibs =[s.fm.readBib() for s in selected]  
        if len(bibs) > 1:
            bibs = ",\n".join(bibs)
        else:
            bibs = bibs[0]
        copy2clip("\""+bibs+"\"")

    def copyCurrentSelectionCitation(self):
        selected = self.getCurrentSelection(return_multiple=True)
        if not selected:
            self.logger.debug("Can't copy citation of selected: None")
            return
        citations = [x.stringCitation() for x in selected]
        copy2clip("\""+"\n".join(citations)+"\"")
    
    def copyCurrentSelectionShareLink(self):
        selected = self.getCurrentSelection(return_multiple=False)
        if not selected:
            return
        copy2clip(selected.getDocShareLink())
    
    def copyCurrentSelectionUUID(self):
        selected = self.getCurrentSelection(return_multiple=False)
        if not selected:
            return
        copy2clip(selected.uuid)
    
    def summarizeCurrentSelection(self):
        sel = self.getCurrentSelection(return_multiple=False)
        if not sel:
            return
        url = getServerURL() + "/summary" + "?uuid=" + sel.uuid + "&key=" + generateHexHash(getConf()["access_key"])
        webbrowser.open(url)

    def editBibtex(self):
        selected_ = self.getCurrentSelection(return_multiple=False)

        if selected_ is None:
            self.logger.debug("Can't edit bibtex of selected: None")
            return
        selected: DataPoint = selected_
        self.logger.debug("Editing bibtex for {}".format(selected.uuid))
        def onConfirm(txt: str):
            # self.infoDialog("Just make sure...", 
            #     "Please make sure no programs is using the file to avoid permission error. "\
            #     "(e.g. close the document before changing the bibtex)")

            try:
                success = selected.changeBib(txt)
            except PermissionError as e:
                # May occur if file is opened..
                # (should not be a problem after 0.12.0?)
                self.logger.debug(traceback.format_exc())
                if not self.database.offline:
                    self.warnDialogCritical("ERROR: {}".format(e), 
                    "Please restart the program to clean cache and don't sync before cache clean for data integrity. (Check log for more info)")
                else:
                    self.warnDialogCritical("ERROR: {}".format(e), 
                    "Please check data integrity manually. (check log for more info)")
                return
            if success:
                self.selection_changed.emit(selected)
                self.infoDialog("Success")
            else:
                self.warnDialog("Failed to change bibtex", "Please check log for more info")

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
            self.getInfoPanel().load(dp)
            QMessageBox.information(self, "Success", "File added")

    def addToDatabase(self, file_path:str):
        """ will be called by signal from bibQuery
        actual file manipulation is implemented in bibQuery
        """
        dp = self.getMainPanel().db.add(file_path)
        self.data_model.add(dp)
        sort_method = getConf()["sort_method"]
        sort_reverse = getConf()["sort_reverse"]
        self.data_model.sortBy(sort_method, reverse=sort_reverse)
    
    def _deleteFromDatabase(self, data: DataPoint):
        if data.uuid in self.getMainPanel().db.keys():
            res = self.getMainPanel().db.delete(data.uuid)
            if not res:
                self.warnDialog("Incomplete deletion", "Check log for more information")
    
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

    def exportData(self):
        selected = self.getCurrentSelection(return_multiple=True)
        if not selected:
            return
        dst = QFileDialog.getExistingDirectory(self, caption = "Choose destination")
        if not dst:
            return
        to_export_uids = []
        for dp in selected:
            to_export_uids.append(dp.uuid)
        self.database.exportFiles(to_export_uids, dst)
    
    def onRowChanged(self, current, previous):
        # self._info_panel.saveComments()
        row = current.row()
        data: DataPoint = self.data_model.datalist[row]

        # decide if un-saved comments
        if self.getInfoPanel().queryCommentSaveStatus() == "changed":
            self.statusBarInfo("You may have un-saved changes lost...", 3.5, bg_color = "red")
        # may fail because file may not be in local
        # sync with fm.setWatch(True) when finished is used to make sure files are watched
        self.logger.debug("Set watch to {} on selection row change".format(data.uuid))
        self.database.watchFileChange([data])   

        self.selection_changed.emit(data)       # info panel will change here
        self.offlineStatus(data.is_local)

    def doubleClickOnEntry(self):
        data = self.getCurrentSelection()
        def _open(dp: DataPoint):
            """
            Open a data point locally
            """
            if not self.keyModifiers("Alt"):
                if self.getMainPanel().openDocInternal(dp):
                    # Try to open in tab instead of using native apps
                    return
            self.getMainPanel().openDocExternal(dp)

        def _onSyncDone(success, to_open):
            if not success and G.last_status_code == 403:
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
        curr_total_tags = self.database.total_tags
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
        self.datalist: DataList = copy.deepcopy(datalist)
    
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
        self.datalist = DataList(datalist)
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

    def sortBy(self, sort_method: str, reverse: bool):
        """
        - sort_method: refer to static items in backend.dataClass.DataList
        """
        self.datalist.sortBy(sort_method, reverse = reverse)

    def add(self, dp: DataPoint):
        self.datalist.append(dp)
        self.layoutChanged.emit()
    
    def data(self, index: QtCore.QModelIndex, role):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return self.datalist.getTableItem(row = index.row(), col = index.column())
    
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = ...) -> typing.Any:
        if orientation == QtCore.Qt.Orientation.Horizontal:
            if role == QtCore.Qt.ItemDataRole.DisplayRole:
                title = getConf()["table_headers"][section]
                if title == DataTableList.HEADER_FILESTATUS:
                    title = ""
                return title
        return super().headerData(section, orientation, role)

    def rowCount(self, parent: QtCore.QModelIndex) -> int:
        return len(self.datalist)
    
    def columnCount(self, parent: QtCore.QModelIndex) -> int:
        return len(getConfV("table_headers"))

class FileTableView(QTableView, LazyResizeMixin):
    # How to highlight entire row on hovering? - https://stackoverflow.com/a/46231218/6775765
    # https://stackoverflow.com/questions/4031168/qtableview-is-extremely-slow-even-for-only-3000-rows
    # https://stackoverflow.com/questions/38098763/pyside-pyqt-how-to-make-set-qtablewidget-column-width-as-proportion-of-the-a
    hoverIndexChanged = QtCore.pyqtSignal(QtCore.QModelIndex)
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.ActionsContextMenu)
        self.setAutoScroll(False)
        self.resize_timer.setInterval(50)
        self.reset_timer = QtCore.QTimer()
        self.reset_timer.setInterval(50)
        self.reset_timer.setSingleShot(True)
        self.reset_timer.timeout.connect(self.reset)

    def initSettings(self):
        self.header = self.horizontalHeader()       
        self.header.setVisible(True)
        self.header.setMinimumSectionSize(10)
        self._init_headerResizeMode(fast = True)
        self._init_headerSize()
        # self._init_headerTitle()
    
    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        return super().paintEvent(e)
        if self.resize_timer.isActive():
            return
        else:
            return super().paintEvent(e)
    
    @property
    def table_headers(self) -> List[str]:
        return getConf()["table_headers"]
    
    def delayed_update(self):
        # self.reset()
        self.update()
    
    def _init_headerResizeMode(self, fast: bool = False):
        for i in range(len(self.table_headers)):
            if getConfV("table_headers")[i] == DataTableList.HEADER_TITLE:
                self.header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.Stretch)
            else:
                if not fast:
                    self.header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)    # This is slow
                else:
                    self.header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.Interactive)
        
    def _init_headerSize(self):
        self.header.setDefaultSectionSize(120)
        for i in range(len(self.table_headers)):
            if getConfV("table_headers")[i] == DataTableList.HEADER_FILESTATUS:
                self.header.resizeSection(i, 20)
            if getConfV("table_headers")[i] == DataTableList.HEADER_YEAR:
                self.header.resizeSection(i, 50)

    def mouseMoveEvent(self, e: QtGui.QMouseEvent) -> None:
        index = self.indexAt(e.pos())
        self.hoverIndexChanged.emit(index)
        return super().mouseMoveEvent(e)
    
    def wheelEvent(self, a0: QtGui.QWheelEvent) -> None:
        selected_indexes = self.selectedIndexes()
        selected_rows = set([idx.row() for idx in selected_indexes])
        if not len(selected_rows) > 1:
            # force update highlighting
            # not to do so when multiple rows are selected
            self.reset_timer.start()
        return super().wheelEvent(a0)

class FileTableDelegate(QStyledItemDelegate):
    # hover_color = QColor(100 , 200, 200, 100) 
    # select_color = QColor(0 , 100, 200, 100) 
    def __init__(self, parent: typing.Optional[QtCore.QObject] = None) -> None:
        super().__init__(parent)
        self.hoverrow_ = None
        self.selectrow_ = None

    def onHoverIndexChanged(self, index: QtCore.QModelIndex):
        self.hoverrow_ = index.row()

    def onSelectionIndexChanged(self, index: QtCore.QModelIndex):
        self.selectrow_ = index.row()

    def paint(self, painter: QtGui.QPainter, option: QStyleOptionViewItem, index: QtCore.QModelIndex) -> None:
        if index.row() == self.hoverrow_:
            # painter.fillRect(option.rect, self.hover_color)
            option.state |= QStyle.StateFlag.State_MouseOver
        else:
            option.state &= ~QStyle.StateFlag.State_MouseOver

        # if index.row() == self.selectrow_:
        #     painter.fillRect(option.rect, self.select_color)
        return super().paint(painter, option, index)
