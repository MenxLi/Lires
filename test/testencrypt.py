import requests, json
from resbibman.confReader import getConfV
from resbibman.core.dataClass import DataBase, DataPoint
from resbibman.core.fileToolsV import FileManipulatorVirtual
from resbibman.core.encryptClient import generateHexHash
from RBMWeb.cmd.manageKey import deleteKey, registerKey
from RBMWeb.backend.encryptServer import queryHashKey

my_key = "123"
if not queryHashKey(generateHexHash(my_key)):
    registerKey(my_key)
    print("registered key")

if queryHashKey(generateHexHash(my_key)):
    print("Successfully validated.")


# test
addr = "http://{}:{}".format(getConfV("host"), getConfV("port"))
flist_addr = "{}/filelist/%".format(addr)

flist = requests.get(flist_addr).text

flist = json.loads(flist)["data"]

db = DataBase()
db.constuct(flist)
print(db)


deleteKey(my_key)