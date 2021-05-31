from PyQt5.QtWidgets import QWidget, QFrame

class FileTreeGUI(QWidget):
    """
    Implement the GUI for file tree
    """
    def __init__(self):
        super().__init__()
        self.initUI()
        self.show()

    def initUI(self):
        pass

class FileTree(FileTreeGUI):
    """
    Implement the functions for file tree
    """
    def __init__(self):
        super().__init__()