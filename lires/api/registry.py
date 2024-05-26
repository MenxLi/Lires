from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable, Any
import aiohttp, asyncio, time, threading
import aiohttp.client_exceptions
from .common import LiresAPIBase
if TYPE_CHECKING:
    from lires_service.registry import ServiceName, Registration

    
class RegistryConn(LiresAPIBase):
    HEARTBEAT_INTERVAL = 5
    def __init__(self):
        self._uid: str | None = None
        self.__register_info: Registration | None = None
        self.__do_heartbeat: threading.Event = threading.Event()
        self.__heatbeat_thread: Optional[threading.Thread] = None
    
    @property
    def uid(self) -> str:
        assert self._uid is not None, "RegistryConn not initialized"
        return self._uid
    
    @property
    def url(self):
        # TODO: get from env
        return "http://localhost:8700"
    
    async def status(self):
        return await self.fetcher.get(self.url + "/status")
        
    async def view(self):
        return await self.fetcher.get(self.url + "/view")
    
    async def get(self, name: ServiceName, group: Optional[str] = None) -> Registration:
        try:
            return await self.fetcher.post(
                self.url + "/query",
                json = {
                    "name": name,
                    "group": group,
                }
            )
        except self.Error.LiresResourceNotFoundError as e:
            raise self.Error.LiresResourceNotFoundError(f"Service {name} (g: {group}) not found at registry: {self.url}")
    
    async def _register(self, info: Registration, ensure_status: bool = True):
        if ensure_status:
            try:
                await self.status()
            except aiohttp.client_exceptions.ClientConnectorError:
                exit("ERROR: Registry server not running")

        self._uid = info["uid"]
        await self.fetcher.post(self.url + "/register", json = dict(info))
        self.__register_info = info
    
    async def register(self, info: Registration, ensure_status: bool = True, start_heartbeat: bool = True):
        if ensure_status:
            try:
                await self.status()
            except aiohttp.client_exceptions.ClientConnectorError:
                exit("ERROR: Registry server not running")

            await self._register(info, ensure_status)
        if start_heartbeat:
            self.startHeartbeatThread(on_fail=lambda e: print("ERROR: Failed to heartbeat: {}".format(e)))
    
    async def heartbeat(self, on_fail: Optional[Callable[[str], Any]] = None):
        try:
            await self.fetcher.post(
                self.url + "/heartbeat",
                json = {
                    "uid": self.uid,
                }
            )
        except self.Error.LiresResourceNotFoundError as e:
            # registry server restarted, re-register
            assert self.__register_info is not None
            await self._register(self.__register_info, ensure_status=False)
        except Exception as e:
            if on_fail is not None:
                if asyncio.iscoroutinefunction(on_fail):
                    await on_fail(str(e))
                else:
                    on_fail(str(e))
            else:
                raise e
    
    def startHeartbeatThread(self, on_fail: Optional[Callable[[str], Any]] = None):
        self.__do_heartbeat.set()

        def heartbeatThread():
            sleep_step = 0.1
            while self.__do_heartbeat.is_set():
                self.run_sync(self.heartbeat(on_fail))
                # split the sleep into smaller steps to allow quick stop
                for _ in range(max(int(self.HEARTBEAT_INTERVAL / sleep_step), 1)):
                    if self.__do_heartbeat.is_set():
                        time.sleep(sleep_step)
                
        self.__heatbeat_thread = threading.Thread(target=heartbeatThread, daemon=True)
        self.__heatbeat_thread.start()
    
    async def withdraw(self):
        # stop heartbeat loop
        if self.__heatbeat_thread is not None:
            self.__do_heartbeat.clear()
            self.__heatbeat_thread.join()
        try:
            await self.fetcher.post(
                self.url + "/withdraw",
                json = {
                    "uid": self.uid,
                }
            )
        except Exception as e:
            print("ERROR: Failed to withdraw: {}".format(e))
