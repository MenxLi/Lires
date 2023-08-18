from lires.core.serverConn import ServerConn, IServerConn

conn = ServerConn()
print(conn.permission())
print(conn.summaries(["xx"]))

iconn = IServerConn()
print(iconn.status)
# print(iconn.featurize("hello"))
print(iconn.queryFeatureIndex("hello"))
res = iconn.chat("Tell me a joke", model_name="gpt-4")
if res:
    for i in res:
        print(i, end="", flush=True)