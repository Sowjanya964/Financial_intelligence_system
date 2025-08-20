
## 🧠 Description:
A modular financial intelligence system using FastAPI agents and HTTP communication, with MCP wrappers for interoperability.

## 📦 Components:
- `api/`: User-facing query entry point.
- `orchestrator/`: LLM-powered orchestration layer.
- `agents/`: Ticker lookup, price fetching, news crawling, and sentiment analysis agents.
- `mcp_adapters/`: Wrappers for MCP calls.

## 🚀 How to Run:

pip install -r requirements.txt

# Terminal 1: DuckDuckGo Agent
uvicorn agents.duckduckgo_agent.app:app --port 8001

# Terminal 2: YFinance Agent
uvicorn agents.yfinance_agent.app:app --port 8002

# Terminal 3: News Agent
uvicorn agents.news_agent.app:app --port 8003

# Terminal 4: Sentiment Agent
uvicorn agents.sentiment_agent.app:app --port 8004

# Terminal 5: Orchestrator
uvicorn orchestrator.stock_assistant:app --port 8000


