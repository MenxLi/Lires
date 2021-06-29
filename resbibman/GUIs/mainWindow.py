from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QDesktopWidget, QDialog, QFileDialog, QMainWindow, QMenu, QMenuBar, QSplitter, QWidget, QHBoxLayout, QFrame, QToolBar
from PyQt5.QtCore import Qt

from .fileInfo import FileInfo
from .fileTags import FileTag
from .fileSelector import FileSelector
from .bibQuery import BibQuery
from .settings import SettingsWidget

from ..backend.fileTools import FileManipulator
from ..backend.utils import openFile
from ..backend.dataClass import DataTags, DataBase, DataPoint
from ..confReader import DOC_PATH, getConf, ICON_PATH, VERSION
import os, copy, typing, webbrowser

# for testing propose
from .fileTags import TagSelector

class MainWindowGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DataBase()
        self.initUI()
        self.show()
    
    def initUI(self):
        self.setWindowTitle("Research bib manager - {version}".format(version = VERSION))
        self._initPanels()
        self._createActions()
        # self._createMenuBar()
        self._createToolBars()

        hbox = QHBoxLayout()
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.file_tags)
        splitter.addWidget(self.file_selector)
        splitter.addWidget(self.file_info)
        splitter.setSizes([100, 300, 120])
        hbox.addWidget(splitter)

        wid = QWidget(self)
        self.setCentralWidget(wid)
        wid.setLayout(hbox)
        self.resize(900, 600)
        self._center()
    
    def _initPanels(self):
        self.file_tags = FileTag(self)
        self.file_info = FileInfo(self)
        self.file_selector = FileSelector(self)

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
        tool_bar.addAction(self.act_opendb)
        tool_bar.addAction(self.act_settings)
        tool_bar.addAction(self.act_help)
    
class MainWindow(MainWindowGUI):
    def __init__(self):
        super().__init__()
        self.initActions()
        self.loadData(getConf()["database"])

    def initActions(self):
        self.act_settings.triggered.connect(self.openSettingsDialog)
        self.act_opendb.triggered.connect(self.openDataBaseDir)
        self.act_help.triggered.connect(self.openHelpFile)
        self.act_file_additem.triggered.connect(self.openAddfileSelectionDialog)

    def loadData(self, data_path):
        self.db = DataBase()
        for f in os.listdir(data_path):
            f = os.path.join(data_path, f)
            if os.path.isdir(f):
                fm = FileManipulator(f)
                if fm.screen():
                    data = DataPoint(fm)
                    self.db[data.uuid] = copy.deepcopy(data)
        self.file_selector.loadValidData(set(getConf()["default_tags"]))
        self.file_tags.initTags(self.getTotalTags())

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
        database = getConf()["database"]
        openFile(database)
    
    def openHelpFile(self):
        help_file_path = os.path.join(DOC_PATH, "info.html")
        webbrowser.open("file://"+help_file_path)
    
    def openAddfileSelectionDialog(self):
        extensions = getConf()["accepted_extensions"]
        extension_filter = "({})".format(" ".join(["*"+i for i in extensions]))
        fname = QFileDialog.getOpenFileName(self, caption="Select papers", filter=extension_filter)[0]
        self.addFilesToDatabseByURL([fname])
    
    def addFilesToDatabseByURL(self, urls: typing.List[str]):
        curr_selected_tags = self.getCurrentSelectedTags()
        curr_total_tags = self.getTotalTags()
        for f in urls:
            self.bib_quary = BibQuery(self, f, tag_data=curr_selected_tags, tag_total=curr_total_tags)
            self.bib_quary.file_added.connect(self.file_selector.addToDatabase)
            self.bib_quary.file_added.connect(self.refreshFileTagSelector)
            self.bib_quary.show()
        
