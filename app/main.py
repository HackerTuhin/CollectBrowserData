from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime
import os
import json

app = FastAPI()

# In-memory storage
browser_data_storage: List[dict] = []

# Pydantic model to match full structure of `collectedInfo` from the frontend
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

@app.post("/collect")
async def collect(data: BrowserData):
    entry = data.dict()
    entry["server_received_time"] = datetime.utcnow().isoformat()
    browser_data_storage.append(entry)

    return {"status": "success", "count": len(browser_data_storage)}

@app.get("/view", response_class=HTMLResponse)
async def view():
    html = "<h2>Submitted Browser Data (In-Memory)</h2><ul>"
    for item in browser_data_storage:
        html += f"<li><pre>{json.dumps(item, indent=2)}</pre></li>"
    html += "</ul>"
    return HTMLResponse(content=html)

# Serve static files (your index.html must be in app/static)
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
