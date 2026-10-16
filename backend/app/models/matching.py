"""Job Matching and Compatibility Assessment Models."""

import uuid
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy import JSON
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin
from app.models.types import GUID


class JobMatch(Base, TimestampMixin):
    __tablename__ = "job_matches"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(GUID(), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    overall_score = Column(Integer, nullable=False)  # 0-100
    recommendation = Column(String(50), nullable=False)  # 'apply', 'consider', 'skip'
    status = Column(String(50), nullable=False, default="new")  # 'new', 'viewed', 'dismissed', 'saved'
    matched_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_job_matches_user_job"),
    )

    user = relationship("User", backref="matches")
    job = relationship("Job", backref="matches")
    assessment = relationship("JobAssessment", back_populates="job_match", uselist=False, cascade="all, delete-orphan")


class JobAssessment(Base, TimestampMixin):
    __tablename__ = "job_assessments"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    job_match_id = Column(GUID(), ForeignKey("job_matches.id", ondelete="CASCADE"), nullable=False, unique=True)
    skills_score = Column(Integer, nullable=False)
    experience_score = Column(Integer, nullable=False)
    seniority_score = Column(Integer, nullable=False)
    location_score = Column(Integer, nullable=False)
    language_score = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)
    strengths = Column(JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=False)
    missing_requirements = Column(JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=False)
    matching_evidence_ids = Column(JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=False)

    job_match = relationship("JobMatch", back_populates="assessment")


class PreScreenResultRecord(Base, TimestampMixin):
    __tablename__ = "prescreen_results"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(GUID(), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    relevant = Column(Boolean, nullable=False)
    confidence = Column(Float, nullable=False)
    reason_codes = Column(JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=False)
    reasoning = Column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_prescreen_results_user_job"),
    )

    user = relationship("User")
    job = relationship("Job")
