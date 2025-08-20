import requests

def get_news(ticker):
    response = requests.get("http://localhost:8003/headlines", params={"ticker": ticker})
    return response.json()
