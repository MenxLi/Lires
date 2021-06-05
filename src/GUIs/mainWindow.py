
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow, QSplitter, QWidget, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt

from .fileInfo import FileInfo
from .fileTags import DEFAULT_TAGS, FileTag
from .fileSelector import FileSelector

from ..backend.fileTools import FileManipulator
from ..confReader import conf
import os, copy, typing

# for testing propose
from .fileTags import TagSelector
from ..backend.dataClass import DataTags, DataBase, DataPoint

DATA_PATH = conf["database"]
DEFAULT_TAGS = conf["default_tags"]
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DataBase()
        self.initUI()
        self.loadData(DATA_PATH)

        self.show()
    
    def initUI(self):
        self.setWindowTitle("Research bib manager")
        temp_file_path = ""
        self.file_tags = FileTag(self)
        self.file_info = FileInfo(self)
        self.file_selector = FileSelector(self)
        # connect after initialization because we have inter-refernce between these 3 widgets
        self.file_info.connectFuncs()
        self.file_selector.connectFuncs()
        self.file_tags.connectFuncs()

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

    
    def loadData(self, data_path):
        for f in os.listdir(data_path):
            f = os.path.join(data_path, f)
            if os.path.isdir(f):
                fm = FileManipulator(f)
                if fm.screen():
                    data = DataPoint(fm)
                    self.db[data.uuid] = copy.deepcopy(data)
        self.file_selector.loadValidData(set(DEFAULT_TAGS))
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