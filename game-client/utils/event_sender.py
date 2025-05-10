# event_sender.py

import json
from kafka import KafkaProducer

class EventSender:
    """Kafka를 통한 이벤트 전송 담당"""

    def __init__(self, topic: str = "game-logs", bootstrap_servers: str = "localhost:9092") -> None:
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=[bootstrap_servers],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def send(self, event_type: str, details: dict | None = None) -> None:
        event = {
            "event_type": event_type,
            "details": details,
        }
        self.producer.send(self.topic, event)

    def flush(self) -> None:
        self.producer.flush()

    def close(self) -> None:
        self.producer.close()
