from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, HTTPException, Depends

from infra.base import engine, Base
from infra.repositories.documents_repository_sql import DocumentNotFoundException

from use_cases.dependencies import (
    get_document_use_case,
    create_document_use_case,
    delete_document_use_case
)
from use_cases.documents import (
    GetDocumentUseCase,
    CreateDocumentUseCase,
    DeleteDocumentUseCase
)

from models.documents import DocumentCreate, DocumentResponse

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        logging.info("Building database")
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Documents async deletion", lifespan=lifespan)

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.get("/documents/{id}", response_model=DocumentResponse)
async def get_document(
    id: str,
    get_document_use_case: GetDocumentUseCase = Depends(get_document_use_case)
):
    try:
        logging.info(f"Getting document with id {id}")
        return await get_document_use_case.execute(id)
    except DocumentNotFoundException as e:
        logging.info(f"Exception {e}")
        raise HTTPException(status_code=404, detail="File not found")

@app.post("/documents/")
async def post_file(
    file: DocumentCreate,
    create_document_use_case: CreateDocumentUseCase = Depends(create_document_use_case)):
    try:
        logging.info(f"Creating document {file.name}")
        return await create_document_use_case.execute(file.name)
    except Exception as e:
        logging.info(f"Exception {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{id}", status_code=202)
async def delete_document(
    id: str,
    delete_document_use_case: DeleteDocumentUseCase = Depends(delete_document_use_case)
):
    try:
        logging.info(f"Deleting document with id {id}")
        await delete_document_use_case.execute(id)
        logging.info(f"Soft delete for document with {id} complete")
        return { "status": "file soft-deleted", "id": id }
    except Exception as e:
        logging.info(f"Exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))
