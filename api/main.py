from fastapi import FastAPI, HTTPException
import requests

app = FastAPI(title="Financial Insights API (Proxy)")

ORCH_URL = "http://localhost:8000/insights"

@app.post("/insights")
def proxy_insights(body: dict):
    try:
        r = requests.post(ORCH_URL, json=body, timeout=20)
        return r.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
