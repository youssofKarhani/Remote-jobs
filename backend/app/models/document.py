"""Generated Document Models for Tailored CV and Artifacts."""

import uuid
from sqlalchemy import (
    Column,
    ForeignKey,
    LargeBinary,
    String,
    Text,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy import JSON
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin
from app.models.types import GUID


class GeneratedDocument(Base, TimestampMixin):
    __tablename__ = "generated_documents"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(GUID(), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=True)
    document_type = Column(String(50), nullable=False)  # 'cv', 'cover_letter'
    format = Column(String(20), nullable=False, default="docx")  # 'docx', 'pdf'
    file_path = Column(String(1024), nullable=False)
    file_bytes = Column(LargeBinary, nullable=True)  # Resilient storage backup for ephemeral containers
    verification_status = Column(String(50), nullable=False, default="unverified", server_default="unverified")
    selected_evidence_ids = Column(JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=True)

    user = relationship("User", backref="documents")
    job = relationship("Job", backref="documents")
