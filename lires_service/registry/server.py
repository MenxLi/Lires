
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
import asyncio
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional
from ..entry import start_service
from .store import RegistryStore, ServiceName

@asynccontextmanager
async def lifespan(app: FastAPI):
    interval = 10
    def _autoClean():
        asyncio.create_task(g_store.autoClean())
        asyncio.get_event_loop().call_later(interval, _autoClean)
    asyncio.get_event_loop().call_later(interval, _autoClean)
    yield
g_store: RegistryStore
app = FastAPI(lifespan=lifespan)

class RegisterRequest(BaseModel):
    uid: str
    name: ServiceName
    endpoint: str
    description: str
    group: Optional[str]
class GetRequest(BaseModel):
    name: ServiceName
    group: Optional[str]

class HeartbeatRequest(BaseModel):
    uid: str

class WithdrawRequest(BaseModel):
    uid: str

@app.get("/status")
def status():
    return { "status": "ok", }

@app.get("/view")
async def view():
    return g_store.view()

@app.post("/register")
async def register(req: RegisterRequest):
    await g_store.register(req.model_dump())    # type: ignore
    return { "status": "ok", }

@app.post("/heartbeat")
async def heartbeat(req: HeartbeatRequest):
    is_alive = await g_store.touch(req.uid)
    if is_alive:
        return { "status": "ok", }
    else:
        raise HTTPException(status_code=404, detail="Service not found")

@app.post("/query")
async def query(req: GetRequest):
    info = await g_store.get(req.name, req.group)
    if info is None:
        raise HTTPException(status_code=404, detail=f"Service {req.name} (g: {req.group}) not found")
    else:
        return info

@app.post("/withdraw")
async def withdraw(req: WithdrawRequest):
    await g_store.withdraw(req.uid)
    return { "status": "ok", }

async def start_server(host: str, port: int):
    global g_store
    g_store = RegistryStore()
    await start_service(
        app = app,
        host = host,
        port = port,
    )
