from uuid import UUID
from typing import Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from domain import Document
from infra.models.document import Document as DocumentDBModel

class DocumentNotFoundException(Exception):
    pass

class DocumentRepositorySQL:
    def __init__(self, db: AsyncSession):
        self.session = db

    async def create_document(self, document: Document) -> Document:
        document_db = DocumentDBModel(**document.model_dump())
        self.session.add(document_db)
        await self.session.flush()
        await self.session.refresh(document_db)
        return Document.model_validate(
            document_db,
            from_attributes=True
        )
    
    async def get_document(self, document_id: UUID) -> Document:
        stmt = select(DocumentDBModel).where(DocumentDBModel.id == document_id, DocumentDBModel.deleted_at == None)
        result = await self.session.execute(stmt)
        document_db = result.scalar_one_or_none()
        if not document_db:
            raise DocumentNotFoundException(f"Document {document_id} not found.")
        return Document.model_validate(document_db, from_attributes=True)

    async def delete_document(self, document_id: UUID) -> None:
        stmt = (
            update(DocumentDBModel)
            .where(DocumentDBModel.id == document_id, DocumentDBModel.deleted_at.is_(None))
            .values(deleted_at=datetime.now())
            .returning(DocumentDBModel.id)
        )

        result = await self.session.execute(stmt)
        row = result.first()

        if not row:
            raise DocumentNotFoundException(f"Document {document_id} not found.")
    
        await self.session.flush()