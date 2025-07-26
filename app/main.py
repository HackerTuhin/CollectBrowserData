from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI()

# Mount static folder
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")

# In-memory storage
browser_data_storage: List[dict] = []

# Pydantic model for validation
class BrowserData(BaseModel):
    userAgent: str
    language: str
    platform: str
    cookiesEnabled: bool
    screen: dict
    time: str

@app.post("/collect")
async def collect_data(data: BrowserData):
    browser_data_storage.append(data.dict())
    return {"status": "received", "total": len(browser_data_storage)}

@app.get("/view", response_class=HTMLResponse)
async def view_data():
    html = "<h1>Collected Browser Data</h1><ul>"
    for entry in browser_data_storage:
        html += f"<li><pre>{entry}</pre></li>"
    html += "</ul>"
    return HTMLResponse(content=html)
