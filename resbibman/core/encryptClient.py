import hashlib

def generateHexHash(s: str) -> str:
    enc = s.encode("ascii")
    return hashlib.sha256(enc).hexdigest()