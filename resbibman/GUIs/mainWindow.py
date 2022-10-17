import pyperclip
from typing import Tuple, List, Callable
from PyQt6 import QtGui
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut
from PyQt6.QtWidgets import QDialog, QFileDialog, QMainWindow, QMenu, QMenuBar, QSplitter, QWidget, QHBoxLayout, QFrame, QToolBar, QSizePolicy
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QThreadPool

from .widgets import RefWidgetBase
from .fileInfo import FileInfo
from .fileTags import FileTag
from .fileSelector import FileSelector
from .bibQuery import BibQuery
from .pendingWindow import PendingWindow
from .settings import SettingsWidget
from .guiInteractions import ChoicePromptGUI
from .helpWidget import HelpWidget
from ._styleUtils import qIconFromSVG_autoBW, isThemeDarkMode

from ..core.fileTools import FileGenerator
from ..core.fileToolsV import FileManipulatorVirtual
from ..core.bibReader import BibParser, BibConverter
from ..core.utils import openFile, ProgressBarCustom
from ..core.dataClass import DataTags, DataBase, DataPoint
from ..confReader import getConf, ICON_PATH, getConfV, getDatabase, saveToConf_guiStatus
from ..confReader import TMP_DB, TMP_WEB, TMP_COVER
from ..version import VERSION
from ..perf.qtThreading import SyncWorker, InitDBWorker
import os, copy, typing, requests, functools, time, shutil

class MainWindowGUI(QMainWindow, RefWidgetBase):
    menu_bar: QMenuBar
    toolbars: List[QToolBar]

    def __init__(self):
        super().__init__()
        self.db = DataBase()
        self._panel_status = (True, True, True)

        self._cache: dict = {
            "current_layout": (True, True, True),
            "prev_layout": (True, True, True)
        }

        self.initUI()
        self.showMaximized()
        self.show() 
    
    def initUI(self):
        self.setWindowTitle("Research bib manager")
        self.setWindowIcon(QIcon(os.path.join(ICON_PATH, "resbibman-icon.png")))
        self._initPanels()
        self._createActions()
        self._createMenuBar()
        self._createToolBars()

        self.status_bar = self.statusBar()

        hbox = QHBoxLayout()
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.file_tags)
        self.splitter.addWidget(self.file_selector)
        self.splitter.addWidget(self.file_info)
        #  self.splitter.setStretchFactor(0,1)
        #  self.splitter.setStretchFactor(1,4)
        #  self.splitter.setStretchFactor(2,2)
        self.toggleLayout(self._panel_status)
        hbox.addWidget(self.splitter)

        wid = QWidget(self)
        self.setCentralWidget(wid)
        wid.setLayout(hbox)
        # self._center()

    def toggleLayout(self, toggle_mask: Tuple[bool, bool, bool]):
        # Record this to be used by toggleFullScreen
        self._cache["prev_layout"] = self._cache["current_layout"]
        self._cache["current_layout"] = toggle_mask

        # Calculate width
        stretch_factor = [1, 4, 2]                  # default stretch factor
        stretch_factor = [ toggle_mask[i]*stretch_factor[i] for i in range(3) ]
        stretch_factor = [ float(f)/sum(stretch_factor) for f in stretch_factor ]
        curr_width = self.frameGeometry().width()
        w_sizes = [ int(curr_width*f) for f in stretch_factor]
        self.splitter.setSizes(w_sizes)
        self.logger.debug("Set sizes to {}".format(w_sizes))
        return 

    def toggleFullScreen(self):
        self.logger.debug("Toggle full screen")
        if self.isFullScreen():
            self.showNormal()
            self.toggleLayout(self._cache["prev_layout"])
        else:
            self.showFullScreen()
            self.toggleLayout((True, True, True))
    
    def _initPanels(self):
        self.file_tags = FileTag(self)
        self.file_info = FileInfo(self)
        self.file_selector = FileSelector(self)

        self.setMainPanel(self)
        self.setInfoPanel(self.file_info)
        self.setSelectPanel(self.file_selector)
        self.setTagPanel(self.file_tags)

        self.file_tags.setMainPanel(self)
        self.file_tags.setInfoPanel(self.file_info)
        self.file_tags.setSelectPanel(self.file_selector)

        self.file_info.setMainPanel(self)
        self.file_info.setTagPanel(self.file_tags)
        self.file_info.setSelectPanel(self.file_selector)

        self.file_selector.setMainPanel(self)
        self.file_selector.setInfoPanel(self.file_info)
        self.file_selector.setTagPanel(self.file_tags)

        # connect after initialization because we have inter-refernce between these widgets
        self.file_info.connectFuncs()
        self.file_selector.connectFuncs()
        self.file_tags.connectFuncs()
    
    def _createActions(self):
        self.act_file_additem = QAction("&Add paper", self)
        self.act_file_additem.setIcon(qIconFromSVG_autoBW(os.path.join(ICON_PATH, "addfile-24px.svg")))

        self.act_opendb = QAction("&Open database", self)
        self.act_opendb.setIcon(qIconFromSVG_autoBW(os.path.join(ICON_PATH, "folder-24px.svg")))

        self.act_settings = QAction("&Settings", self)
        self.act_settings.setIcon(qIconFromSVG_autoBW(os.path.join(ICON_PATH, "settings-24px.svg")))

        self.act_help = QAction("&Info", self)
        self.act_help.setIcon(qIconFromSVG_autoBW(os.path.join(ICON_PATH, "info-24px.svg")))

        self.act_reload = QAction("&Reload/Synchronize", self)
        self.act_reload.setShortcut(QKeySequence("ctrl+r"))
        self.act_reload.setIcon(qIconFromSVG_autoBW(os.path.join(ICON_PATH, "refresh-24px.svg")))

        self.act_open_pdb = QAction("&Pending data", self)
        self.act_open_pdb.setIcon(qIconFromSVG_autoBW(os.path.join(ICON_PATH, "hourglass_bottom_black_24dp.svg")))

        self.act_importbib_from_clip = QAction("Import bib from clipboard", self)
        self.act_importbib_from_clip.setIcon(qIconFromSVG_autoBW(os.path.join(ICON_PATH, "paste-24px.svg")))
        self.act_importbib_from_clip.setShortcut(QKeySequence("ctrl+shift+alt+i"))

        self.act_show_toolbar = QAction("&Show tool bar", self)
        self.act_show_toolbar.setCheckable(True)
        self.act_show_toolbar.setShortcut(QKeySequence("ctrl+t"))

        self.act_show_panel1 = QAction("&Show panel 1", self)
        self.act_show_panel1.setIcon(qIconFromSVG_autoBW(os.path.join(ICON_PATH, "looks_one_black_48dp.svg")))
        self.act_show_panel2 = QAction("&Show panel 2", self)
        self.act_show_panel2.setIcon(qIconFromSVG_autoBW(os.path.join(ICON_PATH, "looks_two_black_48dp.svg")))
        self.act_show_panel3 = QAction("&Show panel 3", self)
        self.act_show_panel3.setIcon(qIconFromSVG_autoBW(os.path.join(ICON_PATH, "looks_3_black_48dp.svg")))
        self.act_toggle_fullscreen = QAction("&full screen", self)
        self.act_toggle_fullscreen.setIcon(qIconFromSVG_autoBW(os.path.join(ICON_PATH, "fullscreen_black_48dp.svg")))
        self.act_toggle_fullscreen.setShortcut(QKeySequence("ctrl+f"))
        #  self.act_toggle_fullscreen.setShortcut(Qt.Key_F11)

    def _createMenuBar(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        files_menu = QMenu("&Files", self)
        menu_bar.addMenu(files_menu)
        files_menu.addAction(self.act_file_additem)
        files_menu.addAction(self.act_importbib_from_clip)
        files_menu.addAction(self.act_opendb)
        files_menu.addAction(self.act_open_pdb)
        files_menu.addAction(self.act_reload)

        view_menu = QMenu("&View", self)
        menu_bar.addMenu(view_menu)
        view_menu.addAction(self.act_show_toolbar)
        view_menu.addAction(self.act_toggle_fullscreen)
        view_menu.addAction(self.act_show_panel1)
        view_menu.addAction(self.act_show_panel2)
        view_menu.addAction(self.act_show_panel3)

        settings_menu = QMenu("&Settings", self)
        menu_bar.addMenu(settings_menu)
        settings_menu.addAction(self.act_settings)

        help_menu = QMenu("&Help", self)
        menu_bar.addMenu(help_menu)
        help_menu.addAction(self.act_help)
    
    def _createToolBars(self):
        tool_bar = QToolBar("Toolbar")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, tool_bar)
        tool_bar.addAction(self.act_file_additem)
        tool_bar.addAction(self.act_importbib_from_clip)
        tool_bar.addAction(self.act_opendb)
        tool_bar.addAction(self.act_settings)
        tool_bar.addAction(self.act_help)
        tool_bar.addAction(self.act_reload)
        
        file_bar = QToolBar("Filebar")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, file_bar)
        file_bar.addAction(self.act_open_pdb)

        panel_bar = QToolBar("Panels")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, panel_bar)
        panel_bar.addAction(self.act_toggle_fullscreen)
        panel_bar.addAction(self.act_show_panel1)
        panel_bar.addAction(self.act_show_panel2)
        panel_bar.addAction(self.act_show_panel3)

        self.toolbars = [tool_bar, file_bar, panel_bar]

    def toggleShowToobar(self, status: bool):
        for bar in self.toolbars:
            bar.setVisible(status)
        saveToConf_guiStatus(show_toolbar = status)
    
class MainWindow(MainWindowGUI):
    def __init__(self):
        super().__init__()
        self.pool = QThreadPool.globalInstance()
        self.logger.debug("Configuration: ")
        self.logger.debug(getConf())
        self.initActions()
        self.initGUIStatusConfig()
        self.reloadData()
    
    @property
    def database(self):
        return self.db

    def initActions(self):
        self.act_settings.triggered.connect(self.openSettingsDialog)
        self.act_opendb.triggered.connect(self.openDataBaseDir)
        self.act_help.triggered.connect(lambda: HelpWidget(self).show())
        self.act_file_additem.triggered.connect(self.openAddfileSelectionDialog)
        self.act_reload.triggered.connect(self.reloadData)
        self.act_open_pdb.triggered.connect(self.openPendingWindow)

        self.act_importbib_from_clip.triggered.connect(self.importEntryFromClipboardBib)

        self.act_show_toolbar.triggered.connect(self.toggleShowToobar)
        self.act_show_panel1.triggered.connect(lambda: self.toggleOnlyPanel(0))
        self.act_show_panel2.triggered.connect(lambda: self.toggleOnlyPanel(1))
        self.act_show_panel3.triggered.connect(lambda: self.toggleOnlyPanel(2))
        self.act_toggle_fullscreen.triggered.connect(self.toggleFullScreen)

    def initGUIStatusConfig(self):
        gui_conf = getConfV("gui_status")
        self.act_show_toolbar.setChecked(gui_conf["show_toolbar"])
        self.toggleShowToobar(gui_conf["show_toolbar"])

    def toggleOnlyPanel(self, idx: int):
        """
        To only show one panel
        """
        assert 0<=idx<3
        # Determine if this is the only panel that is showing
        ONLY_THIS = True
        if not self._cache["current_layout"][idx]:
            ONLY_THIS = False
        else:
            other_panel_idx = [i for i in range(3) if i != idx]
            for other_idx in other_panel_idx:
                if self._cache["current_layout"][other_idx]:
                    ONLY_THIS = False
                    break
        if ONLY_THIS:
            self.toggleLayout((True, True, True))
            return
        else:
            to_toggle = [False, False, False]
            to_toggle[idx] = True
            self.toggleLayout(tuple(to_toggle))
            return

    def togglePanel(self, idx:int):
        """
        Toggle a panel on/off
        """
        assert 0<=idx<3
        status = list(self._panel_status)
        s = status[idx]
        if s: status[idx] = False
        else: status[idx] = True

        # If close all panels, enable all
        ALL_CLOSE = True
        for s_ in status:
            if s_ is True:
                ALL_CLOSE = False
                break
        if ALL_CLOSE:
            status = [True, True, True]

        self._panel_status = tuple(status)
        return self.toggleLayout(self._panel_status)
    
    def _loadData(self, data_path):
        """Deprecated"""
        self.db = DataBase()
        if getConf()["host"] != "":
            # Online mode
            self.statusBarInfo("Requesting remote server", bg_color = "blue")
        self.db.init(data_path)
        self.file_selector.loadValidData(DataTags(getConf()["default_tags"]), hint = True)
        self.file_tags.initTags(self.getTotalTags())
        self.statusBarInfo("Success", 2, bg_color = "green")

    def loadData_async(self, data_path, sync_after = False):
        """
         - data_path: local database path
         - sync_after: call self.syncData_async after loading data
        """

        def _on_done(success, set_offline_mode: bool):
            """
            Load data into GUI, update status bar
            """
            self.setEnabled(True)
            self.file_selector.loadValidData(DataTags(getConf()["default_tags"]), hint = True)
            self.file_tags.initTags(self.getTotalTags())
            if success or set_offline_mode:
                if sync_after:
                    self.statusBarInfo("Data loaded", 2, bg_color = "green")
                else:
                    self.statusBarInfo("Data loaded", 2, bg_color = "blue")
            else:
                self.statusBarInfo("Error connection", 2, bg_color = "red")
            
            if success and sync_after:
                # sync datapoint (local) if any
                to_sync = [dp for uuid, dp in self.db.items() if dp.is_local]
                self.syncData_async(to_sync)
            return 

        # -----Start from here-----
        self.setEnabled(False)
        self.statusBar().setEnabled(True)

        self.db = DataBase()
        is_offline = getConf()["database"] == data_path
        if not is_offline:
            # Online mode
            self.statusBarInfo("Requesting remote server...", bg_color = "blue")
            on_done = functools.partial(_on_done, set_offline_mode = False)
        else:
            self.statusBarInfo("Loading...", bg_color = "blue")
            on_done = functools.partial(_on_done, set_offline_mode = True)

        worker = InitDBWorker(self.db, data_path, force_offline = is_offline)
        worker.signals.finished.connect(on_done)
        self.pool.start(worker)

    def getCurrentSelection(self)->typing.Union[None, DataPoint]:
        return self.file_selector.getCurrentSelection()
    
    def getCurrentSelectedTags(self)->DataTags:
        tags = self.file_tags.tag_selector.getSelectedTags()
        return tags
    
    def getTotalTags(self) -> DataTags:
        tags = DataTags([])
        for d in self.db.values():
            tags = tags.union(d.tags)
        return tags
    
    def refreshFileTagSelector(self, *args):
        self.file_tags.initTags(self.getTotalTags())

    def _center(self):
        qr = self.frameGeometry()
        cp = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def openSettingsDialog(self):
        self.set_win = QDialog()
        self.set_win.setWindowTitle("Settings")
        box = QHBoxLayout()

        self.set_wid = SettingsWidget(self.set_win)
        self.set_wid.setMainPanel(self)
        self.set_wid.setInfoPanel(self.file_info)
        self.set_wid.setTagPanel(self.file_tags)
        self.set_wid.setSelectPanel(self.file_selector)
        self.set_wid.init()

        box.addWidget(self.set_wid)
        self.set_win.setLayout(box)
        self.set_win.show()
    
    def openDataBaseDir(self):
        if getConf()["host"]:
            database = TMP_DB
        else:
            database = getConf()["database"]
        openFile(database)
    
    def openAddfileSelectionDialog(self):
        bib_extensions = [".bib", ".nbib"]
        extensions = getConf()["accepted_extensions"] + bib_extensions
        extension_filter = "({})".format(" ".join(["*"+i for i in extensions]))
        fname = QFileDialog.getOpenFileName(self, caption="Select papers", filter=extension_filter)[0]
        self.addFilesToDatabaseByURL([fname])
    
    def importEntryFromClipboardBib(self):
        """Only support one bib now"""
        raw_text = pyperclip.paste()
        self.addFileToDataBaseByBib(raw_text)
    
    def addFilesToDatabaseByURL(self, urls: typing.List[str]):
        curr_selected_tags = self.getCurrentSelectedTags()
        curr_total_tags = self.getTotalTags()
        for f in urls:
            # if bib file
            if f.endswith(".bib"):
                with open(f) as fp:
                    self.addFileToDataBaseByBib(fp.read())
                continue
            # if nbib file
            elif f.endswith(".nbib"):
                converter = BibConverter()
                with open(f) as fp:
                    nb = fp.read().strip("\n ") + "\n"
                    bb = converter.fromNBib(nb)
                    self.addFileToDataBaseByBib(bb)
                continue

            # else open bib_quary GUI
            elif f == "":
                self.bib_quary = BibQuery(self, None, tag_data=curr_selected_tags, tag_total=curr_total_tags)
            else:
                self.bib_quary = BibQuery(self, f, tag_data=curr_selected_tags, tag_total=curr_total_tags)
            self.bib_quary.setDatabase(self.db)     # Set database for inspect if file already exists
            self.bib_quary.file_added.connect(self.file_selector.addToDatabase)
            self.bib_quary.file_added.connect(self.refreshFileTagSelector)
            self.bib_quary.add_to_pending.connect(self.openPendingWindowAndAddPendingFile)
            if hasattr(self, "pending_win"):
                self.bib_quary.file_added.connect(self.pending_win.loadData)
            self.bib_quary.show()
    
    def addFileToDataBaseByBib(self, bib_str: str):
        tag_list = self.file_tags.tag_selector.getSelectedTags().toOrderedList()
        parser = BibParser(mode = "single")
        try:
            bibs = parser(bib_str)
            bib = bibs[0]
        except:
            self.warnDialog("Invalid clipboard content: ", bib_str)
            return
        if len(bibs) > 1:
            self.warnDialog("Failed - Currently, only one file import is supported")
            return

        sim_bib = self.db.findSimilarByBib(bib_str)
        if isinstance(sim_bib, DataPoint):
            query_strs= [
                "File may exists already",
                "{year} - {title}".format(year = sim_bib.bib["year"], title = sim_bib.bib["title"]),
                "FROM: {authors}".format(authors = "|".join(sim_bib.bib["authors"])),
                "Add anyway?"
            ]
            if not self.queryDialog(title = "File may exist", msg = "\n".join(query_strs)):
                return


        fg = FileGenerator(
            file_path = None,
            title = bib["title"],
            year = bib["year"],
            authors = bib["authors"]
        )
        if not fg.generateDefaultFiles(getDatabase(self.db.offline)):
            return 
        dst_dir = fg.dst_dir
        fm = FileManipulatorVirtual(dst_dir)
        fm.screen()
        fm.writeBib(bib_str)
        fm.writeTags(tag_list)
        del fm
        self.reloadData()
    
    def openPendingWindowAndAddPendingFile(self, url: str):
        if hasattr(self, "pending_win"):
            self.pending_win.show()
        else:
            self.openPendingWindow()
        self.pending_win.addFilesToPendingDataBaseByURL([url])

    def openPendingWindow(self):
        self.pending_win = PendingWindow()
        self.pending_win.setMainPanel(self)
        self.pending_win.show()

    def syncData_async(self, to_sync: List[DataPoint], callback_on_finish: Callable[[bool], None] = lambda _: None):
        """
        To synchronize with remote server, i.e. DataPoint.sync()
         -  callback_on_finish: additional callback to be called when sync is finished
        """
        n_total = len(to_sync)
        def showProgress(to_show):
            self.statusBarInfo(f"Sync with remote: {to_show}", bg_color = "blue")
        progress_bar = ProgressBarCustom(n_total, showProgress)
        on_start = lambda: self.statusBarInfo(f"Sync with remote", bg_color = "blue")
        on_middle = lambda status_code: progress_bar.next()
        def on_finish(success):
            if success:
                self.statusBarInfo("Successfully synchronized", 5, bg_color = "green")
            else:
                self.statusBarInfo("Failed synchronize, check log", 5, bg_color = "red")

            in_info_dp = self.getInfoPanel().curr_data
            if in_info_dp is not None:
                # Watch info panel data in case of note change
                ## unzip file is somewhat asynchronous (in MacOS?), 
                ## thus file creation may come after watching
                ## sleep to avoid logging file creation
                time.sleep(0.5)     
                in_info_dp.fm.setWatch(True)
        # before start sync, make sure that all datapoint are using GUI for user prompt
        prompt_obj = ChoicePromptGUI()
        for dp in to_sync:
            dp.setPromptObj(prompt_obj)
        sync_worker = SyncWorker(to_sync)
        sync_worker.signals.started.connect(on_start)
        sync_worker.signals.on_chekpoint.connect(on_middle)
        sync_worker.signals.finished.connect(on_finish)
        sync_worker.signals.finished.connect(callback_on_finish)
        threadCount = QThreadPool.globalInstance().maxThreadCount()
        self.logger.debug(f"Running {threadCount} Threads")
        self.pool.start(sync_worker)

    def reloadData(self):
        """
        Reload database,
        Will synchronize add data if in online mode
        """
        if getConf()["host"]:
            try:
                # reload server
                addr = "http://{}:{}".format(getConfV("host"), getConfV("port"))
                req_reloadDB = addr + "/cmd/reloadDB"
                res = requests.get(req_reloadDB, timeout = 5)
                # loadData
                self.loadData_async(TMP_DB, sync_after=True)    # (This will not raise an ConnectionError)
                # self._loadData(TMP_DB)
                # sync local with remote
                #  to_sync = [dp for uuid, dp in self.db.items() if dp.is_local]
                #  self.syncData_async(to_sync)
            except requests.exceptions.ConnectionError:
                self.statusBarInfo("Connection error", 5, bg_color = "red")
                self.logger.warning("Server is down, not reload server.")
                self.logger.debug("May fall into offline mode.")
                self.loadData_async(getConf()["database"], sync_after=False)
        else:
            # local dir
            self.loadData_async(getConf()["database"], sync_after=False)
            #  self._loadData(getConf()["database"])
        curr_dp = self.getCurrentSelection()
        if curr_dp is not None:
            self.file_info.load(curr_dp)
        else:
            self.file_info.clearPanel()
        
    def statusBarMsg(self, msg: str, bg_color = "none"):
        if self.db.offline:
            prefix = "ResBibMan-v{} (offline): ".format(VERSION)
        else:
            prefix = "ResBibMan-v{} (online): ".format(VERSION)
        if not isThemeDarkMode():
            font_color = "rgba(0,0,0,255)"
        else:
            font_color = "rgba(255,255,255,255)"
        color = {
            "none" : "QStatusBar{background:rgba(0,0,0,0); color: " + font_color + "}",
            "red" : "QStatusBar{background:rgba(255,0,0,150); color: rgba(255,255,255,255)}",
            "green" : "QStatusBar{background:rgba(0,200,0,150); color:" + font_color + "}",
            "blue" : "QStatusBar{background:rgba(0,0,255,150); color: rgba(255,255,255,255)}",
        }
        self.statusBar().setStyleSheet(color[bg_color])
        # self.statusBar().setStyleSheet(f"color : {txt_color}")
        self.statusBar().showMessage(prefix + msg)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.logger.debug("Closing...")
        # Check if all uptodate
        if not self.database.allUptodate(fetch = False, strict = True):
            if self.queryDialog("There are un-synchronized data, sync now?"):
                self.reloadData()
                # Not close window
                a0.ignore()
                return

        if self.database.offline:
            return super().closeEvent(a0)

        self.logger.info("Deleting cache")
        # unwatch all file, as they are going to be deleted
        self.database.watchFileChange([])   
        for p in [TMP_DB, TMP_WEB, TMP_COVER]:
            if os.path.exists(p):
                shutil.rmtree(p)
        return super().closeEvent(a0)
