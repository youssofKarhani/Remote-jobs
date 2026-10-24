"""Tests for [HIDDEN:EVIDENCE_VERIFICATION] feature flag gating."""

import pytest
from app.config import settings
from app.core.security import create_access_token
from app.models.user import User


def test_verification_endpoints_return_404_when_feature_disabled(client, db_session, monkeypatch):
    """When FEATURE_EVIDENCE_VERIFICATION is False, verify endpoints must return 404."""
    monkeypatch.setattr(settings, "FEATURE_EVIDENCE_VERIFICATION", False)

    # Create dummy user
    user = User(
        email="test_flag@example.com",
        full_name="Test Flag User",
        hashed_password="mocked_password",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    token = create_access_token({"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    # 1. POST /api/v1/profile/evidence/verify
    res_verify = client.post(
        "/api/v1/profile/evidence/verify",
        json={"item_id": "EXP_001", "is_verified": True},
        headers=headers,
    )
    assert res_verify.status_code == 404
    assert "Evidence verification feature is currently disabled" in res_verify.json()["detail"]

    # 2. POST /api/v1/profile/evidence/verify-all
    res_all = client.post(
        "/api/v1/profile/evidence/verify-all",
        headers=headers,
    )
    assert res_all.status_code == 404
    assert "Evidence verification feature is currently disabled" in res_all.json()["detail"]
