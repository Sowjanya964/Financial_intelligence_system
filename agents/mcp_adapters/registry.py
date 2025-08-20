# agents/mcp_adapters/registry.py
AGENT_REGISTRY = {
    "duckduckgo": "http://localhost:8001/search",
    "yfinance": "http://localhost:8002/price",
    "news": "http://localhost:8003/news",
    "sentiment": "http://localhost:8004/analyze"
}

def get_agent_url(name: str):
    return AGENT_REGISTRY.get(name)
