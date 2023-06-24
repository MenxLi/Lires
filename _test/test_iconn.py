from resbibman.core.serverConn import ServerConn, IServerConn

iconn = IServerConn(host="192.168.124.11")
print(iconn.status)
print(iconn.featurize("hello"))
#  print(iconn.queryFeatureIndex("hello"))
# res = iconn.chat("Tell me a joke", model_name="gpt-4")
# if res:
#     for i in res:
#         print(i, end="", flush=True)
