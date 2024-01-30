
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
        self._data: dict[str, list[Registration]] = {}  # key: service name, value: list of registrations
        self._dead_data: dict[str, Registration] = {}   # key: service uid, value: registration

        # last activation time of each service, key: registration uid, value: timestamp
        self._last_activation_time: dict[str, float] = {}
        self._inactive_timeout = 60

        # assure singleton
        assert not hasattr(self.__class__, "_registry_init_done"), "Register should be a singleton"
        setattr(self.__class__, "_registry_init_done", True)
    
    @property
    def data(self):
        return self._data
    
    async def register(self, info: Registration):
        """
        Register a service
        """
        name = info["name"]
        # check if the same ip is already registered, 
        # if so, remove the old one, as it should be a restart / update
        for _name_all in self._data:
            for _info in self._data[_name_all]:
                if _info["endpoint"] == info["endpoint"]:
                    self.logger.info("Service {} already registered, will be replaced".format(formatRegistration(info)))
                    self._data[_name_all].remove(_info)
        if name not in self._data:
            self._data[name] = []
        self._data[name].append(info)
        self._last_activation_time[info["uid"]] = asyncio.get_running_loop().time()
        self.logger.info("Registered service: " + formatRegistration(info))
    
    async def get(self, name: ServiceName, require_group: Optional[str] = None) -> Optional[Registration]:
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
    
    async def touch(self, uid: str) -> bool:
        """
        Touch a service, update the last activation time
        return if the service is alive (if the service is not registered, return False)
        """
        self.logger.debug("Heartbeat from service {}".format(uid))
        self._last_activation_time[uid] = asyncio.get_running_loop().time()
        if uid in self._dead_data:
            # restore the service
            info = self._dead_data.pop(uid)
            await self.register(info)
        for name in self._data:
            for info in self._data[name]:
                if info["uid"] == uid:
                    return True
        return False
    
    async def _getInactive(self, timeout: float) -> list[str]:
        """
        Get inactive services
        """
        ret = []
        for uid in self._last_activation_time:
            if asyncio.get_running_loop().time() - self._last_activation_time[uid] > timeout:
                ret.append(uid)
        return ret
    
    async def _remove(self, uids: list[str], backup: bool = True):
        """
        Remove services
        """
        for uid in uids:
            for service_name in self._data:
                for info in self._data[service_name]:
                    if info["uid"] != uid:
                        continue
                    self._data[service_name].remove(info)
                    if backup:
                        self._dead_data[uid] = info
                    self.logger.info("Remove service: {} | {}".format(formatRegistration(info), "inactive" if backup else "dead"))

            if uid in self._last_activation_time:
                self._last_activation_time.pop(uid)
    
    async def autoClean(self):
        __all_inactive = await self._getInactive(self._inactive_timeout)
        await self._remove(__all_inactive, backup=True)

        __all_long_inactive = await self._getInactive(self._inactive_timeout * 10)
        await self._remove(__all_long_inactive, backup=False)

    async def withdraw(self, uid: str):
        """
        Withdraw a service
        """
        if uid in self._dead_data:
            self._dead_data.pop(uid)
        await self._remove([uid], backup=False)