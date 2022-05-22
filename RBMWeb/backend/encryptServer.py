import hashlib, os
from .confReader import ENC_KEY_PATH

def saveHashKey(h: str) -> bool:
    """
    Save encrypted hash key 
    """
    if not os.path.exists(ENC_KEY_PATH):
        mode = "w"
    else:
        mode = "a"
    with open(ENC_KEY_PATH, mode, encoding="utf-8") as fp:
        fp.write(h + "\n")
    return True

def queryHashKey(h: str) -> bool:
    """
    Check if a hash key is in saved buffer
    """
    if not os.path.exists(ENC_KEY_PATH):
        return False
    with open(ENC_KEY_PATH, "r", encoding="utf-8") as fp:
        txt = fp.read()
    keys = txt.split("\n")
    return h in keys

def deleteHashKey(h: str) -> bool:
    if not os.path.exists(ENC_KEY_PATH):
        return False
    with open(ENC_KEY_PATH, "r", encoding="utf-8") as fp:
        txt = fp.read()
    keys = txt.split("\n")
    DELETED = False
    while True:
        try:
            i = keys.index(h)
            keys.pop(i)
            DELETED = True
        except ValueError:
            break
    if DELETED:
        with open(ENC_KEY_PATH, "w", encoding="utf-8") as fp:
            fp.write("\n".join(keys))
        return True
    return False