from resbibman.core.serverConn import ServerConn


conn = ServerConn()
print(conn.permission())
print(conn.filelist(["xx"]))