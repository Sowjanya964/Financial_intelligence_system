# agents/mcp_adapters/yfinance_mcp.py
from fastapi import FastAPI
import requests

app = FastAPI()

@app.post("/mcp/yfinance")
def mcp_yfinance(data: dict):
    ticker = data.get("ticker")
    resp = requests.get(f"http://localhost:8002/price", params={"ticker": ticker})
    return resp.json()
