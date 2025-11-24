from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

class DocumentDeletedEvent(BaseModel):
    document_id: str
    occurred_at: datetime
    
    event: str = "DocumentDeleted"

class Document(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    name: str
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)