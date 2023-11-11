"""
This is a collection of APIs for lires client
It is designed for easy retrieval of most frequently used modules of lires
"""

# classes
from lires.core.dataClass import DataPoint, DataBase, DataTags
from lires.core.fileTools import FileManipulator
from lires.core.dbConn import DBConnection
from lires.core.serverConn import ServerConn, IServerConn

# variables and functions
from lires.core.fileTools import addDocument
from lires.confReader import LRS_HOME, getConf, saveToConf

__all__ = [
    "DataPoint",
    "DataBase",
    "DataTags",
    "FileManipulator",
    "DBConnection",
    "ServerConn",
    "IServerConn",

    "LRS_HOME",
    "addDocument",
    "getConf",
    "saveToConf",
]