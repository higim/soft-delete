import os
import json
import time
import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime

# from kafka import KafkaProducer

POSTGRES_URL = os.getenv("DATABASE_URL")
# KAFKA_BROKER = os.getenv("KAFKA_BROKER")

engine = create_engine(POSTGRES_URL)
Base = declarative_base()

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.datetime.now)
    deleted_at = Column(DateTime, nullable=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Documents async deletion")

@app.get("/")
def read_root():
    return {"status": "ok"}

# for _ in range(10):  # retry 10 times
#     try:
#         producer = KafkaProducer(bootstrap_servers=[KAFKA_BROKER], 
#                                  value_serializer=lambda v: json.dumps(v).encode("utf-8"))
#         print("Connected to Kafka")
#         break
#     except Exception as e:
#         print("Kafka not ready, retrying in 3s...", e)
#         time.sleep(3)
# else:
#     raise RuntimeError("Cannot connect to Kafka after several retries")


# @app.delete("/documents/{id}", status_code=202)
# def delete_document(id: str):
#     conn = psycopg2.connect(POSTGRES_URL)
#     cur = conn.cursor()

#     cur.execute("UPDATE documents SET deleted_at = NOW() WHERE id = %s RETURNING id;", (id,))
#     if cur.rowcount == 0:
#         raise HTTPException(status_code=404, detail="Document not found")
#     conn.commit()
#     cur.close()
#     conn.close()

#     event = {"event": "DocumentDeleted", "document_id": id, "timestamp": datetime.datetime.now().isoformat()}
#     producer.send("document.deletion.requested", event)

#     return {"status": "queued", "document_id": id}