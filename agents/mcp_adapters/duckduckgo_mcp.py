# agents/mcp_adapters/duckduckgo_mcp.py
from fastapi import FastAPI
import requests

app = FastAPI()

@app.post("/mcp/duckduckgo")
def mcp_duckduckgo(data: dict):
    ticker = data.get("ticker")
    resp = requests.get(f"http://localhost:8001/search", params={"ticker": ticker})
    return resp.json()
