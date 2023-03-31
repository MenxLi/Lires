from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtWidgets import QLineEdit, QWidget, QHBoxLayout, QComboBox
from ..core.dataSearcher import DataSearcher

class SearchLineEdit(QLineEdit):

    def __init__(self, *args, **kwargs):
        super(SearchLineEdit, self).__init__(*args, **kwargs)
        self.clear_sc = QShortcut(QKeySequence('Ctrl+U'), self)
        self.clear_sc.activated.connect(self.clearText)
    
    def clearText(self):
        self.setText("")

class SearchBar(QWidget):
    updateSearch = pyqtSignal()
    def __init__(self, parent = None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        self.search_edit = SearchLineEdit()
        self.combo_box = QComboBox()
        self.combo_box.addItems(["General", "Title", "Author"])
        self.combo_box.setCurrentText("General")

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.combo_box, 1)
        hlayout.addWidget(self.search_edit, 7)
        self.setLayout(hlayout)

        self.search_edit.textChanged.connect(lambda: self.updateSearch.emit())
        self.combo_box.currentTextChanged.connect(lambda: self.updateSearch.emit())
    
    def text(self):
        return self.search_edit.text()
    
    def category(self):
        return self.combo_box.currentText()

    def prepareSearcher(self, searcher):
        text = self.text()
        category = self.category()
        if category == "Title":
            searcher.setRunConfig(
                "searchTitle", 
                {
                    "pattern": text,
                    "ignore_case": True
                }
            )
        elif category == "Author":
            searcher.setRunConfig(
                "searchAuthor", 
                {
                    "pattern": text,
                    "ignore_case": True
                }
            )
        else:
            searcher.setRunConfig(
                "searchStringInfo", 
                {
                    "pattern": text,
                    "ignore_case": True
                }
            )