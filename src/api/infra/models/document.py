from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import String, DateTime, Boolean

from infra.base import Base

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, index=True)
    name: Mapped[UUID] = mapped_column(String, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

class DeletionProgress(Base):
    __tablename__ = "deletion_progress"

    document_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, index=True)
    s3_done: Mapped[bool] = mapped_column(Boolean, nullable=True)
    es_done: Mapped[bool] = mapped_column(Boolean, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
