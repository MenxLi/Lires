
import hashlib

def encryptKey(username: str, password_enc: str):
    """
    Encrypt the user information, for verification
    """
    return hashlib.sha256(
        (username + password_enc).encode("ascii")
        ).hexdigest()
