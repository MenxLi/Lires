from PyQt5.QtWidgets import QWidget, QFrame

class FileInfoGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.show()

    def initUI(self):
        pass

class FileInfo(FileInfoGUI):
    """
    Implement the functions for file info
    """
    def __init__(self):
        super().__init__()
