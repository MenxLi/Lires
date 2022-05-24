import time
from typing import Callable
from PyQt5.QtCore import QThread, QThreadPool, QObject, QRunnable, Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget


class ThreadSignalsQ(QObject):
    started_str = pyqtSignal(str)
    started_int = pyqtSignal(int)
    started = pyqtSignal()
    finished_str = pyqtSignal(str)
    finished_int = pyqtSignal(int)
    finished = pyqtSignal()


class DoLaterQ(QRunnable):
    def __init__(self, wait_time: float, target: Callable, args: tuple, kwargs: dict):
        super().__init__()
        self._wait_time = wait_time
        self._target = target
        self._args = args
        self._kwargs = kwargs
        self.signal = ThreadSignalsQ()

    def run(self):
        self.signal.started.emit()
        time.sleep(self._wait_time)
        self._target(*self._args, **self._kwargs)
        self.signal.finished.emit()

def qDoLater(wait_time: float, target: Callable, args: tuple = (), kwargs: dict = {}):
    worker = DoLaterQ(wait_time, target, args, kwargs)
    pool = QThreadPool.globalInstance()
    pool.start(worker)
