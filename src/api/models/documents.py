from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

class DocumentCreate(BaseModel):
    name: str

class DocumentResponse(BaseModel):
    id: UUID
    name: str
    uploaded_at: datetime