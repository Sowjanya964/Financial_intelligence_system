
'''# API Keys - you must add these yourself
SERP_API_KEY = "a96ac634d7a7c9dc842193a085ba04b36114a9b158b4acf1c9327f7038a1e7fe"
NEWS_API_KEY = "23f6f075064e476d9bc1373b16af3b79"
'''

# config/settings.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# -------------------------------
# RabbitMQ Configuration
# -------------------------------
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

# -------------------------------
# External API Keys
# -------------------------------
SERP_API_KEY = "a96ac634d7a7c9dc842193a085ba04b36114a9b158b4acf1c9327f7038a1e7fe"   # For DuckDuckGo / SerpAPI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # For sentiment analysis (GPT)
NEWS_API_KEY = "23f6f075064e476d9bc1373b16af3b79"   # For News API

# -------------------------------
# Queues (Standardized across system)
# -------------------------------
DUCKDUCKGO_QUEUE = "duckduckgo_queue"
YFINANCE_QUEUE = "yfinance_queue"
NEWS_QUEUE = "news_queue"
SENTIMENT_QUEUE = "sentiment_queue"
ORCHESTRATOR_QUEUE = "orchestrator_queue"

# -------------------------------
# Logging Config
# -------------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
