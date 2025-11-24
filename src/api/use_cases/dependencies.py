from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infra.repositories.documents_repository_sql import DocumentRepositorySQL
from infra.kafka.event_bus_kafka import KafkaEventBus

from use_cases.documents import (
    GetDocumentUseCase,
    CreateDocumentUseCase,
    DeleteDocumentUseCase
)

from infra.base import get_db
from infra.event_bus_base import get_event_bus

async def get_document_use_case(session: AsyncSession = Depends(get_db)) -> GetDocumentUseCase:
    document_repo = DocumentRepositorySQL(session)
    return GetDocumentUseCase(document_repo=document_repo)

async def create_document_use_case(session: AsyncSession = Depends(get_db)) -> CreateDocumentUseCase:
    document_repo = DocumentRepositorySQL(session)
    return CreateDocumentUseCase(session=session, document_repo=document_repo)

async def delete_document_use_case(
        session: AsyncSession = Depends(get_db),
        event_bus: KafkaEventBus = Depends(get_event_bus)
    ) -> DeleteDocumentUseCase:
    document_repo = DocumentRepositorySQL(session)
    return DeleteDocumentUseCase(session=session, document_repo=document_repo, event_bus=event_bus)
