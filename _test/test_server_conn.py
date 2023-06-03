from resbibman.core.serverConn import ServerConn, iServerConn

conn = ServerConn()
print(conn.permission())
print(conn.filelist(["xx"]))

iconn = iServerConn()
print(iconn.status)
# print(iconn.featurize("hello"))
print(iconn.queryFeatureIndex("hello"))
res = iconn.chat("Tell me a joke")
if res:
    for i in res:
        print(i, end="", flush=True)