from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List

app = FastAPI()

# In-memory storage
browser_data_storage: List[dict] = []

class BrowserData(BaseModel):
    userAgent: str
    language: str
    platform: str
    cookiesEnabled: bool
    screen: dict
    time: str

@app.post("/collect")
async def collect(data: BrowserData):
    browser_data_storage.append(data.dict())
    return {"status": "success", "count": len(browser_data_storage)}

@app.get("/view", response_class=HTMLResponse)
async def view():
    html = "<h2>Submitted Browser Data</h2><ul>"
    for item in browser_data_storage:
        html += f"<li><pre>{item}</pre></li>"
    html += "</ul>"
    return HTMLResponse(content=html)

# 🔥 This MUST be defined LAST
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
