from datetime import datetime
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from infra.repositories.documents_repository import DocumentRepository
from infra.kafka.event_bus_kafka import KafkaEventBus

from domain.document import Document, DocumentDeletedEvent

logging.basicConfig(level=logging.INFO)

class GetDocumentUseCase:
    def __init__(self, document_repo: DocumentRepository):
        self.document_repo = document_repo

    async def execute(self, id: str) -> Document:
        return await self.document_repo.get_document(id)

class CreateDocumentUseCase:
    def __init__(self, session: AsyncSession, document_repo: DocumentRepository):
        self.session = session
        self.document_repo = document_repo

    async def execute(self, document_name: str) -> Document:
        new_document = Document(
            name=document_name,
        )
        new_document_db = await self.document_repo.create_document(new_document)
        await self.session.commit()
        return new_document_db

class DeleteDocumentUseCase:
    def __init__(self, session: AsyncSession, document_repo: DocumentRepository, event_bus: KafkaEventBus):
        self.session = session
        self.document_repo = document_repo
        self.event_bus = event_bus

    async def execute(self, id: str) -> None:
        logging.info("Executing delete document use case")
        await self.document_repo.delete_document(id)
        await self.session.commit()

        self.event_bus.publish(DocumentDeletedEvent(document_id=id, occurred_at=datetime.now()))
        logging.info("Delete document use case succeed.")