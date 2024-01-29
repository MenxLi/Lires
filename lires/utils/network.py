import socket, random, asyncio, time
from typing import TypeVar, Callable, Coroutine

def getLocalIP() -> tuple[str, int]:
    """
    Find an available address for the socket.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("", 0))
    local_ip, port = sock.getsockname()
    sock.close()
    return local_ip, port

def getFreePort(low: int = 0, high: int = 65535) -> int:
    """
    Find an available port in the range [low, high).
    """
    assert low < high
    max_try = 100
    while True:
        port = random.randint(low, high-1)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(("", port))
            sock.close()
            return port
        except OSError as e:
            if max_try == 0:
                raise RuntimeError("Cannot find an available port in the range [{}, {})".format(low, high))
            else:
                print("Port {} is not available, try again... ({})".format(port, e))
                max_try -= 1

FuncT = TypeVar("FuncT", bound=Callable[..., Coroutine])
def minResponseInterval(min_interval=0.1):
    """
    Decorator to limit the minimum interval between responses
    """
    last_response_time = 0
    def decorator(func: FuncT) -> FuncT:
        assert asyncio.iscoroutinefunction(func), "minResponseInterval only works with async functions"
        async def wrapper(*args, **kwargs):
            nonlocal last_response_time
            while True:
                now = time.time()
                if now - last_response_time < min_interval:
                    await asyncio.sleep(min_interval - (now - last_response_time))
                else:
                    break
            last_response_time = time.time()
            return await func(*args, **kwargs)
        return wrapper  # type: ignore
    return decorator
