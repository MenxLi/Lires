"""
The core package contains the core modules of the application.
These modules should be self-contained and can be used in other modules.
(except for logger, which uses the api module)

Responsibilities of the core modules are:
- data structures
- load and save data
- global variables
- general utility functions
- interface to the server side
"""

from .error import LiresError
__all__ = ['LiresError']