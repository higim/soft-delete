### Soft Delete to eventual consistency in a distributed system with several storage layers

This repository contains a proof-of-concept (POC) demonstrating how to decouple deletion functionality in a distributed system 
with multiple storage layers.

The accompanying theory and design rationale are explained in [](this blog post).

### Architecture Overview

- FastAPI – Service handling document operations.
- PostgreSQL – Document metadata (primary source of truth).
- MinIO – S3-compatible object storage for document content.
- Elasticsearch – Full-text search storage for documents.
- Kafka – Event streaming platform for asynchronous deletion events.

#### Key concepts demonstrated:

- **Soft Delete** – Mark documents as deleted in PostgreSQL instead of physically removing them.
- **Eventual Consistency** – Document deletions propagate asynchronously to S3/MinIO and Elasticsearch.

⚠️ Disclaimer: This is a POC meant for demonstration purposes. While the API follows a Clean Architecture style, it is not production-ready. Additional improvements are required for production-grade consistency, security, and scalability. Workers are simplified/scripted.

### Getting started

Clone the repo:

```git clone https://github.com/higim/soft-delete
cd soft-delete
```
Start the full stack:

```docker compose up --build```

You can interact with the API using Postman, cURL, or any HTTP client:

- Upload documents
- Retrieve documents
- Delete documents (soft delete + event propagation)

#### Important Note on Document Upload

The current implementation of the POC only stores metadata in PostgreSQL when uploading documents via the API.
- Files in MinIO (S3) or documents in Elasticsearch are not automatically uploaded.
- To see actual deletions in MinIO or Elasticsearch, you must upload the documents to these layers manually.

Since deletions are idempotent, the soft delete mechanism work correctly even if the files do not exist in MinIO or Elasticsearch. This ensures that the system remains consistent and resilient, regardless of which storage layers contain the document.

### MinIO Configuration

You have to create a documents bucket:

```mc alias set local http://minio:9000 minio minio123

mc mb -p local/documents || true
```

### Notes
- **Event-driven deletion**: Actual removal from S3/MinIO and Elasticsearch is asynchronous.
- **Idempotency**: Consumers of deletion events must be idempotent to handle retries safely.
- **Outbox pattern (future improvement)** is needed to ensure atomic operations involving databases and the sending of events.
