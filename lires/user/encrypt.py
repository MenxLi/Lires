
import hashlib

def encrypt_key(username: str, password_enc: str):
    """
    Encrypt the user information, for verification
    """
    return hashlib.sha256(
        (username + password_enc).encode("ascii")
        ).hexdigest()

def generate_hex_hash(s: str) -> str:
    enc = s.encode("ascii")
    return hashlib.sha256(enc).hexdigest()