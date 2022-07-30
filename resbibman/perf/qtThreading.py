from __future__ import annotations

import time
import requests
from typing import Callable, TYPE_CHECKING, List
from PyQt6.QtCore import QThread, QThreadPool, QObject, QRunnable, Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget

from ..core import globalVar as G
if TYPE_CHECKING:
    from ..core.dataClass import DataPoint, DataBase


class ThreadSignalsQ(QObject):
    started = pyqtSignal()
    finished = pyqtSignal()


class ThreadSignalsForSleepWorker(ThreadSignalsQ):
    finished = pyqtSignal()

class SleepWorker(QRunnable):
    def __init__(self, wait_time: float):
        super().__init__()
        self._wait_time = wait_time
        self.signals = ThreadSignalsForSleepWorker()
        self._break = False
    def run(self):
        self.signals.started.emit()
        time.sleep(self._wait_time)
        if not self._break:
            self.signals.finished.emit()
    def setBreak(self):
        self._break = True

class ThreadSignalsForSyncWorker(ThreadSignalsQ):
    # on finish sync one datapoint -> status code (0 for success)
    on_chekpoint = pyqtSignal(int)      
    finished = pyqtSignal(bool)

class SyncWorker(QRunnable):
    def __init__(self, sync_lis: List[DataPoint]):
        super().__init__()
        self.to_sync = sync_lis
        self.signals = ThreadSignalsForSyncWorker()

    def run(self):
        self.signals.started.emit()
        SUCCESS = True
        for dp in self.to_sync:
            success = dp.sync()
            if not success:
                self.signals.on_chekpoint.emit(G.last_status_code)
                SUCCESS = False
            else:
                self.signals.on_chekpoint.emit(0)
        self.signals.finished.emit(SUCCESS)

class ThreadSignalsForInitDBWorker(ThreadSignalsQ):
    finished = pyqtSignal(bool)

class InitDBWorker(QRunnable):
    def __init__(self, db: DataBase, local_db_path: str, force_offline = False):
        super().__init__()
        self.db = db
        self.force_offline = force_offline
        self.local_db_path = local_db_path
        self.signals = ThreadSignalsForInitDBWorker()

    def run(self):
        try:
            self.db.init(self.local_db_path, force_offline = self.force_offline)
            self.signals.finished.emit(True)
        except requests.exceptions.ConnectionError:
            self.signals.finished.emit(False)
