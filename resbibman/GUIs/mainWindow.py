import pyperclip
from typing import Literal, Tuple, List, Callable
from PyQt6 import QtGui
from PyQt6.QtGui import QIcon, QKeySequence
from PyQt6.QtWidgets import QDialog, QFileDialog, QMainWindow, QMenu, QMenuBar, QSplitter, QWidget, QHBoxLayout, QToolBar, QTabWidget, QTabBar, QApplication
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QThreadPool

from .widgets import RefWidgetBase
from .fileInfo import FileInfo
from .fileTags import FileTag
from .fileSelector import FileSelector
from .docReader import DocumentReader
from .bibQuery import BibQuery
from .pendingWindow import PendingWindow
from .settings import SettingsWidget
from .guiInteractions import ChoicePromptGUI
from .tagModifer import TagModifier
from .helpWidget import HelpWidget
from ._styleUtils import qIconFromSVG_autoBW, isThemeDarkMode

from ..core.fileTools import addDocument
from ..core.fileToolsV import FileManipulatorVirtual
from ..core.bibReader import BibParser, BibConverter
from ..core.utils import openFile, ProgressBarCustom
from ..core.serverConn import ServerConn
from ..core.dataClass import DataTags, DataBase, DataPoint
from ..confReader import getConf, ICON_PATH, getConfV, getDatabase, saveToConf, saveToConf_guiStatus
from ..confReader import TMP_DB, TMP_WEB, TMP_COVER, getStyleSheets
from ..version import VERSION
from ..perf.qtThreading import SyncWorker, InitDBWorker
import os, typing, requests, functools, time, shutil, traceback, webbrowser

class MainTabWidget(QTabWidget, RefWidgetBase):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setTabsClosable(True)

        # a list of tabs except the first one
        self._tabs: List[QWidget] = []
        self._now_tab_idx = None

        self.tabCloseRequested.connect(self.closeTab)
        self.currentChanged.connect(self.onTabChange)

    def switchToExistingTab(self, uid: str) -> bool:
        """
        return if find the designated tab
        """
        for i in range(len(self._tabs)):
            tab = self._tabs[i]
            if isinstance(tab, DocumentReader):
                if tab.doc_uid == uid:
                    self.setCurrentIndex(i+1)
                    return True
        return False

    def addDocReader(self, reader: DocumentReader, name: str):
        self.addTab(reader, name)
        self._tabs.append(reader)
        self.setCurrentIndex(self.count()-1)

    def onTabChange(self, idx: int):
        self.logger.debug(f"Switching to tab: {idx}")
        if idx<0:
            return
        if self._now_tab_idx is not None:
            self.onLeaveTab(self._now_tab_idx)

        # Reload info panel in case comments change
        if idx == 0:
            # Mainwindow
            self.getInfoPanel().reload()
        else:
            wid = self._tabs[idx-1]
            if isinstance(wid, DocumentReader):
                wid.maybeInitSpliterSize()
                wid.info_panel.reload()
        self._now_tab_idx = idx

    def onLeaveTab(self, idx: int):
        # maybe save unsaved comments
        if idx == 0:
            # mainWindow
            self.getInfoPanel()._saveComments()
        else:
            for wid in self._tabs:
                if isinstance(wid, DocumentReader):
                    wid.info_panel._saveComments()

    def closeTab(self, idx: int):
        self.logger.debug(f"Closing tab: {idx}")
        if idx == 0:
            self.infoDialog("Don't close me :)", "Close the application if you want to quit")
            return
        self.removeTab(idx)
        _idx = idx-1
        wid = self._tabs[_idx]
        wid.deleteLater()
        self._tabs.pop(_idx)

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
        self.toggleLayout(self._panel_status)
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
        hbox.addWidget(self.splitter)

        main_wid = QWidget(self)
        main_wid.setLayout(hbox)

        self.tab_wid = MainTabWidget(self)
        self.passRefTo(self.tab_wid)
        self.tab_wid.addTab(main_wid, "HOME")
        self.setCentralWidget(self.tab_wid)
        # self._center()

        self.loadFontConfig()

    def toggleLayout(self, toggle_mask: Tuple[bool, bool, bool]):
        # Record this to be used by toggleFullScreen
        self._cache["prev_layout"] = self._cache["current_layout"]
        self._cache["current_layout"] = toggle_mask

        # Calculate width
        stretch_factor = [3, 10, 3]                  # default stretch factor
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

        # Set reference, this is a bit tricky, for type checking
        _self_cast = typing.cast(MainWindow, self)

        self.setMainPanel(_self_cast)
        self.setInfoPanel(self.file_info)
        self.setSelectPanel(self.file_selector)
        self.setTagPanel(self.file_tags)

        self.file_tags.setMainPanel(_self_cast)
        self.file_tags.setInfoPanel(self.file_info)
        self.file_tags.setSelectPanel(self.file_selector)

        self.file_info.setMainPanel(_self_cast)
        self.file_info.setTagPanel(self.file_tags)
        self.file_info.setSelectPanel(self.file_selector)

        self.file_selector.setMainPanel(_self_cast)
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

        self.act_fontsize_increase = QAction("&Increase font size", self)
        self.act_fontsize_increase.setShortcut(QKeySequence("ctrl+="))
        self.act_fontsize_increase.setIcon(qIconFromSVG_autoBW(os.path.join(ICON_PATH, "font-size-increase.svg")))
        self.act_fontsize_decrease = QAction("&Decrease font size", self)
        self.act_fontsize_decrease.setShortcut(QKeySequence("ctrl+-"))
        self.act_fontsize_decrease.setIcon(qIconFromSVG_autoBW(os.path.join(ICON_PATH, "font-size-decrease.svg")))

        self.act_show_panel1 = QAction("&Show panel 1", self)
        self.act_show_panel1.setIcon(qIconFromSVG_autoBW(os.path.join(ICON_PATH, "looks_one_black_48dp.svg")))
        self.act_show_panel1.setShortcut(QKeySequence("ctrl+1"))
        self.act_show_panel2 = QAction("&Show panel 2", self)
        self.act_show_panel2.setIcon(qIconFromSVG_autoBW(os.path.join(ICON_PATH, "looks_two_black_48dp.svg")))
        self.act_show_panel2.setShortcut(QKeySequence("ctrl+2"))
        self.act_show_panel3 = QAction("&Show panel 3", self)
        self.act_show_panel3.setIcon(qIconFromSVG_autoBW(os.path.join(ICON_PATH, "looks_3_black_48dp.svg")))
        self.act_show_panel3.setShortcut(QKeySequence("ctrl+3"))
        self.act_toggle_fullscreen = QAction("&full screen", self)
        self.act_toggle_fullscreen.setIcon(qIconFromSVG_autoBW(os.path.join(ICON_PATH, "fullscreen_black_48dp.svg")))
        self.act_toggle_fullscreen.setShortcut(QKeySequence("ctrl+f"))
        #  self.act_toggle_fullscreen.setShortcut(Qt.Key_F11)

        self.act_tool_renametag = QAction("&Rename tag", self)
        self.act_tool_deletetag = QAction("&Delete tag", self)

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

        tool_menu = QMenu("&Tools", self)
        menu_bar.addMenu(tool_menu)
        tool_menu.addAction(self.act_tool_renametag)
        tool_menu.addAction(self.act_tool_deletetag)

        settings_menu = QMenu("&Settings", self)
        menu_bar.addMenu(settings_menu)
        settings_menu.addAction(self.act_settings)
        settings_menu.addAction(self.act_fontsize_increase)
        settings_menu.addAction(self.act_fontsize_decrease)

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

    def loadFontConfig(self):
        font_config = getConf()["font_sizes"]
        self.file_selector.applyFontConfig(font_config)
        self.file_tags.applyFontConfig(font_config)

    def fontSizeStep1(self, mode: Literal["increase", "decrease"] = "increase"):
        self.logger.debug(f"{mode} font size by 1")
        font_config = getConf()["font_sizes"]
        new_font_config = font_config.copy()
        for k in ["data", "tag"]:
            old_font = font_config[k]
            list_font = list(old_font)
            if mode == "increase":
                list_font[1] += 1
            elif mode == "decrease":
                list_font[1] -= 1
            else:
                raise ValueError("Invalid mode in function: fontSizeStep1")
            new_font = tuple(list_font)
            new_font_config[k] = new_font
        self.file_selector.applyFontConfig(new_font_config)
        self.file_tags.applyFontConfig(new_font_config)
        saveToConf(font_sizes = new_font_config)

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
        self.act_fontsize_increase.triggered.connect(lambda: self.fontSizeStep1(mode = "increase"))
        self.act_fontsize_decrease.triggered.connect(lambda: self.fontSizeStep1(mode = "decrease"))
        self.act_show_panel1.triggered.connect(lambda: self.toggleOnlyPanel(0))
        self.act_show_panel2.triggered.connect(lambda: self.toggleOnlyPanel(1))
        self.act_show_panel3.triggered.connect(lambda: self.toggleOnlyPanel(2))
        self.act_toggle_fullscreen.triggered.connect(self.toggleFullScreen)

        self.act_tool_renametag.triggered.connect(lambda: TagModifier(self).promptRenameTag())
        self.act_tool_deletetag.triggered.connect(lambda: TagModifier(self).promptDeleteTag())

    def initGUIStatusConfig(self):
        gui_conf = getConfV("gui_status")
        self.act_show_toolbar.setChecked(gui_conf["show_toolbar"])
        self.toggleShowToobar(gui_conf["show_toolbar"])

    def openDocInternal(self, dp: DataPoint) -> bool:
        """
        open document with built-viewer (DocumentReader)
        return if successfully opened the file
        """
        if self.tab_wid.switchToExistingTab(dp.uuid):
            return True
        new_tab = DocumentReader(self)
        if new_tab.loadDataByUid(dp.uuid):
            self.tab_wid.addDocReader(new_tab, dp.getAuthorsAbbr())
            return True
        else:
            new_tab.deleteLater()
            return False

    def openDocExternal(self, dp: DataPoint):
        """
        open document with system application
        """
        if not dp.is_local:
            return

        if dp.fm.openFile():
            return

        # No local document
        web_url = dp.fm.getWebUrl()
        if web_url == "":
            self.warnDialog("The file is missing", "To add the paper, right click on the entry -> add file")
        elif os.path.exists(web_url):
            openFile(web_url)
        else:
            webbrowser.open(web_url)

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
        self.file_tags.initTags(self.database.total_tags)
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
            # self.setEnabled(True)
            self.file_selector.setEnabled(True)
            self.file_info.setEnabled(True)
            self.file_tags.initTags(self.database.total_tags)
            self.file_selector.loadValidData_async()
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

            # May be update data info panel, 
            # as we may have downloaded data from online to local
            # more info is accessible
            curr_dp = self.getCurrentSelection()
            if curr_dp is not None:
                self.file_info.load(curr_dp)
            else:
                self.file_info.clearPanel()
            return 

        # -----Start from here-----
        # Disable file info panel and selector panel, 
        # because we are to re-create the database object
        # self.setEnabled(False)
        self.file_selector.setEnabled(False)
        self.file_info.setEnabled(False)
        self.statusBar().setEnabled(True)

        if hasattr(self, "db"):
            # First unwatch all file changes, if any
            # otherwise those observer threads will be un-refereced
            # thus can't be stopped
            self.logger.debug("Unwatching all data...")
            self.db: DataBase
            self.db.watchFileChange([])

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
    
    def refreshFileTagSelector(self, *args):
        self.file_tags.initTags(self.database.total_tags)

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
        curr_total_tags = self.database.total_tags
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

        uid = addDocument(self.database.conn, bib_str)
        if uid is None: return 
        fm = FileManipulatorVirtual(uid, self.database.conn)
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
                self.logger.debug("Starting watching {} because it's the current loaded one"\
                    .format(in_info_dp.uuid))
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
        by the way... realod stylesheet
        """
        if getConf()["host"]:
            try:
                # reload server
                ServerConn().reloadDB()
                # loadData
                self.loadData_async(TMP_DB, sync_after=True)    # (This will not raise an ConnectionError)
            except requests.exceptions.ConnectionError:
                self.statusBarInfo("Connection error", 5, bg_color = "red")
                self.logger.warning("Server is down, not reload server.")
                self.logger.debug("May fall into offline mode.")
                self.loadData_async(getConf()["database"], sync_after=False)
        else:
            # local dir
            self.loadData_async(getConf()["database"], sync_after=False)
            #  self._loadData(getConf()["database"])
        # reload stylesheet
        # get application style, for development purpose
        app: QApplication = QApplication.instance()     # type: ignore
        ss = getStyleSheets()[getConf()["stylesheet"]]
        if ss != "":
            with open(ss, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
            self.loadFontConfig()   # we should reload font config whenever stylesheet is loaded
        
    def statusBarMsg(self, msg: str, bg_color = "none"):
        if self.db.offline:
            prefix = "ResBibMan-v{} (offline) ".format(VERSION)
        else:
            prefix = "ResBibMan-v{} (online) ".format(VERSION)

        proxy_status = []
        if getConf()["proxies"]["enable_requests"]:
            proxy_status.append("requests")
        if getConf()["proxies"]["enable_qt"]:
            proxy_status.append("qt")
        if proxy_status:
            prefix += "[proxy<{}>: {}] ".format(
                getConf()["proxies"]["proxy_config"]["proxy_type"], 
                " ".join(proxy_status)
            )
        prefix += ": "

        if not isThemeDarkMode():
            font_color = "rgba(0,0,0,255)"
        else:
            font_color = "rgba(255,255,255,255)"
        color = {
            "none" : "QStatusBar{background:rgba(0,0,0,0); color: " + font_color + "}",
            "red" : "QStatusBar{background:rgba(255,0,0,150); color: rgba(255,255,255,255)}",
            "green" : "QStatusBar{background:rgba(0,200,0,150); color:" + font_color + "}",
            "blue" : "QStatusBar{background:rgba(0,0,255,150); color: rgba(255,255,255,255)}",
            "yellow" : "QStatusBar{background:rgba(255,255,0,150); color: rgba(0,0,0,255)}",
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
        self.database.conn.close()
        try:
            for p in [TMP_DB, TMP_WEB, TMP_COVER]:
                if os.path.exists(p):
                    shutil.rmtree(p)
        except (PermissionError, FileNotFoundError, OSError) as e:
            self.warnDialogCritical(
                "Failed to clean the cache: " + str(e), 
                "Please restart and close the program again to clean cache (or clean with command)"
                )
            self.logger.error(f"Failed to clean cache: {traceback.format_exc()}")
        return super().closeEvent(a0)
