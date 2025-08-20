import requests
import pika
from common.utils import make_connection, safe_json, parse_json
from config.settings import NEWS_QUEUE, SERP_API_KEY

def fetch_news_serpapi(ticker: str):
    if not SERP_API_KEY:
        return []
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_news",
        "q": f"{ticker} stock",
        "api_key": SERP_API_KEY,
        "num": "10",
        "hl": "en"
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    results = data.get("news_results", []) or data.get("articles", []) or []
    headlines = []
    for item in results:
        title = item.get("title") or item.get("headline")
        if title:
            headlines.append(title.strip())
    # dedupe quick
    seen = set()
    deduped = []
    for h in headlines:
        key = h.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(h)
    return deduped[:10]

def handle_news_task(ch, method, properties, body):
    msg = parse_json(body)
    ticker = msg.get("ticker", "").upper()

    result = {
        "type": "news",
        "ticker": ticker,
        "headlines": []
    }
    try:
        result["headlines"] = fetch_news_serpapi(ticker)
    except Exception as e:
        result["error"] = f"{e}"

    reply_to = properties.reply_to
    corr_id = properties.correlation_id
    if reply_to:
        ch.basic_publish(
            exchange="",
            routing_key=reply_to,
            properties=pika.BasicProperties(correlation_id=corr_id, delivery_mode=2),
            body=safe_json(result)
        )
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    conn = make_connection()
    ch = conn.channel()
    ch.queue_declare(queue=NEWS_QUEUE, durable=True)
    ch.basic_qos(prefetch_count=1)
    ch.basic_consume(queue=NEWS_QUEUE, on_message_callback=handle_news_task, auto_ack=False)
    print("[news_agent] Waiting for news tasks...")
    ch.start_consuming()

if __name__ == "__main__":
    main()
