
from typing import TypedDict, Literal, Optional
import random

# will add more service in the future
ServiceName = Literal["ai", "log"]

class Registration(TypedDict):
    """
    Register information
    """
    name: ServiceName
    endpoint: str
    description: str
    group: Optional[str]        # group name, specifies which database the service is using

class RegistryStore:
    """
    A service registry that stores all services' information, should be a singleton
    """
    def __init__(self):
        self._data: dict[str, list[Registration]] = {}

        # assure singleton
        assert not hasattr(self.__class__, "_registry_init_done"), "Register should be a singleton"
        setattr(self.__class__, "_registry_init_done", True)
    
    @property
    def data(self):
        return self._data
    
    def register(self, name: ServiceName, endpoint: str, description: str, group: Optional[str] = None):
        """
        Register a service
        """
        info: Registration = {
            "name": name,
            "endpoint": endpoint,
            "description": description,
            "group": group,
        }
        if name not in self._data:
            self._data[name] = []
        self._data[name].append(info)
    
    def get(self, name: ServiceName, require_group: Optional[str] = None) -> Optional[Registration]:
        """
        Get a service's information
        """
        if name not in self._data:
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
            return None
        else:
            return random.choice(eligible_service)