
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow, QSplitter, QWidget, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt

from .fileInfo import FileInfo
from .fileTags import FileTag
from .fileSelector import FileSelector

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
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
    
    def _center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())