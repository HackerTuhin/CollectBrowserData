from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime
import json

app = FastAPI()

# In-memory storage
browser_data_storage: List[dict] = []

# Pydantic model to match frontend data structure
class BrowserData(BaseModel):
    meta: Dict[str, Any]
    basicinfo: Dict[str, Any]
    screeninfo: Dict[str, Any]
    browserinfo: Dict[str, Any]
    hardwareinfo: Dict[str, Any]
    networkinfo: Dict[str, Any]
    fontdetection: Any
    canvasfingerprint: Any
    webglinfo: Dict[str, Any]
    audiofingerprint: Any
    batteryinfo: Dict[str, Any]
    geolocation: Dict[str, Any]
    mediadevices: Any
    permissions: Dict[str, Any]
    storageinfo: Dict[str, Any]
    cpubenchmark: Dict[str, Any]
    localips: Any
    fingerprintjs: Dict[str, Any]

# Endpoint to receive data from client
@app.post("/collect")
async def collect(data: BrowserData):
    entry = data.dict()
    entry["server_received_time"] = datetime.utcnow().isoformat()
    browser_data_storage.append(entry)
    return {"status": "success", "count": len(browser_data_storage)}

# Endpoint to serve the viewer HTML
@app.get("/view", response_class=HTMLResponse)
async def view():
    return FileResponse("app/static/view.html")

# Endpoint to return JSON data for viewer
@app.get("/data")
async def get_data():
    return JSONResponse(content=browser_data_storage)

# Mount static assets (HTML)
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")

# Mount JS separately
app.mount("/js", StaticFiles(directory="app/static"), name="js")
