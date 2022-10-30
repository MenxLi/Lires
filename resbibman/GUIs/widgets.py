from __future__ import annotations
import typing, logging
from typing import TYPE_CHECKING, Literal

from PyQt6 import QtGui
from PyQt6.QtWidgets import QWidget, QMessageBox, QApplication
from PyQt6.QtCore import QThreadPool, pyqtSignal, Qt

from ..perf.qtThreading import SleepWorker

if TYPE_CHECKING:
    from .mainWindow import MainWindow
    from .fileInfo import FileInfo
    from .fileSelector import FileSelector
    from .fileTags import FileTag
    from ..core.dataClass import DataBase
    from ..confReader import _ConfFontSizeT

LOGGER = logging.getLogger("rbm")
class WidgetBase:
    logger = logging.getLogger("rbm")
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
    def infoDialog(self, messege, info_msg = ""):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(messege)
        msg_box.setInformativeText(info_msg)
        msg_box.setWindowTitle("Info")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        return msg_box.exec()

    def warnDialog(self, messege, info_msg = ""):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setText(messege)
        msg_box.setInformativeText(info_msg)
        msg_box.setWindowTitle("Warning")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        return msg_box.exec()
    
    def warnDialogCritical(self, messege, info_msg = "Please restart the program"):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setText(messege)
        msg_box.setInformativeText(info_msg)
        msg_box.setWindowTitle("Critical warning")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        return msg_box.exec()
    
    def queryDialog(self, msg, title = "Query", func = lambda x: None) -> bool:
        msg_box = QMessageBox()
        msg_box.setText(msg)
        msg_box.setWindowTitle(title)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        msg_box.buttonClicked.connect(func)
        return_value = msg_box.exec()
        if return_value == QMessageBox.StandardButton.Ok:
            return True
        else: return False

    def _center(self):
        if isinstance(self, QWidget):
            qr = self.frameGeometry()
            cp = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
            qr.moveCenter(cp)
            self.move(qr.topLeft())

class RefBase:
    def __init__(self) -> None:
        self._main_panel = None
        self._select_panel = None
        self._info_panel = None
        self._tag_panel = None
        self._offline_status = True

    def passRefTo(self, new: RefBase):
        if self.getMainPanel():
            new.setMainPanel(self.getMainPanel())

        if self.getInfoPanel():
            new.setInfoPanel(self.getInfoPanel())

        if self.getTagPanel():
            new.setTagPanel(self.getTagPanel())

        if self.getSelectPanel():
            new.setSelectPanel(self.getSelectPanel())

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

    def setTagPanel(self, panel: FileTag):
        self._tag_panel = panel
    
    def getTagPanel(self) -> FileTag:
        assert self._tag_panel is not None, "Tag panel not set, use setTagPanel to set the panel"
        return self._tag_panel


class RefWidgetBase(QWidget, WidgetBase, RefBase):
    # Somehow not working properly... see __init_subclass__
    update_statusmsg = pyqtSignal(str)      # to stop previously scheduled timing status bar info
    def __init__(self, parent: typing.Optional['QWidget']=None) -> None:
        super().__init__(parent=parent)

    def __init_subclass__(cls) -> None:
        # Have to do this, otherwise may somehow lead to \
        # AttributeError: 'MainWindow' does not have a signal with the signature update_statusmsg(QString)
        cls.update_statusmsg = pyqtSignal(str)
        return super().__init_subclass__()
    
    def statusBarInfo(self, info: str, time: float = -1, **kwargs):
        # Send a signal to abort previous worker
        self.update_statusmsg.emit(info)
        self.getMainPanel().statusBarMsg(info, **kwargs)
        def _laterDo():
            self.getMainPanel().statusBarMsg(msg = "Welcome!", bg_color = "none")
        if time>0:
            worker = SleepWorker(time)
            worker.signals.finished.connect(_laterDo)

            # Abort this worker
            self.update_statusmsg.connect(lambda str_: worker.setBreak())
            QApplication.instance().aboutToQuit.connect(worker.setBreak)    # not send signal after app exited

            pool = QThreadPool.globalInstance()
            pool.start(worker)
    
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

    def freeze(self):
        class Freezer:
            def __enter__(_self):
                self.setEnabled(False)
            def __exit__(_self, exception_type, exception_value, traceback):
                self.setEnabled(True)
        return Freezer()

class MyQUtils(QWidget):
    @classmethod
    def keyModifiers(cls, *args: Literal["Control", "Shift", "Alt"]) -> bool:
        """Check if key modifiers has been pressed

        Args:
            *args (Literal[&quot;Control&quot;, &quot;Shift&quot;, &quot;Alt&quot;]): Modifiers to be checked

        Returns:
            bool: True if all modifiers are pressed
        """
        modifiers = []
        for k in args:
            try:
                attr = getattr(Qt.KeyboardModifier, k + "Modifier")
                modifiers.append(attr)
            except AttributeError:
                LOGGER.error("Unable to get modifier from QtCore.Qt: {}".format(k))
                return False
        m_total = modifiers[0]
        for m in modifiers[1:]:
            m_total = m|m_total
        return QApplication.keyboardModifiers() == m_total

class MainWidgetBase(MyQUtils, RefWidgetBase):
    @property
    def database(self) -> DataBase:
        return self.getMainPanel().database

    def applyFontConfig(self, font_config: _ConfFontSizeT):
        # To be implemented by subclasses
        return None
