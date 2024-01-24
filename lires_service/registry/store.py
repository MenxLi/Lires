
from typing import TypedDict, Literal, Optional
import asyncio
import aiohttp
import aiohttp.client_exceptions
import random
from lires.utils import setupLogger

# will add more service in the future
ServiceName = Literal["ai", "log"]

class Registration(TypedDict):
    """
    Register information
    """
    uid: str
    name: ServiceName
    endpoint: str
    description: str
    group: Optional[str]        # group name, specifies which database the service is using

def formatRegistration(reg: Registration):
    return f"[{reg['name'].rjust(6)} | {reg['uid'][:8]}] {reg['endpoint']} (g: {reg['group']})"

class RegistryStore:
    """
    A service registry that stores all services' information, should be a singleton,
    Periodically ping the registry server to update the registry
    """
    logger = setupLogger(
        "registry-store",
        term_id = "registry",
        term_log_level="DEBUG",
        )
    def __init__(self):
        self._data: dict[str, list[Registration]] = {}

        # assure singleton
        assert not hasattr(self.__class__, "_registry_init_done"), "Register should be a singleton"
        setattr(self.__class__, "_registry_init_done", True)
    
    @property
    def data(self):
        return self._data
    
    def register(self, info: Registration):
        """
        Register a service
        """
        name = info["name"]
        if name not in self._data:
            self._data[name] = []
        self._data[name].append(info)
        self.logger.info("Registered service: " + formatRegistration(info))
    
    def get(self, name: ServiceName, require_group: Optional[str] = None) -> Optional[Registration]:
        """
        Get a service's information
        """
        if name not in self._data:
            self.logger.debug("Service {} not found".format(name))
            return None
        eligible_service = []
        if require_group is None:
            # balance load
            eligible_service = self._data[name]
        else:
            for info in self._data[name]:
                if info["group"] == require_group:
                    eligible_service.append(info)
        if len(eligible_service) == 0:
            self.logger.debug("Service {} not found".format(name))
            return None
        else:
            ret = random.choice(eligible_service)
            self.logger.debug("Get service {}".format(formatRegistration(ret)))
            return ret
    
    async def ping(self):
        """
        Ping the registry server to update the registry
        """
        async def pingEndpoint(endpoint: str) -> bool:
            try:
                timeout = 5
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                            endpoint + "/status",
                            timeout = timeout
                        ) as res:
                        if res.status == 200:
                            return True
                        elif res.status == 404:
                            self.logger.warning("Service {} should implement /status endpoint".format(endpoint))
                            return True
                        elif res.status == 401 or res.status == 403:
                            self.logger.warning("Service {} requires authentication".format(endpoint))
                            return True
                        else:
                            self.logger.debug("Ping {} failed (status code: {})".format(endpoint, res.status))
                            return False
            except (aiohttp.ClientConnectorError, aiohttp.client_exceptions.ClientConnectorError, asyncio.TimeoutError) as e:
                self.logger.debug("Ping {} failed due to exception".format(endpoint))
                return False

        for name in self._data:
            for info in self._data[name]:
                if not await pingEndpoint(info["endpoint"]):
                    self.logger.info("Service {}-{} is dead".format(info["name"], info["endpoint"]))
                    self._data[name].remove(info)