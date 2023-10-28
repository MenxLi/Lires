
import hashlib

def encryptKey(username: str, password: str):
    """
    Encrypt the user information, for verification
    """
    return hashlib.sha256(
        (username + password).encode("ascii")
        ).hexdigest()
