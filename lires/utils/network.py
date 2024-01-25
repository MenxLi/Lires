import socket, random

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