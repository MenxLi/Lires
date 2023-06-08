"""
This is a collection of APIs for resbibman client
It is designed for easy retrieval of most frequently used modules of resbibman
"""

# classes
from resbibman.core.dataClass import DataPoint, DataBase, DataTags
from resbibman.core.fileToolsV import FileManipulatorVirtual
from resbibman.core.dbConn import DBConnection
from resbibman.core.serverConn import ServerConn, IServerConn

# variables and functions
from resbibman.core.fileTools import addDocument
from resbibman.confReader import RBM_HOME, getDatabase, getConf, saveToConf

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