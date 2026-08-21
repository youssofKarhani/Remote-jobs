import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Any, List, Optional
from sqlalchemy import Boolean, ForeignKey, Numeric, String, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin
from app.models.types import GUID

if TYPE_CHECKING:
    from app.models.user import User


class CandidatePreference(Base, TimestampMixin):
    """Deterministic job matching constraints configured by the candidate."""
    __tablename__ = "candidate_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    target_roles: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )
    locations: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )
    remote_only: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    hybrid_allowed: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    onsite_allowed: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    job_types: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=lambda: ["Full Time"],
        nullable=False,
    )
    min_salary: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )
    salary_currency: Mapped[Optional[str]] = mapped_column(
        String(10),
        default="EUR",
        nullable=True,
    )
    max_seniority: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    languages: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=lambda: ["English"],
        nullable=False,
    )
    excluded_companies: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )
    excluded_keywords: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )
    preferred_industries: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="candidate_preference",
    )

    def __repr__(self) -> str:
        return f"<CandidatePreference id={self.id} user_id={self.user_id} remote_only={self.remote_only}>"
