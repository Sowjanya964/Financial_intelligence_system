# agents/mcp_adapters/sentiment_mcp.py
from fastapi import FastAPI
import requests

app = FastAPI()

@app.post("/mcp/sentiment")
def mcp_sentiment(data: dict):
    resp = requests.post("http://localhost:8004/analyze", json=data)
    return resp.json()
