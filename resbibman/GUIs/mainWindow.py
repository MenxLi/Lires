import pyperclip
from typing import Tuple
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QAction, QDesktopWidget, QDialog, QFileDialog, QMainWindow, QMenu, QMenuBar, QSplitter, QWidget, QHBoxLayout, QFrame, QToolBar, QSizePolicy
from PyQt5.QtCore import Qt

from .widgets import RefWidgetBase, WidgetBase
from .fileInfo import FileInfo
from .fileTags import FileTag
from .fileSelector import FileSelector
from .bibQuery import BibQuery
from .pendingWindow import PendingWindow
from .settings import SettingsWidget

from ..core.fileTools import FileGenerator
from ..core.fileToolsV import FileManipulatorVirtual
from ..core.bibReader import BibParser
from ..core.utils import openFile
from ..core.dataClass import DataTags, DataBase, DataPoint
from ..confReader import DOC_PATH, TMP_DB, getConf, ICON_PATH, VERSION, getConfV, getDatabase
import os, copy, typing, requests

# for testing propose
from .fileTags import TagSelector

class MainWindowGUI(QMainWindow, RefWidgetBase):
    def __init__(self):
        super().__init__()
        self.db = DataBase()
        self._panel_status = (True, True, True)

        self.initUI()
        self.showMaximized()
        self.show() 
    
    def initUI(self):
        self.setWindowTitle("Research bib manager")
        # self.resize(900, 600)
        self.setWindowIcon(QIcon(os.path.join(ICON_PATH, "resbibman-icon.png")))
        self._initPanels()
        self._createActions()
        # self._createMenuBar()
        self._createToolBars()

        self.status_bar = self.statusBar()

        hbox = QHBoxLayout()
        self.splitter = QSplitter(Qt.Horizontal)
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
        stretch_factor = [1, 4, 2]      # default stretch factor
        stretch_factor = [ toggle_mask[i]*stretch_factor[i] for i in range(3) ]
        stretch_factor = [ float(f)/sum(stretch_factor) for f in stretch_factor ]
        curr_width = self.frameGeometry().width()
        w_sizes = [ int(curr_width*f) for f in stretch_factor]
        self.splitter.setSizes(w_sizes)
        self.logger.debug("Set sizes to {}".format(w_sizes))
        return 
    
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
        self.act_file_additem.setIcon(QIcon(os.path.join(ICON_PATH, "addfile-24px.svg")))
        self.act_opendb = QAction("&Open database", self)
        self.act_opendb.setIcon(QIcon(os.path.join(ICON_PATH, "folder-24px.svg")))
        self.act_settings = QAction("&Settings", self)
        self.act_settings.setIcon(QIcon(os.path.join(ICON_PATH, "settings-24px.svg")))
        self.act_help = QAction("&Info", self)
        self.act_help.setIcon(QIcon(os.path.join(ICON_PATH, "info-24px.svg")))
        self.act_reload = QAction("&Reload", self)
        self.act_reload.setIcon(QIcon(os.path.join(ICON_PATH, "refresh-24px.svg")))
        self.act_open_pdb = QAction("&Pending data", self)
        self.act_open_pdb.setIcon(QIcon(os.path.join(ICON_PATH, "hourglass_bottom_black_24dp.svg")))

        self.act_importbib_from_clip = QAction("Import bib from clipboard", self)
        self.act_importbib_from_clip.setIcon(QIcon(os.path.join(ICON_PATH, "paste-24px.svg")))
        self.act_importbib_from_clip.setShortcut(QKeySequence("ctrl+shift+alt+i"))

        self.act_show_panel1 = QAction("&Show panel 1", self)
        self.act_show_panel1.setIcon(QIcon(os.path.join(ICON_PATH, "looks_one_black_48dp.svg")))
        self.act_show_panel2 = QAction("&Show panel 2", self)
        self.act_show_panel2.setIcon(QIcon(os.path.join(ICON_PATH, "looks_two_black_48dp.svg")))
        self.act_show_panel3 = QAction("&Show panel 3", self)
        self.act_show_panel3.setIcon(QIcon(os.path.join(ICON_PATH, "looks_3_black_48dp.svg")))

    def _createMenuBar(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        files_menu = QMenu("&Files", self)
        menu_bar.addMenu(files_menu)
        files_menu.addAction(self.act_file_additem)

        settings_menu = QMenu("&Settings", self)
        menu_bar.addMenu(settings_menu)
        settings_menu.addAction(self.act_settings)
    
    def _createToolBars(self):
        tool_bar = QToolBar("Toolbar")
        self.addToolBar(Qt.TopToolBarArea, tool_bar)
        tool_bar.addAction(self.act_file_additem)
        tool_bar.addAction(self.act_importbib_from_clip)
        tool_bar.addAction(self.act_opendb)
        tool_bar.addAction(self.act_settings)
        tool_bar.addAction(self.act_help)
        tool_bar.addAction(self.act_reload)
        
        tool_bar = QToolBar("Filebar")
        self.addToolBar(Qt.TopToolBarArea, tool_bar)
        tool_bar.addAction(self.act_open_pdb)

        # Align right
        #  tool_bar = QToolBar("Spacer")
        #  tool_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        #  self.addToolBar(Qt.TopToolBarArea, tool_bar)

        toob_bar = QToolBar("Panels")
        self.addToolBar(Qt.TopToolBarArea, toob_bar)
        toob_bar.addAction(self.act_show_panel1)
        toob_bar.addAction(self.act_show_panel2)
        toob_bar.addAction(self.act_show_panel3)
    
class MainWindow(MainWindowGUI):
    def __init__(self):
        super().__init__()
        self.logger.debug("Configuration: ")
        self.logger.debug(getConf())
        self.initActions()
        self.reloadData()
    
    @property
    def database(self):
        return self.db

    def initActions(self):
        self.act_settings.triggered.connect(self.openSettingsDialog)
        self.act_opendb.triggered.connect(self.openDataBaseDir)
        self.act_help.triggered.connect(self.openHelpFile)
        self.act_file_additem.triggered.connect(self.openAddfileSelectionDialog)
        self.act_reload.triggered.connect(self.reloadData)
        self.act_open_pdb.triggered.connect(self.openPendingWindow)

        self.act_importbib_from_clip.triggered.connect(self.importEntryFromClipboardBib)

        self.act_show_panel1.triggered.connect(lambda: self.togglePanel(0))
        self.act_show_panel2.triggered.connect(lambda: self.togglePanel(1))
        self.act_show_panel3.triggered.connect(lambda: self.togglePanel(2))

    def togglePanel(self, idx:int):
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
    
    def loadData(self, data_path):
        self.db = DataBase()
        if getConf()["host"] != "":
            # Online mode
            self.statusBarInfo("Requesting remote server", bg_color = "blue")
        self.db.init(data_path)
        self.file_selector.loadValidData(set(getConf()["default_tags"]), hint = True)
        self.file_tags.initTags(self.getTotalTags())
        self.statusBarInfo("Success", 2, bg_color = "green")

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
        cp = QDesktopWidget().availableGeometry().center()
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
    
    def openHelpFile(self):
        # help_file_path = os.path.join(DOC_PATH, "info.html")
        # webbrowser.open("file://"+help_file_path)
        help_file_path = os.path.join(DOC_PATH, "使用说明.md")
        openFile(help_file_path)
    
    def openAddfileSelectionDialog(self):
        extensions = getConf()["accepted_extensions"]
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
            if f == "":
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
    
    def reloadData(self):
        if getConf()["host"]:
            try:
                # reload server
                addr = "http://{}:{}".format(getConfV("host"), getConfV("port"))
                req_reloadDB = addr + "/cmd/reloadDB"
                requests.get(req_reloadDB)
                # loadData
                self.loadData(TMP_DB)
                # sync local with remote
                n_local = self.db.n_local
                _count = 0
                for uuid, dp in self.db.items():
                    dp: DataPoint
                    if dp.is_local:
                        _count += 1
                        self.statusBarInfo(f"Sync with remote: {_count}/{n_local}", bg_color = "blue")
                        self.logger.info(f"Sync with remote: {_count}/{n_local}")
                        dp.sync()
                self.statusBarInfo("Successfully synchronized", 5, bg_color = "green")
            except requests.exceptions.ConnectionError:
                self.statusBarInfo("Connection error", 5, bg_color = "red")
                self.logger.warning("Server is down, not reload server.")
                self.logger.debug("May fall into offline mode.")
                self.loadData(getConf()["database"])
        else:
            # local dir
            self.loadData(getConf()["database"])
        self.file_info.clearPanel()
        
    def statusBarMsg(self, msg: str, bg_color = "none"):
        if self.db.offline:
            prefix = "ResBibMan-v{} (offline): ".format(VERSION)
        else:
            prefix = "ResBibMan-v{} (online): ".format(VERSION)
        color = {
           "none" : "QStatusBar{background:rgba(0,0,0,0)}",
           "red" : "QStatusBar{background:rgba(255,0,0,150)}",
           "green" : "QStatusBar{background:rgba(0,255,0,150)}",
           "blue" : "QStatusBar{background:rgba(0,0,255,150)}",
        }
        self.statusBar().setStyleSheet(color[bg_color])
        # self.statusBar().setStyleSheet(f"color : {txt_color}")
        self.statusBar().showMessage(prefix + msg)
