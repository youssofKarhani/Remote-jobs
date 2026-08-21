"""Integration tests for CV Parsing, Ingestion Pipeline, Stable IDs, and Evidence Management."""

import io
import docx
from pypdf import PdfWriter
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.evidence import EvidenceItem, ExperienceRecord, Skill
from app.models.profile import CandidateProfile
from app.models.user import User
from app.services.document_parser import (
    EmptyDocumentError,
    UnsupportedFileFormatError,
    parse_document,
)


def create_mock_docx(paragraphs: list[str]) -> bytes:
    """Helper to create an in-memory DOCX binary."""
    doc = docx.Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def test_document_parser_txt():
    """Test parsing plaintext binary."""
    content = b"Alex Morgan\nSenior AI Engineer\nExperience:\n- Built high throughput systems"
    parsed = parse_document(content, "resume.txt")
    assert "Alex Morgan" in parsed
    assert "Built high throughput systems" in parsed


def test_document_parser_docx():
    """Test parsing DOCX binary."""
    docx_bytes = create_mock_docx([
        "Jane Doe",
        "Staff Software Engineer - Munich, Germany",
        "Experience",
        "- Engineered distributed database pipeline with 99.99% uptime",
    ])
    parsed = parse_document(docx_bytes, "resume.docx")
    assert "Jane Doe" in parsed
    assert "Staff Software Engineer" in parsed


def test_document_parser_empty_error():
    """Test that empty or unreadable files raise EmptyDocumentError."""
    with pytest.raises(EmptyDocumentError):
        parse_document(b"   \n   ", "empty.txt")


def test_cv_parse_text_endpoint(client: TestClient, sample_user: User, auth_headers: dict, db_session: Session):
    """Test parsing raw CV text via /api/v1/cv/parse-text."""
    cv_payload = {
        "text": """
Youssof El Karhani
AI & Automation Lead - Munich, Germany
Phone: +49 170 1234567
LinkedIn: https://linkedin.com/in/youssofkarhani

Professional Experience:
RUYA Advisory - AI & Automation Lead
- Architected the Ruya Central Hub middleware in Python and Flask.
- Developed secure headless payment system with OAuth2.

Skills:
Python, FastAPI, PostgreSQL, PyTorch, Docker

Projects:
Sentimental Chatbot - Discord AI bot with custom neural network

Education:
University of Balamand - Bachelor of Science in Computer Science

Certifications:
Model Context Protocol (MCP) - DeepLearning.AI
"""
    }

    response = client.post("/api/v1/cv/parse-text", json=cv_payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "summary" in data
    summary = data["summary"]
    assert summary["experiences_extracted"] >= 1
    assert summary["skills_extracted"] >= 1

    # Verify stable IDs in database
    bullets = db_session.query(EvidenceItem).filter(EvidenceItem.user_id == sample_user.id).all()
    assert len(bullets) >= 1
    assert any(b.stable_id == "EXP_001" for b in bullets)
    assert all(b.is_verified is False for b in bullets)  # Draft staging invariant

    skills = db_session.query(Skill).filter(Skill.user_id == sample_user.id).all()
    assert len(skills) >= 1
    assert any(s.stable_id == "SKILL_001" for s in skills)


def test_cv_upload_file_endpoint(client: TestClient, sample_user: User, auth_headers: dict, db_session: Session):
    """Test uploading a file via multipart /api/v1/cv/upload."""
    docx_bytes = create_mock_docx([
        "Alice Johnson",
        "Lead DevOps Engineer - Berlin, Germany",
        "Experience:",
        "TechCorp - Senior Infrastructure Lead",
        "- Automated Kubernetes multi-cluster deployment reducing lead time by 60%.",
        "Skills:",
        "Kubernetes, Terraform, AWS, Docker, Python",
    ])

    files = {"file": ("alice_cv.docx", io.BytesIO(docx_bytes), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    response = client.post("/api/v1/cv/upload", files=files, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["filename"] == "alice_cv.docx"


def test_get_profile_and_verify_evidence(client: TestClient, sample_user: User, auth_headers: dict, db_session: Session):
    """Test retrieving complete profile and verifying evidence items."""
    # First parse CV to populate evidence bank
    client.post(
        "/api/v1/cv/parse-text",
        json={"text": "Alex Morgan\nAI Engineer\nExperience:\nAlpha Corp - Developer\n- Built API gateway\nSkills:\nPython, FastAPI"},
        headers=auth_headers,
    )

    # 1. Fetch Profile
    res = client.get("/api/v1/profile", headers=auth_headers)
    assert res.status_code == 200
    p_data = res.json()
    assert p_data["user_id"] == str(sample_user.id)
    assert "evidence_bank" in p_data
    exp_list = p_data["evidence_bank"]["experiences"]
    assert len(exp_list) >= 1
    first_bullet = exp_list[0]["bullets"][0]
    assert first_bullet["stable_id"] == "EXP_001"
    assert first_bullet["is_verified"] is False

    # 2. Toggle Verification for EXP_001
    v_res = client.post(
        "/api/v1/profile/evidence/verify",
        json={"item_id": "EXP_001", "item_type": "experience_bullet", "is_verified": True},
        headers=auth_headers,
    )
    assert v_res.status_code == 200
    assert v_res.json()["is_verified"] is True

    # 3. Check that EXP_001 is now verified in profile
    res2 = client.get("/api/v1/profile", headers=auth_headers)
    updated_bullet = res2.json()["evidence_bank"]["experiences"][0]["bullets"][0]
    assert updated_bullet["is_verified"] is True

    # 4. Verify All
    v_all = client.post("/api/v1/profile/evidence/verify-all", headers=auth_headers)
    assert v_all.status_code == 200

    res3 = client.get("/api/v1/profile", headers=auth_headers)
    skills = res3.json()["evidence_bank"]["skills"]
    assert all(s["is_verified"] is True for s in skills)


def test_update_profile_metadata(client: TestClient, sample_user: User, auth_headers: dict):
    """Test updating candidate profile headline and summary."""
    update_payload = {
        "headline": "Principal Systems Architect",
        "location": "Berlin, Germany",
        "summary": "Seasoned distributed systems architect.",
    }
    response = client.put("/api/v1/profile", json=update_payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["headline"] == "Principal Systems Architect"
    assert data["location"] == "Berlin, Germany"
    assert data["summary"] == "Seasoned distributed systems architect."
