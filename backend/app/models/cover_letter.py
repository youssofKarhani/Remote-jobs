"""Cover Letter Models."""

import uuid
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy import JSON
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin
from app.models.types import GUID


class CoverLetter(Base, TimestampMixin):
    __tablename__ = "cover_letters"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(GUID(), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    strategy = Column(String(100), nullable=False, default="Technical Depth")
    content = Column(Text, nullable=False)
    referenced_evidence_ids = Column(JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_cover_letters_user_job"),
    )

    user = relationship("User", backref="cover_letters")
    job = relationship("Job", backref="cover_letters")
