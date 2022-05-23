from __future__ import annotations
import typing, logging
from typing import TYPE_CHECKING

from PyQt5.QtWidgets import QWidget, QMessageBox, QDesktopWidget

from ..core.utils import delay_exec

if TYPE_CHECKING:
    from .mainWindow import MainWindow
    from .fileInfo import FileInfo
    from .fileSelector import FileSelector
    from .tagSelector import TagSelector

class WidgetBase:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("rbm")

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
        if isinstance(self, QWidget):
            qr = self.frameGeometry()
            cp = QDesktopWidget().availableGeometry().center()
            qr.moveCenter(cp)
            self.move(qr.topLeft())

class RefWidgetBase(QWidget, WidgetBase):
    def __init__(self, parent: typing.Optional['QWidget']=None) -> None:
        super().__init__(parent=parent)
        self._main_panel = None
        self._select_panel = None
        self._info_panel = None
        self._tag_panel = None
        self._offline_status = True
    
    def statusBarInfo(self, info: str, time: float = -1, **kwargs):
        self.getMainPanel().statusBarMsg(info, **kwargs)
        if time>0:
            delay_exec(self.getMainPanel().statusBarMsg, time, \
                msg = "Welcome!", bg_color = "none")
    
    def offlineStatus(self, status: bool):
        """
        To be called when change datapoint
        e.g. Set widgets enable status
        """
        if self._offline_status == status:
            # No need to run if status unchanged
            # prevent some circular call
            return
        self._offline_status = status

    def setMainPanel(self, panel: MainWindow):
        self._main_panel = panel
    
    def getMainPanel(self) -> MainWindow:
        assert self._main_panel is not None, "Main panel not set, use setMainPanel to set the panel"
        return self._main_panel
        
    def setSelectPanel(self, panel: FileSelector):
        self._select_panel = panel
    
    def getSelectPanel(self) -> FileSelector:
        assert self._select_panel is not None, "Select panel not set, use setSelectPanel to set the panel"
        return self._select_panel

    def setInfoPanel(self, panel: FileInfo):
        self._info_panel = panel
    
    def getInfoPanel(self) -> FileInfo:
        assert self._info_panel is not None, "Info panel not set, use setInfoPanel to set the panel"
        return self._info_panel

    def setTagPanel(self, panel: TagSelector):
        self._tag_panel = panel
    
    def getTagPanel(self) -> TagSelector:
        assert self._tag_panel is not None, "Tag panel not set, use setTagPanel to set the panel"
        return self._tag_panel

MainWidgetBase = RefWidgetBase


