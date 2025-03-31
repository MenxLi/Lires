"""
Microservices for Lires
"""

def avaliablePort():
    from lires.config import getConf
    from lires.utils.network import get_free_port
    port_low, port_high = getConf()["service_port_range"]
    return get_free_port(port_low, port_high)