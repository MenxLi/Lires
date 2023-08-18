"""
This is a collection of APIs for lires client
It is designed for easy retrieval of most frequently used modules of lires
"""

# classes
from lires.core.dataClass import DataPoint, DataBase, DataTags
from lires.core.fileToolsV import FileManipulatorVirtual
from lires.core.dbConn import DBConnection
from lires.core.serverConn import ServerConn, IServerConn

# variables and functions
from lires.core.fileTools import addDocument
from lires.confReader import RBM_HOME, getDatabase, getConf, saveToConf

__all__ = [
    "DataPoint",
    "DataBase",
    "DataTags",
    "FileManipulatorVirtual",
    "DBConnection",
    "ServerConn",
    "IServerConn",

    "RBM_HOME",
    "addDocument",
    "getDatabase",
    "getConf",
    "saveToConf",
]