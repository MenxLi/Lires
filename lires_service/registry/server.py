
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
import uvicorn
from pydantic import BaseModel
from typing import Optional
from .store import RegistryStore, ServiceName

g_store: RegistryStore
app = FastAPI()

class RegisterRequest(BaseModel):
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
    print(req)
    g_store.register(req.name, req.endpoint, req.description, req.group)
    return {
        "status": "ok",
        }

@app.post("/get")
def get(req: GetRequest):
    info = g_store.get(req.name, req.group)
    if info is None:
        raise HTTPException(status_code=404, detail="Service not found")
    else:
        return info

def startServer(host: str, port: int):
    global g_store
    g_store = RegistryStore()
    uvicorn.run(
        app, host=host, port=port, log_level="debug", workers=1,
    )