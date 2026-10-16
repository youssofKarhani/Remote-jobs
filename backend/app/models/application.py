"""Application Tracking System (ATS) Models."""

import uuid
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin
from app.models.types import GUID


class Application(Base, TimestampMixin):
    __tablename__ = "applications"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(GUID(), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), nullable=False, default="Saved")
    # Valid stages: 'Saved', 'Applying', 'Applied', 'Interview', 'Offer', 'Rejected'
    tailored_cv_id = Column(GUID(), ForeignKey("generated_documents.id", ondelete="SET NULL"), nullable=True)
    cover_letter_id = Column(GUID(), ForeignKey("cover_letters.id", ondelete="SET NULL"), nullable=True)
    applied_at = Column(DateTime(timezone=True), nullable=True)
    salary_offered = Column(Numeric(12, 2), nullable=True)
    notes = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_applications_user_job"),
    )

    user = relationship("User", backref="applications")
    job = relationship("Job", backref="applications")
    tailored_cv = relationship("GeneratedDocument")
    cover_letter = relationship("CoverLetter")
    events = relationship("ApplicationEvent", back_populates="application", cascade="all, delete-orphan", order_by="ApplicationEvent.created_at.desc()")


class ApplicationEvent(Base, TimestampMixin):
    __tablename__ = "application_events"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    application_id = Column(GUID(), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)

    application = relationship("Application", back_populates="events")
