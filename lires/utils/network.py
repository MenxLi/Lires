import socket

def getLocalIP() -> tuple[str, int]:
    """
    Find an available address for the socket.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("", 0))
    local_ip, port = sock.getsockname()
    sock.close()
    return local_ip, port