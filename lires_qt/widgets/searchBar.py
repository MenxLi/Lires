from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtWidgets import QLineEdit, QWidget, QHBoxLayout, QComboBox
from lires.core.dataSearcher import DataSearcher

class SearchLineEdit(QLineEdit):

    def __init__(self, *args, **kwargs):
        super(SearchLineEdit, self).__init__(*args, **kwargs)
        self.clear_sc = QShortcut(QKeySequence.StandardKey.DeleteCompleteLine, self)    # Alt + Backspace
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
        self.combo_box.addItems(["General", "Title", "Author", "Year", "Publication", "Note", "Feature"])
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

    def prepareSearcher(self, searcher: DataSearcher):
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
        elif category == "Year":
            searcher.setRunConfig(
                "searchYear", 
                {
                    "pattern": text,
                }
            )
        elif category == "Note":
            searcher.setRunConfig(
                "searchComment", 
                {
                    "pattern": text,
                    "ignore_case": True
                }
            )
        elif category == "Publication":
            searcher.setRunConfig(
                "searchPublication", 
                {
                    "pattern": text,
                    "ignore_case": True
                }
            )
        elif category == "Feature":
            searcher.setRunConfig(
                "searchFeature", 
                {
                    "pattern": text,
                    "n_return": 999
                }
            )
        else:
            assert category == "General"
            searcher.setRunConfig(
                "searchStringInfo", 
                {
                    "pattern": text,
                    "ignore_case": True
                }
            )