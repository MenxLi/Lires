import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
 
class Example(QMainWindow):
 
    def __init__(self):
        super(Example, self).__init__()
        # 窗口标题
        self.setWindowTitle('文件拖入')
        # 定义窗口大小
        self.resize(500, 400)
        self.textBrowser = QTextBrowser()
        self.setCentralWidget(self.textBrowser)
        # 不换行设置
        self.textBrowser.setLineWrapMode(0)
        # 调用Drops方法
        self.setAcceptDrops(True)
        # 设置字体
        font = QFont()
        font.setFamily("黑体")
        font.setPointSize(13)
        self.textBrowser.setFont(font)
 
    # 鼠标拖入事件
    def dragEnterEvent(self, event):
        self.textBrowser.setText('文件路径:\n' + os.path.dirname((event.mimeData().urls())[0].toLocalFile()))
 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    example = Example()
    example.show()
    sys.exit(app.exec_())