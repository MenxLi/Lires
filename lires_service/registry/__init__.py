"""
A service registry that stores all services' information
"""
from .server import startServer
from .store import ServiceName, Registration

__all__ = [
    "startServer",
    "ServiceName",
    "Registration"
]