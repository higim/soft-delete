import os
import logging
import time
import json

from kafka import KafkaProducer
from infra.kafka.event_bus_kafka import KafkaEventBus

KAFKA_BROKER = os.getenv("KAFKA_BROKER")

logging.basicConfig(level=logging.INFO)

producer = None

def get_event_bus(retries: int =10, delay: int=3):
    global producer
    if producer is not None:
        return producer
    
    for attempt in range(1, retries+1):
        try:
            logging.info(f"Connecting to Kafka (attempt {attempt})")
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            logging.info("Kafka connected successfully.")
            
            return KafkaEventBus(producer)
        except Exception as e:
            time.sleep(delay)
            logging.warning(f"Kafka not ready, retrying... {e}")

    raise RuntimeError("Failed to connect to kafka.")