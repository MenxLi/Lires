import requests, json, logging, sys
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
from resbibman.confReader import getConfV
from resbibman.core.dataClass import DataBase, DataPoint
from resbibman.core.fileToolsV import FileManipulatorVirtual, FileManipulator

addr = "http://{}:{}".format(getConfV("host"), getConfV("port"))

flist_addr = "{}/filelist/%".format(addr)

flist = requests.get(flist_addr).text

flist = json.loads(flist)["data"]

db = DataBase()
db.constuct(flist)
# vfm = FileManipulatorVirtual("/tmp/ResBibMan/Database/2022-sss-ttt")
# vfm.screen()
# db.add(DataPoint(vfm))

uuid = "daf5a770-be8e-4563-8dfd-a75c3c8e9896"
# db[uuid].fm._download()

print(db)

# db[uuid].fm._upload()
db[uuid].fm._deleteRemote()
