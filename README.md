You have to create a documents bucket:

mc alias set local http://minio:9000 minio minio123

mc mb -p local/documents || true