import os, json, time
import logging

from kafka import KafkaConsumer, KafkaProducer
from elasticsearch import Elasticsearch

logging.basicConfig(level=logging.INFO)

KAFKA_BROKER = os.getenv("KAFKA_BROKER")
ES_ENDPOINT = os.getenv("ES_ENDPOINT")

def wait_kafka():
    for _ in range(10):
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            logging.info("Connected to kafka")
            return producer
        except Exception as e:
            logging.warning(f"Kafka not ready, retrying {e}")
            time.sleep(3)
    raise RuntimeError("Kafka unavailable")

def get_es():
    for _ in range(10):
        try:
            es = ElasticSearch(ES_ENDPOINT)
            if es.ping():
                return es
        except Exception as e:  
            logging.info(f"ES not ready, retrying {e}")
            time.sleep(3)
    raise RuntimeError("ES unavailable")

def delete_from_es(index, es_id):
    es = ElasticSearch(ES_ENDPOINT)

    try:
        es.delete(index=index, id=es_id, ignore=[404])
        logging.info(f"ES: deleted index={index}, id={es_id}")
    except Exception as e:
        logging.warning(f"ES delete failed (idempotent): {e}")

def main():
    producer = wait_kafka()
    consumer = KafkaConsumer(
        "document.deletion.requested",
        bootstrap_servers=[KAFKA_BROKER],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        group_id="worker-es"
    )

    logging.info("ES worker listening...")
    
    for msg in consumer:
        event = msg.value
        doc_id = event["document_id"]
        index = event["es_index"]
        es_id = event["es_id"]

        logging.info(f"Processing delete for doc={doc_id}")

        delete_from_es(index, es_id)

        out_event = {
            "document_id": doc_id,
            "es_index": index,
            "es_id": es_id
        }

        producer.send("document.es_deleted", out_event)
        producer.flush()

        logging.info(f"Emitted event: document.es_deleted for doc={doc_id}")


if __name__=="__main__":
    main()