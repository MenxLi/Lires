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
        self.__do_heartbeat = False
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
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url + "/status") as res:
                self.ensureRes(res)
                return await res.json()
        
    async def view(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url + "/view") as res:
                self.ensureRes(res)
                return await res.json()
    
    async def get(self, name: ServiceName, group: Optional[str] = None) -> Registration:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url + "/query",
                json = {
                    "name": name,
                    "group": group,
                }
            ) as res:
                self.ensureRes(res)
                return await res.json()
    
    async def _register(self, info: Registration, ensure_status: bool = True):
        if ensure_status:
            try:
                await self.status()
            except aiohttp.client_exceptions.ClientConnectorError:
                exit("ERROR: Registry server not running")

        self._uid = info["uid"]
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url + "/register",
                json = info
            ) as res:
                self.ensureRes(res)
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
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url + "/heartbeat",
                    json = {
                        "uid": self.uid,
                    }
                ) as res:
                    self.ensureRes(res)
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
        self.__do_heartbeat = True
        def heartbeatThread():
            while self.__do_heartbeat:
                self.run_sync(self.heartbeat(on_fail))
                time.sleep(self.HEARTBEAT_INTERVAL)
        threading.Thread(target=heartbeatThread, daemon=True).start()
    
    async def withdraw(self):
        # stop heartbeat loop
        if self.__heatbeat_thread is not None:
            self.__do_heartbeat = False
            self.__heatbeat_thread.join()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url + "/withdraw",
                    json = {
                        "uid": self.uid,
                    }
                ) as res:
                    self.ensureRes(res)
        except Exception as e:
            print("ERROR: Failed to withdraw: {}".format(e))
