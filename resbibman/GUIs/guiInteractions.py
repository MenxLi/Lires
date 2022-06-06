from typing import List
from PyQt6.QtWidgets import QWidget, QDialog, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal
from ..core.clInteractions import ChoicePromptAbstract

#  class M_ChoicePromptGUI(type(ChoicePromptAbstract), type(QDialog)): ...
#      # https://stackoverflow.com/a/41266737

class ChoicePromptDialog(QDialog):
    def __init__(self, p, prompt: str, choices: List[str], title: str):
        super().__init__(None)
        self.prompt = prompt
        self.choices = choices
        self.title = title
        self.p = p

    def initUI(self):
        self.setWindowTitle(self.title)
        vlayout = QVBoxLayout()
        vlayout.addWidget(QLabel(self.prompt))
        hlayout = QHBoxLayout()
        self.btns = []
        for choice in self.choices:
            btn = QPushButton(choice, self)
            btn.clicked.connect(self.onClickChoice)
            hlayout.addWidget(btn)
            self.btns.append(btn)
        vlayout.addLayout(hlayout)
        self.setLayout(vlayout)

    def onClickChoice(self):
        print("hello")
        self.p._choice = "skip"
        self.accept()

class ChoicePromptGUI(ChoicePromptAbstract):
    def __init__(self, prompt: str, choices: List[str], title: str = "User interaction required"):
        ChoicePromptAbstract.__init__(self, prompt, choices, title)
        self.dialog = ChoicePromptDialog(self, prompt, choices, title)

    @property
    def choice(self):
        return self._choice

    def show(self):
        # will freeze window some how
        # related to qt threading...
        self.dialog.initUI()
        self.dialog.exec()
        return
