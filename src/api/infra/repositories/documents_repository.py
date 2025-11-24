from uuid import UUID
from typing import Protocol

from domain import Document

class DocumentRepository(Protocol):
    async def create_document(self, document: Document) -> Document:
        ...

    async def get_document(self, id: UUID) -> Document:
        ...

    async def delete_document(slef, id: UUID) -> None:
        ...