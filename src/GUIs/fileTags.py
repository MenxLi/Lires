from PyQt5.QtWidgets import QWidget, QFrame, QHBoxLayout
from .widgets import WidgetBase

class FileTagGUI(WidgetBase):
    """
    Implement the GUI for file tree
    """
    def __init__(self, parent = None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.frame = QFrame()
        self.frame.setFrameStyle(QFrame.StyledPanel)
        hbox = QHBoxLayout()
        hbox.addWidget(self.frame)
        self.setLayout(hbox)

class FileTag(FileTagGUI):
    """
    Implement the functions for file tree
    """
    def __init__(self, parent = None):
        super().__init__(parent)
    
    def connectFuncs(self):
        pass