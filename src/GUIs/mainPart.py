
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow, QWidget, QHBoxLayout
from .fileTree import FileTree
from .bibQuary import BibQuary

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.show()
    
    def initUI(self):
        self.setWindowTitle("Research bib manager")
        self._center()
        # self.file_tree = FileTree()
        self.bib_quary = BibQuary(self)
        self.bib_quary.show()
    
    def _center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())