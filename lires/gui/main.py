
from PyQt6 import QtNetwork
from PyQt6.QtWidgets import QApplication, QStyleFactory
import logging, os, sys
from ..core import globalVar as G
from ..confReader import getStyleSheets, getConf
from ..version import VERSION
from ..core.utils import getDateTimeStr

from .mainWindow import MainWindow

def execProg():
    logger = logging.getLogger("rbm")
    logger.info("************Welcome to Lires-v{} | {}**************".format(VERSION, getDateTimeStr()))

    # Qt proxy settings
    if getConf()["proxies"]["enable_requests"]:
        raise NotImplementedError("Proxy not implemented for requests yet.")
    proxy_settings = getConf()["proxies"]["proxy_config"]
    if proxy_settings["proxy_type"] and getConf()["proxies"]["enable_qt"]:
        proxy = QtNetwork.QNetworkProxy()
        if proxy_settings["proxy_type"].lower() == "socks5":
            proxy.setType(QtNetwork.QNetworkProxy.ProxyType.Socks5Proxy)
        else:
            raise NotImplementedError("qt proxy type not implemented: {}".format(proxy_settings["proxy_type"]))
        logger.info("Using qt proxy: {}".format(proxy_settings))
        proxy.setHostName(proxy_settings["host"])
        proxy.setPort(int(proxy_settings["port"]))
        QtNetwork.QNetworkProxy.setApplicationProxy(proxy)

    # supress webengine warnings
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-logging"
    # os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--enable-logging --log-level=3"

    app = QApplication(sys.argv)

    # set system default style
    logger.debug("Available styles: {}".format(QStyleFactory.keys()))
    if sys.platform == "win32":
        app.setStyle(QStyleFactory.create("Fusion"))
    elif sys.platform == "darwin":
        app.setStyle(QStyleFactory.create("macOS"))     # default
    else: 
        ...
    
    # load user stylesheet
    ss = getStyleSheets()[getConf()["stylesheet"]]
    if ss != "":
        with open(ss, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    # default style may change font size
    # apply font size from conf
    gui = MainWindow()
    gui.loadFontConfig()
    EXIT_CODE =  app.exec()
    G.clearTempDirs()
    return EXIT_CODE
