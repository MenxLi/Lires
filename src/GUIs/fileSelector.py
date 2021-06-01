from PyQt5.QtWidgets import QHBoxLayout, QWidget, QFrame
from PyQt5 import QtGui, QtCore
import typing

from .bibQuery import BibQuery

class FileSelectorGUI(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.initUI()
        self.setAcceptDrops(True)
    
    def initUI(self):
        self.frame = QFrame()
        self.frame.setFrameStyle(QFrame.StyledPanel)
        hbox = QHBoxLayout()
        hbox.addWidget(self.frame)
        self.setLayout(hbox)
    

class FileSelector(FileSelectorGUI):
    def __init__(self, parent = None):
        super().__init__(parent)
    
    def dragEnterEvent(self, a0: QtGui.QDragEnterEvent) -> None:
        if a0.mimeData().hasUrls():
            a0.accept()
        else:
            a0.ignore()
        return super().dragEnterEvent(a0)
    
    def dropEvent(self, a0: QtGui.QDropEvent) -> None:
        files = [u.toLocalFile() for u in a0.mimeData().urls()]
        for f in files:
            print(f)
            self.bib_quary = BibQuery(self, f)
            self.bib_quary.show()
        return super().dropEvent(a0)