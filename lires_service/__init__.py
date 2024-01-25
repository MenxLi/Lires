"""
Microservices for Lires
"""

def avaliablePort():
    from lires.config import getConf
    from lires.utils.network import getFreePort
    port_low, port_high = getConf()["service_port_range"]
    return getFreePort(port_low, port_high)