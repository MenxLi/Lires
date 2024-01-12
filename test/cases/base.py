from lires.user import encrypt
from lires import utils

class BaseConfig:
    @property
    def admin_user(self):
        return {
            "username": "admin",
            "password": "admin_password",
            "token": encrypt.encryptKey("admin", encrypt.generateHexHash("admin_password"))
        }
    
    @property
    def normal_user(self):
        return {
            "username": "normal",
            "password": "normal_password",
            "token": encrypt.encryptKey("normal", encrypt.generateHexHash("normal_password"))
        }

__all__ = [
    "BaseConfig",
    "utils"
]