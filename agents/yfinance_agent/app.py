'''
import pika
import yfinance as yf
from typing import Optional
from common.utils import make_connection, safe_json, parse_json
from config.settings import YFINANCE_QUEUE


def compute_change_percent(hist) -> Optional[float]:
    try:
        closes = hist["Close"].dropna()
        if len(closes) >= 2:
            prev = float(closes.iloc[-2])
            last = float(closes.iloc[-1])
            if prev != 0:
                return round(((last - prev) / prev) * 100, 2)
    except Exception:
        pass
    return None

def handle_price_task(ch, method, properties, body):
    msg = parse_json(body)
    ticker = msg.get("ticker", "").upper()

    result = {
        "type": "price",
        "ticker": ticker,
        "price": None,
        "change_percent": None,
        "company_name": None
    }

    try:
        tk = yf.Ticker(ticker)
        hist = tk.history(period="5d", interval="1d")
        change_pct = compute_change_percent(hist)
        # Try to get current price from recent data or fast_info
        price = None
        try:
            price = float(hist["Close"].dropna().iloc[-1])
        except Exception:
            price = float(getattr(tk.fast_info, "last_price", None) or 0) or None

        # Company name if available
        info = {}
        try:
            info = tk.info or {}
        except Exception:
            info = {}
        company_name = info.get("longName") or info.get("shortName")

        result.update({
            "price": price,
            "change_percent": change_pct,
            "company_name": company_name
        })
    except Exception as e:
        result["error"] = f"{e}"

    # Reply
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
    ch.queue_declare(queue=YFINANCE_QUEUE, durable=True)
    ch.basic_qos(prefetch_count=1)
    ch.basic_consume(queue=YFINANCE_QUEUE, on_message_callback=handle_price_task, auto_ack=False)
    print("[yfinance_agent] Waiting for price tasks...")
    ch.start_consuming()

if __name__ == "__main__":
    main()

'''
import pika
import yfinance as yf
from typing import Optional
from common.utils import make_connection, safe_json, parse_json
from config.settings import YFINANCE_QUEUE


def compute_change_percent(hist) -> Optional[float]:
    """Compute daily % change from last 2 closes."""
    try:
        closes = hist["Close"].dropna()
        if len(closes) >= 2:
            prev = float(closes.iloc[-2])
            last = float(closes.iloc[-1])
            if prev != 0:
                return round(((last - prev) / prev) * 100, 2)
    except Exception:
        pass
    return None


def handle_price_task(ch, method, properties, body):
    msg = parse_json(body)
    ticker = msg.get("ticker", "").upper()

    result = {
        "type": "price",
        "ticker": ticker,
        "price": None,
        "change_percent": None,
        "company_name": None
    }

    try:
        tk = yf.Ticker(ticker)

        # Get last 5d daily history
        hist = tk.history(period="5d", interval="1d")
        change_pct = compute_change_percent(hist)

        # Try to get current price
        price = None
        try:
            price = float(hist["Close"].dropna().iloc[-1])
        except Exception:
            try:
                price = float(getattr(tk.fast_info, "last_price", None) or 0) or None
            except Exception:
                price = None

        # Company name if available
        company_name = None
        try:
            info = tk.info or {}
            company_name = info.get("longName") or info.get("shortName")
        except Exception:
            company_name = None

        result.update({
            "price": price,
            "change_percent": change_pct,
            "company_name": company_name
        })

    except Exception as e:
        result["error"] = str(e)

    # Reply to requester
    reply_to = properties.reply_to
    corr_id = properties.correlation_id
    if reply_to:
        ch.basic_publish(
            exchange="",
            routing_key=reply_to,
            properties=pika.BasicProperties(
                correlation_id=corr_id,
                delivery_mode=2
            ),
            body=safe_json(result)
        )
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    conn = make_connection()
    ch = conn.channel()
    ch.queue_declare(queue=YFINANCE_QUEUE, durable=True)
    ch.basic_qos(prefetch_count=1)
    ch.basic_consume(queue=YFINANCE_QUEUE, on_message_callback=handle_price_task, auto_ack=False)
    print("[yfinance_agent] Waiting for price tasks...")
    ch.start_consuming()


if __name__ == "__main__":
    main()
