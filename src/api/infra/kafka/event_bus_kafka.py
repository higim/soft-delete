import logging

from kafka import KafkaProducer

from domain.document import DocumentDeletedEvent

logging.basicConfig(level=logging.INFO)

class KafkaEventBus:
    def __init__(self, producer: KafkaProducer):
        self.producer = producer

    def publish_all(self, events: list[dict]):
        for event in events:
            self.publish(event)

    def publish(self, event):
        logging.info(f"Publishing event: {event.event}")
        if isinstance(event, DocumentDeletedEvent):
            logging.info(f"Sending Document deleted Event: {event.document_id}")
            self.producer.send(
                "document.deletion.requested", # Decouple if time
                event.model_dump(mode="json")
            )