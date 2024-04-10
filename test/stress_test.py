import sys
from lires.user import encrypt
from lires.api import ServerConn
from lires.utils import Timer
import asyncio

N_CONCURRENT = 10
SEMAPHORE = asyncio.Semaphore(N_CONCURRENT)
async def makeRequest(conn: ServerConn) -> bool:
    # when the server do status check, it will check avaliable documents, uptime, number of connections, etc.
    # the server will also check if the token is valid and make some log
    # so this is a good way to stress test the server
    try:
        async with SEMAPHORE:
            await conn.status()
        return True
    except Exception as e:
        print(e)
        return False

async def main(username: str, password: str):
    token = encrypt.encryptKey(username, encrypt.generateHexHash(password))
    conn = ServerConn(token=token, endpoint="http://localhost:8080")
    n_req = 1000
    with Timer(f"{n_req} requests (concurrent {N_CONCURRENT})"):
        res = await asyncio.gather(*[makeRequest(conn) for _ in range(n_req)])
    print(f"Success: {res.count(True)} / {n_req}")

if __name__ == "__main__":

    try:
        username, password = sys.argv[1], sys.argv[2]
    except IndexError:
        print("Usage: stress_test.py <username> <password>")
        exit(1)
    asyncio.run(main(username, password))