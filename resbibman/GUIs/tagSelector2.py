import os
import typing
from typing import Optional, Union, List, overload

from PyQt6.QtWidgets import QListView, QHBoxLayout, QInputDialog
from PyQt6.QtGui import QAction, QFont
from PyQt6 import QtCore
from PyQt6 import QtGui

from QCollapsibleCheckList import CollapsibleCheckList

from .widgets import RefWidgetBase
from ._styleUtils import qIconFromSVG_autoBW
from ..confReader import ICON_PATH, getConfV, saveToConf
from ..core.dataClass import DataTags

class TagSelector(RefWidgetBase):
    entry_added = QtCore.pyqtSignal(str)

    def __init__(self, tag_data = Optional[DataTags], tag_total = Optional[DataTags]) -> None:
        super().__init__()
        self.initUI()
        ...

    @property
    def database(self):
        return self.getMainPanel().database
    
    def initUI(self):...

    # can be deleted
    def loadNewTagSet(self, tag_data: DataTags, tag_total: DataTags):
        ...

    def getSelectedTags(self) -> DataTags:...

    def getTotalTags(self) -> DataTags:...

    def addNewSelectedEntry(self, tag: str):...
