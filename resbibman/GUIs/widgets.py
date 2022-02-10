
from PyQt5.QtWidgets import QStyle, QWidget, QMessageBox, QListView, QHBoxLayout, QVBoxLayout, QDesktopWidget
from PyQt5 import QtCore
from PyQt5 import QtGui

import typing
from ..backend.dataClass import DataTags

class WidgetBase(QWidget):
    def warnDialog(self, messege, info_msg = ""):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText(messege)
        msg_box.setInformativeText(info_msg)
        msg_box.setWindowTitle("Warning")
        msg_box.setStandardButtons(QMessageBox.Ok)
        return msg_box.exec()
    
    def warnDialogCritical(self, messege, info_msg = "Please restart the program"):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText(messege)
        msg_box.setInformativeText(info_msg)
        msg_box.setWindowTitle("Critical warning")
        msg_box.setStandardButtons(QMessageBox.Ok)
        return msg_box.exec()
    
    def queryDialog(self, msg, title = "Query", func = lambda x: None) -> bool:
        msg_box = QMessageBox()
        msg_box.setText(msg)
        msg_box.setWindowTitle(title)
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg_box.buttonClicked.connect(func)
        return_value = msg_box.exec()
        if return_value == QMessageBox.Ok:
            return True
        else: return False

    def _center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

class RefWidgetBase(WidgetBase):
    def __init__(self, parent: typing.Optional['QWidget']=None) -> None:
        super().__init__(parent=parent)
        self._main_panel = None
        self._select_panel = None
        self._info_panel = None
        self._tag_panel = None
    
    def setMainPanel(self, panel: QWidget):
        self._main_panel = panel
    
    def getMainPanel(self) -> WidgetBase:
        assert self._main_panel is not None, "Main panel not set, use setMainPanel to set the panel"
        return self._main_panel
        
    def setSelectPanel(self, panel: QWidget):
        self._select_panel = panel
    
    def getSelectPanel(self) -> WidgetBase:
        assert self._select_panel is not None, "Select panel not set, use setSelectPanel to set the panel"
        return self._select_panel

    def setInfoPanel(self, panel: QWidget):
        self._info_panel = panel
    
    def getInfoPanel(self) -> WidgetBase:
        assert self._info_panel is not None, "Info panel not set, use setInfoPanel to set the panel"
        return self._info_panel

    def setTagPanel(self, panel: QWidget):
        self._tag_panel = panel
    
    def getTagPanel(self) -> WidgetBase:
        assert self._tag_panel is not None, "Tag panel not set, use setTagPanel to set the panel"
        return self._tag_panel

MainWidgetBase = RefWidgetBase


