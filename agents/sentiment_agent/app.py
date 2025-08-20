import pika
from textblob import TextBlob
from common.utils import make_connection, safe_json, parse_json
from config.settings import SENTIMENT_QUEUE

def analyze_texts(texts):
    if not texts:
        return {"score": 0.0, "label": "neutral", "summary": "No major news found."}
    scores = []
    for t in texts:
        try:
            pol = TextBlob(t).sentiment.polarity
        except Exception:
            pol = 0.0
        scores.append(pol)
    avg = sum(scores) / max(len(scores), 1)
    label = "positive" if avg > 0.15 else "negative" if avg < -0.15 else "neutral"
    summary = f"Avg sentiment {avg:.2f} → {label} based on {len(texts)} headlines."
    return {"score": round(avg, 3), "label": label, "summary": summary}

def handle_sentiment_task(ch, method, properties, body):
    msg = parse_json(body)
    ticker = msg.get("ticker", "").upper()
    texts = msg.get("texts", [])

    result = {"type": "sentiment", "ticker": ticker}
    try:
        result.update(analyze_texts(texts))
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
    ch.queue_declare(queue=SENTIMENT_QUEUE, durable=True)
    ch.basic_qos(prefetch_count=1)
    ch.basic_consume(queue=SENTIMENT_QUEUE, on_message_callback=handle_sentiment_task, auto_ack=False)
    print("[sentiment_agent] Waiting for sentiment tasks...")
    ch.start_consuming()

if __name__ == "__main__":
    main()

