

# def main():
#     producer = wait_kafka()
#     consumer = KafkaConsumer(
#         "document.deletion.requested",
#         bootstrap_servers=[KAFKA_BROKER],
#         value_deserializer=lambda m: json.loads(m.decode('utf-8')),
#         group_id="worker-s3"
#     )
#     logging.info("S3 worker listening...")

#     for msg in consumer:
#         event = msg.value
#         doc_id = event["document_id"]
#         key = event["s3_key"]

#         logging.info(f"Processing delete for doc={doc_id}")

#         delete_from_s3(key)

#         out_event = {
#             "document_id": doc_id,
#             "s3_key": key
#         }

#         producer.send("document.s3_deleted", out_event)
#         producer.flush()

#         logging.info(f"Emitted event: document.s3_deleted for doc={doc_id}")

import os, json, time
import logging

from kafka import KafkaConsumer
from minio import Minio

logging.basicConfig(level=logging.INFO)

KAFKA_BROKER = os.getenv("KAFKA_BROKER")
KAFKA_BROKER = os.getenv("KAFKA_BROKER")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS = os.getenv("MINIO_ACCESS")
MINIO_SECRET = os.getenv("MINIO_SECRET")
S3_BUCKET = os.getenv("S3_BUCKET")

def wait_kafka():
    for _ in range(10):
        try:
            consumer = KafkaConsumer(
                "document.deletion.requested",
                bootstrap_servers=[KAFKA_BROKER],
                value_deserializer=lambda x: json.loads(x.decode()),
                group_id="s3-worker"
            )
            logging.info("Connected to kafka")
            return consumer
        except Exception as e:
            logging.warning(f"Kafka not ready, retrying {e}")
            time.sleep(3)
    raise RuntimeError("Kafka unavailable")

def get_minio():
    for _ in range(10):
        try:
            client = Minio(
                endpoint=MINIO_ENDPOINT,
                access_key=MINIO_ACCESS,
                secret_key=MINIO_SECRET,
                secure=False)
            return client
        except Exception as e:
            logging.warning(f"Minio not ready, retrying {e}")
            time.sleep(3)
    raise RuntimeError("Minio unavailable")

def main():
    consumer = wait_kafka()
    minio_client = get_minio()

    logging.info("Waiting for kafka events")
    for message in consumer:
        logging.info("Message received")
        event = message.value
        logging.info(f"Event value: {event}")
        document_id = event["document_id"]

        logging.info(f"Processing delete for doc={document_id}")

        minio_client.remove_object(bucket_name=S3_BUCKET, object_name=document_id)

if __name__=="__main__":
    main()