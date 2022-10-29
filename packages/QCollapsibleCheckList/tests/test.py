from __future__ import annotations
from PyQt6 import QtCore
from PyQt6 import QtGui

from PyQt6.QtGui import QAction, QKeySequence, QShortcut
from QCollapsibleCheckList import NodeWidget, DataItemAbstract, CollapsibleCheckList
from PyQt6.QtWidgets import QApplication, QFrame, QLineEdit, QMainWindow, QPushButton, QVBoxLayout
import random

def randomTrue():
    return random.random()> 0.5

class StringData(str, DataItemAbstract):
    SEP = "->"

    def isParentOf(self, d: StringData) -> bool:
        d_split = d.split(self.SEP)
        self_split = self.split(self.SEP)
        if len(d_split) <= len(self_split):
            return False
        for i, j in zip(self_split, d_split):
            if i != j:
                return False
        return True
    
    def toString(self) -> str:
        return self

    def __ge__(self, d: StringData) -> bool:
        return len(self) >= len(d)

    def __lt__(self, d: StringData) -> bool:
        return len(self) < len(d)

class MainWindow(QMainWindow):
    new_d0 = StringData("1->3->4")
    new_d1 = StringData("1->3")
    new_d2 = StringData("2->3->4")

    def __init__(self, stringdata, status) -> None:
        super().__init__()

        self.ccl = CollapsibleCheckList(self, stringdata, status)
        self.ccl.onCheckItem.connect(lambda x: print("Signal - onCheckItem", x))
        self.ccl.onUnCheckItem.connect(lambda x: print("Signal - onUnCheckItem", x))

        self.ccl.onHoverEnter.connect(lambda x: print("Signal - onHoverEnter", x))
        self.ccl.onHoverLeave.connect(lambda x: print("Signal - onHoverLeave", x))

        self.ccl.onHoverEnterNodeWidget.connect(lambda x: print("Signal - onHoverEnterNodeWidget", x))
        self.ccl.onHoverLeaveNodeWidget.connect(lambda x: print("Signal - onHoverLeaveNodeWidget", x))

        self.ccl.onCollapseNode.connect(lambda x: print("Signal - onCollapseNode", x))
        self.ccl.onUnCollapseNode.connect(lambda x: print("Signal - onUnCollapseNode", x))

        self.ccl.onCollapseNodeWidget.connect(lambda x: print("Signal - onCollapseNodeWidget", x))
        self.ccl.onUnCollapseNodeWidget.connect(lambda x: print("Signal - onUnCollapseNodeWidget", x))

        frame = QFrame()
        layout = QVBoxLayout()
        frame.setLayout(layout)
        layout.addWidget(self.ccl)


        self.setCentralWidget(frame)
        self.show()

        self.installEventFilter(self)

    def eventFilter(self, a0, a1: QtGui.QKeyEvent) -> bool:
        if a1.type() == QtCore.QEvent.Type.KeyPress:
            a1: QtGui.QKeyEvent
            if a1.key() == QtCore.Qt.Key.Key_A:
                self.ccl.addItem(StringData("1->5"), randomTrue())
                self.ccl.addItem(StringData("2->4"), randomTrue())
                self.ccl.addItem(StringData("1->2->3->4"), randomTrue())
                self.ccl.addItem(self.new_d0, randomTrue())
                self.ccl.addItem(self.new_d1, randomTrue())
                self.ccl.addItem(self.new_d2, randomTrue())
            if a1.key() == QtCore.Qt.Key.Key_D:
                self.ccl.removeItem(self.new_d0)
                self.ccl.removeItem(self.new_d1)
                self.ccl.removeItem(self.new_d2)
        return super().eventFilter(a0, a1)

if __name__ == "__main__":
    app = QApplication([])
    strings = [
        "1",
        "1->3",
        "1->2",
        "2->3",
        "1->2->3",
        "1->2->3->4",
    ]
    sds = [ StringData(s) for s in strings]
    status = [ random.random()>0.5 for s in strings]

    main_win = MainWindow(sds, status)

    app.exec()
