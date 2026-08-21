import uuid
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin
from app.models.types import GUID

if TYPE_CHECKING:
    from app.models.profile import CandidateProfile
    from app.models.preference import CandidatePreference
    from app.models.evidence import (
        ExperienceRecord,
        EvidenceItem,
        Skill,
        Certification,
        Project,
        EducationRecord,
    )


class User(Base, TimestampMixin):
    """User account entity representing a registered tenant."""
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Relationships
    candidate_profile: Mapped[Optional["CandidateProfile"]] = relationship(
        "CandidateProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    candidate_preference: Mapped[Optional["CandidatePreference"]] = relationship(
        "CandidatePreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    experience_records: Mapped[List["ExperienceRecord"]] = relationship(
        "ExperienceRecord",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    evidence_items: Mapped[List["EvidenceItem"]] = relationship(
        "EvidenceItem",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    skills: Mapped[List["Skill"]] = relationship(
        "Skill",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    projects: Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    certifications: Mapped[List["Certification"]] = relationship(
        "Certification",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    education_records: Mapped[List["EducationRecord"]] = relationship(
        "EducationRecord",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"
