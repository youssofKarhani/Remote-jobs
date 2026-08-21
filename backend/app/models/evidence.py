import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin
from app.models.types import GUID

if TYPE_CHECKING:
    from app.models.user import User


class ExperienceRecord(Base, TimestampMixin):
    """Parent work experience container (e.g. company role with start/end date)."""
    __tablename__ = "experience_records"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    company_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    role_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    location: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    start_date: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    end_date: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    is_current: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="experience_records",
    )
    evidence_items: Mapped[List["EvidenceItem"]] = relationship(
        "EvidenceItem",
        back_populates="experience_record",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ExperienceRecord id={self.id} company={self.company_name!r} role={self.role_title!r}>"


class EvidenceItem(Base, TimestampMixin):
    """Discrete, atomic, verifiable bullet point or factual claim with a stable ID."""
    __tablename__ = "evidence_items"
    __table_args__ = (
        UniqueConstraint("user_id", "stable_id", name="uq_evidence_items_user_stable_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    experience_record_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID,
        ForeignKey("experience_records.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    stable_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    raw_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    category: Mapped[str] = mapped_column(
        String(50),
        default="experience",
        nullable=False,
    )
    variants: Mapped[Optional[Dict[str, str]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="evidence_items",
    )
    experience_record: Mapped[Optional["ExperienceRecord"]] = relationship(
        "ExperienceRecord",
        back_populates="evidence_items",
    )

    def __repr__(self) -> str:
        return f"<EvidenceItem id={self.id} stable_id={self.stable_id!r} verified={self.is_verified}>"


class Skill(Base, TimestampMixin):
    """Verified candidate skill record with stable ID."""
    __tablename__ = "skills"
    __table_args__ = (
        UniqueConstraint("user_id", "stable_id", name="uq_skills_user_stable_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    stable_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False,
    )
    category: Mapped[str] = mapped_column(
        String(50),
        default="backend",
        nullable=False,
    )
    proficiency: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    years_of_experience: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="skills",
    )

    def __repr__(self) -> str:
        return f"<Skill id={self.id} stable_id={self.stable_id!r} name={self.name!r}>"


class Project(Base, TimestampMixin):
    """Verified portfolio or side project record with stable ID."""
    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint("user_id", "stable_id", name="uq_projects_user_stable_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    stable_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    technologies: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )
    url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )
    github_url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )
    start_date: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    end_date: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="projects",
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id} stable_id={self.stable_id!r} title={self.title!r}>"


class Certification(Base, TimestampMixin):
    """Verified license or certification record with stable ID."""
    __tablename__ = "certifications"
    __table_args__ = (
        UniqueConstraint("user_id", "stable_id", name="uq_certifications_user_stable_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    stable_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    issuing_organization: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    issue_date: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    expiration_date: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    credential_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    credential_url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="certifications",
    )

    def __repr__(self) -> str:
        return f"<Certification id={self.id} stable_id={self.stable_id!r} name={self.name!r}>"


class EducationRecord(Base, TimestampMixin):
    """Verified academic degree and education record with stable ID."""
    __tablename__ = "education_records"
    __table_args__ = (
        UniqueConstraint("user_id", "stable_id", name="uq_education_user_stable_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    stable_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    institution: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    degree: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    field_of_study: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    start_date: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    end_date: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    grade: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    activities: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="education_records",
    )

    def __repr__(self) -> str:
        return f"<EducationRecord id={self.id} stable_id={self.stable_id!r} degree={self.degree!r}>"
