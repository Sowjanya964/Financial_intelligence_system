import json
import pika
from typing import Dict, Any, Optional
from config.settings import RABBITMQ_HOST

def make_connection():
    """
    Return a pika.BlockingConnection to RabbitMQ.
    Agents and orchestrator will open channels from this connection.
    """
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    return connection

def safe_json(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False).encode("utf-8")

def parse_json(body: bytes) -> Dict[str, Any]:
    try:
        return json.loads(body.decode("utf-8"))
    except Exception:
        return {}

