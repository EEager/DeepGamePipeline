from aiokafka import AIOKafkaProducer
import asyncio
import json
import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "game-logs")

class KafkaProducerSingleton:
    def __init__(self):
        self.producer = None

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await self.producer.start()

    async def send_event(self, event_type, details):
        if self.producer is None:
            await self.start()
        event = {"event_type": event_type, "details": details}
        await self.producer.send_and_wait(KAFKA_TOPIC, event)

    async def stop(self):
        if self.producer:
            await self.producer.stop()

kafka_producer = KafkaProducerSingleton()