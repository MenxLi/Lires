import argparse
from resbibman.core.encryptClient import generateHexHash
from resbibman.core.utils import randomAlphaNumeric
from resbibman.server.auth.encryptServer import saveHashKey, deleteHashKey

def generateKey(length: int = 6) -> str:
    k = randomAlphaNumeric(length)
    if registerKey(k):
        return k
    else:
        return ""

def registerKey(key: str) -> bool:
    h = generateHexHash(key)
    return saveHashKey(h)

def deleteKey(key: str) -> bool:
    h = generateHexHash(key)
    return deleteHashKey(h)

def run():
    parser = argparse.ArgumentParser("Key management")
    parser.add_argument("-g", "--generate",
                    help = "genetate key of given length")
    parser.add_argument("-r", "--register", 
                    help = "save a key")
    parser.add_argument("-d", "--delete", 
                    help = "delete a key")

    args = parser.parse_args()

    if args.generate:
        length = int(args.generate)
        key = generateKey(length)
        print("Generated key: ", key)
    
    if args.register:
        if registerKey(args.register):
            print("Success.")

    if args.delete:
        if deleteKey(args.delete):
            print("Success.")


if __name__ == "__main__":
    run()