import requests, json
from resbibman.confReader import getConfV
from resbibman.core.dataClass import DataBase, DataPoint
from resbibman.core.fileToolsV import FileManipulatorVirtual

addr = "http://{}:{}".format(getConfV("host"), getConfV("port"))

flist_addr = "{}/filelist/%".format(addr)

flist = requests.get(flist_addr).text

flist = json.loads(flist)["data"]

db = DataBase()
db.constuct(flist)
print(db)