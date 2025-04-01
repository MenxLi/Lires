"""
Microservices for Lires
"""

def avaliablePort():
    from lires.config import get_conf
    from lires.utils.network import get_free_port
    port_low, port_high = get_conf()["service_port_range"]
    return get_free_port(port_low, port_high)