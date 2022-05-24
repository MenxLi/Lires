from __future__ import annotations

import time
from ..core import globalVar as G
from typing import Callable, TYPE_CHECKING, List
from PyQt5.QtCore import QThread, QThreadPool, QObject, QRunnable, Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget

if TYPE_CHECKING:
    from ..core.dataClass import DataPoint


class ThreadSignalsQ(QObject):
    started_str = pyqtSignal(str)
    started_int = pyqtSignal(int)
    started = pyqtSignal()
    finished_str = pyqtSignal(str)
    finished_int = pyqtSignal(int)
    finished = pyqtSignal()
    at_checkpoint_str = pyqtSignal(str)
    at_checkpoint_int = pyqtSignal(int)
    at_chekpoint = pyqtSignal()
    breaked = pyqtSignal()

class SleepWorker(QRunnable):
    def __init__(self, wait_time: float):
        super().__init__()
        self._wait_time = wait_time
        self.signal = ThreadSignalsQ()
    def run(self):
        self.signal.started.emit()
        time.sleep(self._wait_time)
        self.signal.finished.emit()


class SyncWorker(QRunnable):
    def __init__(self, sync_lis: List[DataPoint]):
        super().__init__()
        self.to_sync = sync_lis
        self.signal = ThreadSignalsQ()

    def run(self):
        self.signal.started.emit()
        SUCCESS = True
        for dp in self.to_sync:
            success = dp.sync()
            if not success:
                self.signal.at_checkpoint_int.emit(G.last_status_code)
                SUCCESS = False
            else:
                self.signal.at_checkpoint_int.emit(0)
        self.signal.finished_int.emit(SUCCESS)

