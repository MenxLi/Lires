
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
import asyncio
import uvicorn
from pydantic import BaseModel
from typing import Optional
from .store import RegistryStore, ServiceName

g_store: RegistryStore
app = FastAPI()

class RegisterRequest(BaseModel):
    uid: str
    name: ServiceName
    endpoint: str
    description: str
    group: Optional[str]
class GetRequest(BaseModel):
    name: ServiceName
    group: Optional[str]

@app.get("/status")
def status():
    return {
        "status": "ok",
        }

@app.post("/register")
def register(req: RegisterRequest):
    g_store.register(req.dict())    # type: ignore
    return {
        "status": "ok",
        }

@app.post("/query")
def query(req: GetRequest):
    info = g_store.get(req.name, req.group)
    if info is None:
        raise HTTPException(status_code=404, detail="Service not found")
    else:
        return info

@app.on_event("startup")
async def startup_event():
    # ping the registry server periodically
    interval = 10
    def ping():
        asyncio.create_task(g_store.ping())
        asyncio.get_event_loop().call_later(interval, ping)
    asyncio.get_event_loop().call_later(interval, ping)

def startServer(host: str, port: int):

    global g_store
    g_store = RegistryStore()

    uvicorn.run(
        app, host=host, port=port, log_level="debug", access_log=False
    )