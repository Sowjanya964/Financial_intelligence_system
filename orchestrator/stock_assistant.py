from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import time
import pika

from common.utils import make_connection, safe_json, parse_json
from common.schemas import InsightRequest
from config.settings import YFINANCE_QUEUE, NEWS_QUEUE, SENTIMENT_QUEUE

app = FastAPI(title="Financial Insights Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Aggregator:
    def __init__(self):
        self.results = {
            "price": None,
            "news": None,
            "sentiment": None
        }
        self.sentiment_dispatched = False

    def complete(self) -> bool:
        return (
            self.results["price"] is not None and
            self.results["news"] is not None and
            self.results["sentiment"] is not None
        )

@app.post("/insights")
def insights(req: InsightRequest):
    ticker = req.ticker.strip().upper()
    correlation_id = str(uuid.uuid4())

    conn = make_connection()
    ch = conn.channel()

    # declare target queues (idempotent)
    ch.queue_declare(queue=YFINANCE_QUEUE, durable=True)
    ch.queue_declare(queue=NEWS_QUEUE, durable=True)
    ch.queue_declare(queue=SENTIMENT_QUEUE, durable=True)

    # Per-request exclusive callback queue
    cb = ch.queue_declare(queue="", exclusive=True)
    callback_queue = cb.method.queue

    # aggregator to collect results
    agg = Aggregator()

    # Consumer callback
    def on_reply(_ch, method, properties, body):
        if properties.correlation_id != correlation_id:
            _ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        msg = parse_json(body)
        msg_type = msg.get("type")

        if msg_type == "price":
            agg.results["price"] = msg

        elif msg_type == "news":
            # dedupe headlines, keep top 10
            headlines = msg.get("headlines", [])
            seen = set()
            deduped = []
            for h in headlines:
                t = h.strip()
                if t and t.lower() not in seen:
                    seen.add(t.lower())
                    deduped.append(t)
            msg["headlines"] = deduped[:10]
            agg.results["news"] = msg

            # Trigger sentiment if not already dispatched
            if not agg.sentiment_dispatched:
                payload = {
                    "type": "sentiment_task",
                    "ticker": ticker,
                    "texts": msg.get("headlines", [])
                }
                ch.basic_publish(
                    exchange="",
                    routing_key=SENTIMENT_QUEUE,
                    body=safe_json(payload),
                    properties=pika.BasicProperties(
                        reply_to=callback_queue,
                        correlation_id=correlation_id,
                        delivery_mode=2
                    )
                )
                agg.sentiment_dispatched = True

        elif msg_type == "sentiment":
            agg.results["sentiment"] = msg

        _ch.basic_ack(delivery_tag=method.delivery_tag)

    # Start consuming replies
    ch.basic_consume(queue=callback_queue, on_message_callback=on_reply, auto_ack=False)

    # Publish initial tasks: price + news
    task_price = {"type": "price_task", "ticker": ticker}
    ch.basic_publish(
        exchange="",
        routing_key=YFINANCE_QUEUE,
        body=safe_json(task_price),
        properties=pika.BasicProperties(
            reply_to=callback_queue, correlation_id=correlation_id, delivery_mode=2
        )
    )

    task_news = {"type": "news_task", "ticker": ticker}
    ch.basic_publish(
        exchange="",
        routing_key=NEWS_QUEUE,
        body=safe_json(task_news),
        properties=pika.BasicProperties(
            reply_to=callback_queue, correlation_id=correlation_id, delivery_mode=2
        )
    )

    # Wait loop (up to timeout)
    timeout_s = 15.0
    start = time.time()
    while time.time() - start < timeout_s:
        conn.process_data_events(time_limit=0.5)
        if agg.complete():
            break

    # Clean up consumer for this queue
    try:
        ch.queue_delete(queue=callback_queue)
    except Exception:
        pass
    ch.close()
    conn.close()

    # If not all results arrived, return partial with note
    if not agg.complete():
        return {
            "ticker": ticker,
            "note": "Partial results due to timeout.",
            "price": agg.results["price"],
            "news": agg.results["news"],
            "sentiment": agg.results["sentiment"],
        }

    # Build response
    price = agg.results["price"] or {}
    news = agg.results["news"] or {}
    sentiment = agg.results["sentiment"] or {}

    return {
        "ticker": ticker,
        "price": {
            "value": price.get("price"),
            "change_percent": price.get("change_percent"),
            "company_name": price.get("company_name"),
        },
        "news": {
            "headlines": news.get("headlines", [])
        },
        "sentiment": {
            "score": sentiment.get("score"),
            "label": sentiment.get("label"),
            "summary": sentiment.get("summary"),
        },
    }

