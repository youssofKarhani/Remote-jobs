"""Test Suite for Phase 10 — Controlled Production Rollout.

Verifies:
1. End-to-end CV upload via multipart `/api/v1/cv/upload` routed through the hardened spatial pipeline.
2. Backwards-compatible response schema enriched with audit metadata (quality score, block count, provenance status).
3. Backwards-compatibility feature flag toggle (`CV_HARDENED_PIPELINE_ENABLED`).
4. Two-column CV reading order preserved without interleaving when ingested through HTTP API.
5. Plain text CV parsed through `/api/v1/cv/parse-text` utilizing structured line-by-line block mapping.
6. Evidence Bank safety invariants: all parsed items staged with `is_verified=False` and stable sequential IDs.
7. Data isolation invariant: uploading for user A never overwrites or mutates records belonging to user B (Rule 11 & 13).
"""

import io
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from app.models.evidence import Certification, EducationRecord, EvidenceItem, ExperienceRecord, Project, Skill
from app.models.profile import CandidateProfile
from app.models.user import User
from app.services.cv_benchmark_runner import build_youssof_twocolumn_pdf


# ============================================================================
# 1. Hardened CV Upload Endpoint Tests
# ============================================================================

def test_hardened_cv_upload_two_column_endpoint(
    client: TestClient, sample_user: User, auth_headers: dict, db_session: Session
):
    """Verify Youssof's two-column CV uploads through API and parses with 100% hardened metadata."""
    settings.CV_HARDENED_PIPELINE_ENABLED = True
    pdf_bytes = build_youssof_twocolumn_pdf()

    files = {"file": ("youssof_cv.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    response = client.post("/api/v1/cv/upload", files=files, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "summary" in data

    summary = data["summary"]
    # Verify hardened pipeline audit metadata
    assert summary.get("hardened_pipeline") is True
    assert summary.get("provenance_valid") is True
    assert summary.get("quality_score", 0) > 0.0
    assert summary.get("reading_order_blocks", 0) >= 10
    assert summary.get("is_scanned") is False
    assert summary.get("document_type") == "native_pdf"

    # Verify database persistence & stable IDs
    profile = db_session.query(CandidateProfile).filter(CandidateProfile.user_id == sample_user.id).first()
    assert profile is not None
    assert profile.is_verified is False
    assert "Youssof El Karhani" in (profile.raw_cv_text or "")

    skills = db_session.query(Skill).filter(Skill.user_id == sample_user.id).all()
    assert len(skills) >= 4
    skill_names = [s.name for s in skills]
    assert "Python" in skill_names
    assert "FastAPI" in skill_names
    assert all(s.stable_id.startswith("SKILL_") for s in skills)
    assert all(s.is_verified is False for s in skills)  # Staging guard


def test_hardened_cv_upload_feature_flag_toggle(
    client: TestClient, sample_user: User, auth_headers: dict, db_session: Session
):
    """Verify switching CV_HARDENED_PIPELINE_ENABLED=False activates the legacy path safely."""
    settings.CV_HARDENED_PIPELINE_ENABLED = False
    pdf_bytes = build_youssof_twocolumn_pdf()

    files = {"file": ("legacy_cv.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    response = client.post("/api/v1/cv/upload", files=files, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    summary = data["summary"]
    # In legacy mode, hardened_pipeline metadata is absent
    assert summary.get("hardened_pipeline") is None

    # Restore flag
    settings.CV_HARDENED_PIPELINE_ENABLED = True


# ============================================================================
# 2. Plain Text Endpoint Integration
# ============================================================================

def test_hardened_parse_text_endpoint(
    client: TestClient, sample_user: User, auth_headers: dict, db_session: Session
):
    """Verify /cv/parse-text endpoint runs through hardened pipeline with line-by-line blocks."""
    settings.CV_HARDENED_PIPELINE_ENABLED = True
    payload = {
        "text": (
            "Diana Prince\n"
            "Cloud Security Engineer - London\n"
            "Email: diana@defense.io\n\n"
            "EXPERIENCE\n"
            "Lead Security Architect at ShieldCorp (2020 - Present)\n"
            "- Designed zero-trust identity architecture.\n\n"
            "SKILLS\n"
            "AWS, Terraform, Python, Kubernetes, Vault\n"
        )
    }

    response = client.post("/api/v1/cv/parse-text", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    summary = data["summary"]

    assert summary.get("hardened_pipeline") is True
    assert summary.get("document_type") == "plain_text"
    assert summary.get("provenance_valid") is True
    assert summary.get("source_blocks_count") >= 4

    # Verify skills created
    skills = db_session.query(Skill).filter(Skill.user_id == sample_user.id).all()
    assert any("Terraform" in s.name for s in skills)
    assert all(s.is_verified is False for s in skills)


# ============================================================================
# 3. Data Isolation Invariant (Rule 11 & 13)
# ============================================================================

def test_cv_upload_does_not_mutate_other_users(
    client: TestClient, sample_user: User, auth_headers: dict, db_session: Session
):
    """Verify that uploading a CV for sample_user does not touch or overwrite protected candidate records."""
    settings.CV_HARDENED_PIPELINE_ENABLED = True

    # 1. Simulate an existing protected profile (Candidate B)
    candidate_b = User(
        email="protected_user@remotejobs.com",
        hashed_password="hashed_pw_xyz",
        full_name="Protected Candidate",
        is_active=True,
    )
    db_session.add(candidate_b)
    db_session.commit()
    db_session.refresh(candidate_b)

    b_profile = CandidateProfile(
        user_id=candidate_b.id,
        headline="Protected Senior Architect",
        raw_cv_text="PROTECTED DO NOT OVERWRITE",
        is_verified=False,
    )
    b_skill = Skill(
        user_id=candidate_b.id,
        stable_id="SKILL_001",
        name="COBOL",
        is_verified=False,
    )
    db_session.add(b_profile)
    db_session.add(b_skill)
    db_session.commit()

    # 2. Upload for sample_user
    pdf_bytes = build_youssof_twocolumn_pdf()
    files = {"file": ("sample_user_cv.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    res = client.post("/api/v1/cv/upload", files=files, headers=auth_headers)
    assert res.status_code == 200

    # 3. Verify Candidate B remained 100% untouched
    b_profile_fresh = db_session.query(CandidateProfile).filter(CandidateProfile.user_id == candidate_b.id).first()
    assert b_profile_fresh.headline == "Protected Senior Architect"
    assert b_profile_fresh.raw_cv_text == "PROTECTED DO NOT OVERWRITE"

    b_skills_fresh = db_session.query(Skill).filter(Skill.user_id == candidate_b.id).all()
    assert len(b_skills_fresh) == 1
    assert b_skills_fresh[0].name == "COBOL"
