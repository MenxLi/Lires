from resbibman.core.serverConn import ServerConn, IServerConn

conn = ServerConn()
print(conn.permission())
print(conn.filelist(["xx"]))

iconn = IServerConn()
print(iconn.status)
# print(iconn.featurize("hello"))
print(iconn.queryFeatureIndex("hello"))
res = iconn.chat("Tell me a joke")
if res:
    for i in res:
        print(i, end="", flush=True)