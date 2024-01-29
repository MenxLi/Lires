import sys
from lires.user import encrypt
from lires.api import ServerConn
from lires.utils import Timer
import asyncio, multiprocessing

async def makeRequest(conn: ServerConn) -> bool:
    # when the server do status check, it will check avaliable documents, uptime, number of connections, etc.
    # the server will also check if the token is valid and make some log
    # so this is a good way to stress test the server
    try:
        await conn.status()
        return True
    except Exception as e:
        print(e)
        return False

N_CONCURRENT = 10
def run(conn):
    global N_CONCURRENT
    async def makeConcurrentRequests():
        # send 10 requests concurrently
        return await asyncio.gather(*[makeRequest(conn) for _ in range(N_CONCURRENT)])
    return asyncio.run(makeConcurrentRequests())

if __name__ == "__main__":

    try:
        username, password = sys.argv[1], sys.argv[2]
    except IndexError:
        print("Usage: stress_test.py <username> <password>")
        exit(1)

    token = encrypt.encryptKey(username, encrypt.generateHexHash(password))
    conn = ServerConn(token, "http://localhost:8080")

    n_req = 100
    conn_pool = [conn] * n_req
    with multiprocessing.Pool(4) as pool:
        with Timer(f"{n_req} * {N_CONCURRENT} requests"):
            res = pool.map(run, conn_pool)
    
    __all_res = []
    for _res in res:
        __all_res.extend(_res)
    print(f"Success: {__all_res.count(True)} / {len(__all_res)}")