#         out_event = {
#             "document_id": doc_id,
#             "es_index": index,
#             "es_id": es_id
#         }

#         producer.send("document.es_deleted", out_event)
#         producer.flush()

#         logging.info(f"Emitted event: document.es_deleted for doc={doc_id}")

import os, json, time
import logging

from kafka import KafkaConsumer
from elasticsearch import Elasticsearch

logging.basicConfig(level=logging.INFO)

KAFKA_BROKER = os.getenv("KAFKA_BROKER")
ES_ENDPOINT = os.getenv("ES_ENDPOINT")
ES_INDEX = os.getenv("ES_INDEX")

def wait_kafka():
    for _ in range(10):
        try:
            consumer = KafkaConsumer(
                "document.deletion.requested",
                bootstrap_servers=[KAFKA_BROKER],
                value_deserializer=lambda x: json.loads(x.decode()),
                group_id="elastic-worker"
            )
            logging.info("Connected to kafka")
            return consumer
        except Exception as e:
            logging.warning(f"Kafka not ready, retrying {e}")
            time.sleep(3)
    raise RuntimeError("Kafka unavailable")

def get_es():
    for _ in range(10):
        try:
            es = Elasticsearch(ES_ENDPOINT)
            return es
        except Exception as e:  
            logging.info(f"ES not ready, retrying {e}")
            time.sleep(3)
    raise RuntimeError("ES unavailable")


def main():
    consumer = wait_kafka()
    es = get_es()

    logging.info("Waiting for kafka events")
    for message in consumer:
        logging.info("Message received")
        event = message.value
        logging.info(f"Event value: {event}")
        document_id = event.get("document_id")

        logging.info(f"Processing delete for doc={document_id}")

        es.options(ignore_status=[400, 404]).delete(index=ES_INDEX, id=document_id)
        
        # Send document removed

if __name__=="__main__":
    main()