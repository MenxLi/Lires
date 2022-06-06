import time, logging
from typing import List
from PyQt6.QtWidgets import QDialog, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PyQt6.QtCore import pyqtSignal, QObject
from ..core.clInteractions import ChoicePromptAbstract


class ChoicePromptDialog(QDialog):
    choice_decided = pyqtSignal(str)
    def __init__(self):
        super().__init__(None)
        self.vlayout = QVBoxLayout()
        self.hlayout = QHBoxLayout()
        self.label = QLabel()
        self.vlayout.addWidget(self.label)
        self.vlayout.addLayout(self.hlayout)
        self.setLayout(self.vlayout)

    def showUp(self, prompt: str, choices: List[str], title: str = "Prompt"):
        self.prompt = prompt
        self.choices = choices
        self.title = title

        self.setUI()
        self.show()

    def setUI(self):
        self.setWindowTitle(self.title)
        self.label.setText(self.prompt)
        self.btns = []
        for choice in self.choices:
            btn = QPushButton(choice, parent = self)
            btn.clicked.connect(self.onClickChoice)
            self.hlayout.addWidget(btn)
            self.btns.append(btn)

    def destoryUI(self):
        for btn in self.btns:
            btn: QPushButton
            btn.setParent(None)

    def onClickChoice(self):
        choice = self.sender().text()
        self.choice_decided.emit(choice)
        self.close()

class M_ChoicePromptGUI(type(ChoicePromptAbstract), type(QObject)): ...
    # https://stackoverflow.com/a/41266737

class ChoicePromptGUI(ChoicePromptAbstract, QObject, metaclass = M_ChoicePromptGUI):
    logger = logging.getLogger("rbm")
    open_choices = pyqtSignal(str, list, str)
    def __init__(self):
        ChoicePromptAbstract.__init__(self)
        QObject.__init__(self)
        self.__choice_set = False
        # the dialog GUI should be run on main thread, call self.__init__ in main thread
        self.initDialogWid()

    @property
    def choice(self):
        return self._choice

    def initDialogWid(self):
        self._dialog = ChoicePromptDialog()
        # self.show may run on worker thread, thus use signals for communication
        self._dialog.choice_decided.connect(self.setChoice)
        self.open_choices.connect(self._dialog.showUp)

    def show(self, prompt: str, choices: List[str], title: str = "Prompt"):
        self.__choice_set = False
        self.open_choices.emit(prompt, choices, title)
        self.logger.debug("Waiting for user response")
        while True:
            if self.__choice_set:
                break
            # waiting for user input
            time.sleep(0.5)
        return

    def setChoice(self, choice: str):
        self._choice = choice
        self._dialog.destoryUI()
        self.__choice_set = True
