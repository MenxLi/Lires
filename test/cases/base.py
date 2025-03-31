from lires.user import encrypt
from lires import utils

class BaseConfig:
    @property
    def admin_user(self):
        return {
            "username": "admin",
            "password": "admin_password",
            "token": encrypt.encrypt_key("admin", encrypt.generate_hex_hash("admin_password"))
        }
    
    @property
    def normal_user(self):
        return {
            "username": "normal",
            "password": "normal_password",
            "token": encrypt.encrypt_key("normal", encrypt.generate_hex_hash("normal_password"))
        }

__all__ = [
    "BaseConfig",
    "utils"
]