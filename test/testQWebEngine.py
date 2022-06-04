import sys
from PyQt5.Qt import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebKitWidgets import QWebView


app = QApplication(sys.argv)

# web = QWebEngineView()
web = QWebEngineView()

web.load(QUrl("www.bing.com"))

web.show()

sys.exit(app.exec_())
