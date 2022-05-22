import requests, json, os
from resbibman.confReader import getConfV, TMP_DIR
from resbibman.core.utils import openFile
from resbibman.core.dataClass import DataBase, DataPoint
from resbibman.core.fileToolsV import FileManipulatorVirtual
from resbibman.core.encryptClient import generateHexHash
from RBMWeb.cmd.manageKey import deleteKey, registerKey
from RBMWeb.backend.encryptServer import queryHashKey

my_key = "123"
enc_key = generateHexHash(my_key)
if not queryHashKey(enc_key):
    registerKey(my_key)
    print("registered key")

if queryHashKey(enc_key):
    print("Successfully validated.")


# test
addr = "http://{}:{}".format(getConfV("host"), getConfV("port"))
flist_addr = "{}/filelist/%".format(addr)

req_params = {
    "key": enc_key
}

res = requests.get(flist_addr, params=req_params)
print(res.status_code)
if res.status_code == 401:
    print("Unauthorized")
elif res.ok:
    print("success")
    flist = res.text

# Bad request
res = requests.get(flist_addr, params={"key": "123"})
print(res.status_code)
if res.status_code == 401:
    print("Unauthorized")

flist = json.loads(flist)["data"]

db = DataBase()
db.constuct(flist)
print(db)



##==================Test post
cmd = "hello"
file_post_addr = "{}/file".format(addr)
uuid = "ffe75f2f-5ecc-48f4-86ab-d98797c3d7c9"

# Dowload
post_args = {
    "key": enc_key,
    "cmd": "download",
    "uuid": uuid
}
res = requests.post(file_post_addr, params=post_args)
out_file = os.path.join(TMP_DIR, uuid+".zip")
with open(out_file, "wb") as fp:
    fp.write(res.content)
print(out_file)


deleteKey(my_key)