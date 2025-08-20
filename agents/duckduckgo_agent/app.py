import pika
import requests
from common.utils import make_connection, safe_json, parse_json
from config.settings import SERP_API_KEY

Q_DDG = "duckduckgo_queue"  # name for this queue if you choose to use it

def lookup_company_to_ticker(query: str):
    """
    Try to use SerpAPI Google Finance to normalize company query → ticker.
    Falls back to returning the original query uppercased if no key or failure.
    """
    if not SERP_API_KEY:
        return query.upper(), query
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_finance",
        "q": query,
        "api_key": SERP_API_KEY
    }
    r = requests.get(url, params=params, timeout=15)
    data = r.json()
    finance = data.get("finance_results", {})
    ticker = finance.get("ticker") or query.upper()
    title = finance.get("title") or query
    return ticker, title

def handle_ddg_task(ch, method, properties, body):
    msg = parse_json(body)
    query = msg.get("query", "")
    ticker, company = lookup_company_to_ticker(query)
    result = {"type": "duckduckgo", "query": query, "ticker": ticker, "company": company}

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
    ch.queue_declare(queue=Q_DDG, durable=True)
    ch.basic_qos(prefetch_count=1)
    ch.basic_consume(queue=Q_DDG, on_message_callback=handle_ddg_task, auto_ack=False)
    print("[duckduckgo_agent] Waiting for ddg tasks...")
    ch.start_consuming()

if __name__ == "__main__":
    main()
