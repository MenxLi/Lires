"""
The core package contains the core modules of the application.
These modules should be self-contained and can be used in other modules.

Responsibilities of the core modules are:
- data structures
- load and save data
- global variables
- general utility functions
- interface to the server side
"""
from . import globalVar
globalVar.init()


# from .dataClass import DataBase, DataPoint, DataTags
# from .fileTools import addDocument, DBConnection
# from .fileToolsV import FileManipulatorVirtual
