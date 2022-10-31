"""
Adapted from: https://stackoverflow.com/a/41643802/6775765
"""
import sys
from PyQt6 import QtGui, QtWidgets
from QFlowLayout import FlowLayout

class Bubble(QtWidgets.QLabel):
    def __init__(self, text):
        super(Bubble, self).__init__(text)
        self.word = text
        self.setContentsMargins(5, 5, 5, 5)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        painter.drawRoundedRect(
            0, 0, self.width() - 1, self.height() - 1, 5, 5)
        super(Bubble, self).paintEvent(event)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, text, parent=None):
        super(MainWindow, self).__init__(parent)
        self.mainArea = QtWidgets.QScrollArea(self)
        self.mainArea.setWidgetResizable(True)
        widget = QtWidgets.QWidget(self.mainArea)
        widget.setMinimumWidth(50)
        layout = FlowLayout(widget)
        self.words = []
        for word in text.split():
            label = Bubble(word)
            label.setFont(QtGui.QFont('SblHebrew', 18))
            label.setFixedWidth(label.sizeHint().width())
            self.words.append(label)
            layout.addWidget(label)
        self.mainArea.setWidget(widget)
        self.setCentralWidget(self.mainArea)

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow('Harry Potter is a series of fantasy literature')
    window.show()
    sys.exit(app.exec())