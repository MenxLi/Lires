import random
import string
from uuid import uuid4

def sUUID() -> str:
    """generate short UUID of length 21
    Returns:
        str: short string uuid
    """
    B16_TABLE = {
        "0": "0000",
        "1": "0001",
        "2": "0010",
        "3": "0011",
        "4": "0100",
        "5": "0101",
        "6": "0110",
        "7": "0111",
        "8": "1000",
        "9": "1001",
        "a": "1010",
        "b": "1011",
        "c": "1100",
        "d": "1101",
        "e": "1110",
        "f": "1111",
    }
    B64_LIST =[
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",\
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",\
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+", "-"
    ]
    uuid_long = uuid4().hex
    # b_asciis = " ".join(["{0:08b}".format(ord(u), "b") for u in uuid_long])
    binary = "".join([B16_TABLE[u] for u in uuid_long])
    # len(binary) = 128
    uuid_short = ["0"]*21
    for i in range(0, len(binary)-2, 6):
        b = binary[i:i+6]
        integer = int(b, 2)
        uuid_short[i//6] = B64_LIST[integer]
    return "".join(uuid_short)

def ssUUID() -> str:
    """Short uuid of length 16

    Returns:
        str: uuid
    """
    suid = sUUID()
    return suid[:8] + suid[-8:]

def sssUUID() -> str:
    """Short uuid of length 8

    Returns:
        str: uuid
    """
    return ssUUID()[::2]

def randomAlphaNumeric(length: int):
    """Generate a random string"""
    str = string.ascii_lowercase
    return ''.join(random.choice(str) for i in range(length))
