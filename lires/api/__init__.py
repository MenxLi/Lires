"""
Connect to peripherals and provide an API to interact with them.
Should depend only on lires.config and lires.utils
"""
from .ai import IServerConn
from .server import ServerConn
from .registry import RegistryConn
from .log import LServerConn

__all__ = ["IServerConn", "ServerConn", "RegistryConn", "LServerConn"]