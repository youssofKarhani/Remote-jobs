"""Security and Integrity tests for Strict Evidence ID Validation Gate."""

import uuid
import pytest
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.evidence import EvidenceItem, ExperienceRecord, Skill
from app.models.user import User
from app.services.evidence_validation import (
    EvidenceValidationError,
    get_user_allowed_evidence_ids,
    resolve_verified_evidence_text,
    validate_selected_evidence_ids,
)


def test_validate_selected_ids_success():
    """Test that a valid subset of allowed IDs passes validation."""
    allowed = {"EXP_001", "EXP_002", "SKILL_001", "SKILL_002", "PROJ_001"}
    selected = ["EXP_001", "SKILL_001"]
    # Should not raise
    validate_selected_evidence_ids(selected, allowed, max_bullets=4)


def test_validate_selected_ids_hallucinated_rejection():
    """Test that any hallucinated or fabricated ID raises EvidenceValidationError."""
    allowed = {"EXP_001", "EXP_002", "SKILL_001"}
    selected = ["EXP_001", "EXP_999"]  # EXP_999 is fabricated

    with pytest.raises(EvidenceValidationError) as exc_info:
        validate_selected_evidence_ids(selected, allowed)
    assert "EXP_999" in str(exc_info.value)
    assert "Validation Failed" in str(exc_info.value)


def test_validate_selected_ids_exceeds_max_limit():
    """Test that selecting more bullets than max limit raises EvidenceValidationError."""
    allowed = {"EXP_001", "EXP_002", "EXP_003", "EXP_004", "EXP_005"}
    selected = ["EXP_001", "EXP_002", "EXP_003", "EXP_004"]

    with pytest.raises(EvidenceValidationError) as exc_info:
        validate_selected_evidence_ids(selected, allowed, max_bullets=3)
    assert "exceeds maximum allowed" in str(exc_info.value)


def test_cross_tenant_evidence_isolation(db_session: Session):
    """Test that User A cannot resolve or select User B's evidence items."""
    # Create User A (Backend Dev)
    user_a = User(
        email="alice@example.com",
        hashed_password=get_password_hash("pass"),
        full_name="Alice A",
        is_active=True,
    )
    # Create User B (Frontend Dev)
    user_b = User(
        email="bob@example.com",
        hashed_password=get_password_hash("pass"),
        full_name="Bob B",
        is_active=True,
    )
    db_session.add_all([user_a, user_b])
    db_session.commit()

    # User A has verified EXP_001
    item_a = EvidenceItem(
        user_id=user_a.id,
        stable_id="EXP_001",
        raw_text="Architected distributed Kafka pipeline handling 50k msgs/sec.",
        is_verified=True,
    )
    # User B has verified SKILL_001
    skill_b = Skill(
        user_id=user_b.id,
        stable_id="SKILL_001",
        name="React",
        is_verified=True,
    )
    db_session.add_all([item_a, skill_b])
    db_session.commit()

    # Allowed set for User A
    allowed_a = get_user_allowed_evidence_ids(db_session, user_a.id, verified_only=True)
    assert "EXP_001" in allowed_a
    assert "SKILL_001" not in allowed_a

    # User A tries to select User B's SKILL_001 -> Validation Failure
    with pytest.raises(EvidenceValidationError):
        validate_selected_evidence_ids(["SKILL_001"], allowed_a)

    # Resolving text for User A returns only User A's factual DB text
    resolved_a = resolve_verified_evidence_text(db_session, user_a.id, ["EXP_001"])
    assert len(resolved_a) == 1
    assert resolved_a[0]["text"] == "Architected distributed Kafka pipeline handling 50k msgs/sec."


def test_unverified_draft_evidence_rejected_from_allowed_set(db_session: Session, sample_user: User):
    """Test that unverified draft items (is_verified=False) are excluded from allowed selection set."""
    draft_item = EvidenceItem(
        user_id=sample_user.id,
        stable_id="EXP_001",
        raw_text="Draft unverified claim.",
        is_verified=False,
    )
    verified_item = EvidenceItem(
        user_id=sample_user.id,
        stable_id="EXP_002",
        raw_text="Verified factual achievement.",
        is_verified=True,
    )
    db_session.add_all([draft_item, verified_item])
    db_session.commit()

    allowed = get_user_allowed_evidence_ids(db_session, sample_user.id, verified_only=True)
    assert "EXP_002" in allowed
    assert "EXP_001" not in allowed  # Unverified draft excluded
