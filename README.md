# Financial Insights System — RabbitMQ A2A

## Overview
FastAPI orchestrator + RabbitMQ workers (agents):
- yfinance → price & daily change %
- news → latest headlines (SerpAPI optional)
- sentiment → TextBlob polarity summary
- (optional) duckduckgo → company → ticker lookup

## Start RabbitMQ

Windows Service: start RabbitMQ from Services

(Optional) enable UI: rabbitmq-plugins.bat enable rabbitmq_management

UI at http://localhost:15672 (guest/guest)

## Install
```powershell
cd "E:\Finance Intelligent System"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Terminal A
.\venv\Scripts\Activate.ps1
python -m agents.yfinance_agent.app

# Terminal B
.\venv\Scripts\Activate.ps1
python -m agents.news_agent.app

# Terminal C
.\venv\Scripts\Activate.ps1
python -m agents.sentiment_agent.app

# (Optional) Terminal D - only if you use company→ticker
.\venv\Scripts\Activate.ps1
python -m agents.duckduckgo_agent.app

# Terminal D 
.\venv\Scripts\Activate.ps1
uvicorn orchestrator.stock_assistant:app --port 8000 --reload

```

## Call from Postman

Method: POST

URL: http://localhost:8000/insights

Headers: Content-Type: application/json

Body (raw JSON):

{ "ticker": "NVDA" }



