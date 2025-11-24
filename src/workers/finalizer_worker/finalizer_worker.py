import json, os, time
import logging

from kafka import KafkaConsumer
import psycopg2
from psycopg2.extras import RealDictCursor

logging.basicConfig(level=logging.INFO)

KAFKA_BROKER = os.getenv("KAFKA_BROKER")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASS = os.getenv("POSTGRES_PASS")

def get_pg_conn():
    for _ in range(10):
        try:
            conn = psycopg2.connect(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                database=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASS
            )
            conn.autocommit = True
            logging.info("Connected to Postgres")
            return conn
        except Exception as e:
            logging.warning(f"Postgres not ready, retrying... {e}")
            time.sleep(3)
    raise RuntimeError("Cannot connect to Postgres")


def ensure_progress_row(conn, doc_id):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO deletion_progress (document_id)
            VALUES (%s)
            ON CONFLICT (document_id) DO NOTHING;         
        """, (doc_id,))

def mark_step_complete(conn, doc_id, step):
    with conn.cursor() as cur:
        if step == "s3":
            cur.execute("""
                UPDATE deletion_progress
                SET s3_done = TRUE, updated_at = now()
                WHERE document_id = %s;         
            """, (doc_id,))
        elif step == "es":
            cur.execute("""
                UPDATE deletion_progress
                SET es_done = TRUE, updated_at = now()         
                WHERE document_id = %s;
            """, (doc_id,))

def get_progress(conn, doc_id):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT s3_done, es_done
            FROM deletion_progress
            WHERE document_id = %s;
        """, (doc_id,))
        return cur.fetchone()
    
def delete_document_metadata(conn, doc_id):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM documents WHERE id = %s;", (doc_id,))
        cur.execute("DELETE FROM deletion_progress WHERE document_id = %s;", (doc_id,))

def wait_kafka():
    for _ in range(10):
        try:
            consumer = KafkaConsumer(
                "document.s3_deleted", "document.es_deleted",
                bootstrap_servers=[KAFKA_BROKER],
                value_deserializer=lambda m: json.loads(m.decode()),
                group_id="finalizer_worker",
                auto_offset_reset="earliest"
            )
            logging.info("Connected to kafka")
            return consumer
        except Exception as e:
            logging.warning(f"Kafka producer retry... {e}")
            time.sleep(3)
    raise RuntimeError("Cannot connect to Kafka producer")

def main():
    consumer = wait_kafka()
    ps_connection = get_pg_conn()
    logging.info("Waiting for events...")

    for msg in consumer:
        event = msg.value
        document_id = event["document_id"]

        logging.info(f"Finalizer received event {event} on {msg.topic} for document={document_id}")

        ensure_progress_row(ps_connection, document_id)

        if msg.topic == "document.s3_deleted":
            mark_step_complete(ps_connection, document_id, "s3")
        elif msg.topic == "document.es_deleted":
            logging.info(f"Document ID received in document.es_deleted: {document_id}")
            mark_step_complete(ps_connection, document_id, "es")

        state = get_progress(ps_connection, document_id)
        logging.info(f"Progress state: {state}")

        if state["s3_done"] and state["es_done"]:
            logging.info(f"All steps completed for document={document_id}. Finalizing deletion...")
            delete_document_metadata(ps_connection, document_id)

            logging.info("Document fully deleted.")

if __name__=="__main__":
    main()