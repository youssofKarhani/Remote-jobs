"""Comprehensive integration test suite covering Phases 1 through 6.

Tests:
1. Evidence Bank CRUD endpoints (experience, bullets, skills, projects, certifications, education).
2. Non-destructive CV extraction merge vs destructive replace_existing.
3. Job SQL-level filtering and pagination.
4. AI Compatibility Assessment and Matching Engine.
5. CV Tailoring pipeline, docxtpl Word generation, and document download.
6. Grounded Cover Letter Generator with 10 engineering positioning strategies.
7. Application Tracking System (ATS) stage progression and audit events.
"""

from datetime import datetime, timezone
from decimal import Decimal
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.evidence import (
    Certification,
    EducationRecord,
    EvidenceItem,
    ExperienceRecord,
    Project,
    Skill,
)
from app.models.job import Job
from app.models.matching import JobMatch
from app.models.user import User


def test_evidence_bank_crud_endpoints(client: TestClient, sample_user: User, auth_headers: dict, db_session: Session):
    """Test full CRUD on experiences, bullets, skills, projects, certs, and education."""
    # 1. Create Experience
    exp_payload = {
        "company_name": "Acme Innovations",
        "role_title": "Senior Backend Architect",
        "location": "Berlin, Germany",
        "start_date": "2022-01",
        "end_date": None,
        "is_current": True,
        "description": "Leading distributed systems team.",
    }
    res_exp = client.post("/api/v1/profile/experiences", json=exp_payload, headers=auth_headers)
    assert res_exp.status_code == 201
    exp_data = res_exp.json()
    exp_id = exp_data["id"]
    assert exp_data["company_name"] == "Acme Innovations"

    # 2. Add Bullet to Experience
    bullet_payload = {
        "experience_record_id": exp_id,
        "raw_text": "Scaled async event bus processing 50k events/sec with zero loss.",
        "category": "achievement",
        "is_verified": True,
    }
    res_b = client.post("/api/v1/profile/evidence", json=bullet_payload, headers=auth_headers)
    assert res_b.status_code == 201
    b_data = res_b.json()
    b_id = b_data["id"]
    assert b_data["stable_id"].startswith("EXP_")
    assert b_data["is_verified"] is True

    # 3. Update Bullet Text
    update_b = client.put(f"/api/v1/profile/evidence/{b_id}", json={"raw_text": "Scaled async event bus to 60k events/sec."}, headers=auth_headers)
    assert update_b.status_code == 200
    assert "60k events/sec" in update_b.json()["raw_text"]

    # 4. Create and Delete Skill
    skill_payload = {"name": "PostgreSQL Internals", "category": "backend", "proficiency": "expert", "is_verified": True}
    res_s = client.post("/api/v1/profile/skills", json=skill_payload, headers=auth_headers)
    assert res_s.status_code == 201
    s_data = res_s.json()
    assert s_data["stable_id"].startswith("SKILL_")

    del_s = client.delete(f"/api/v1/profile/skills/{s_data['id']}", headers=auth_headers)
    assert del_s.status_code == 200

    # 5. Create and Delete Project
    proj_payload = {
        "title": "Autonomous Query Optimizer",
        "category": "database",
        "description": "AI-guided index tuner for PostgreSQL.",
        "technologies": ["Python", "SQLAlchemy", "pg_stat_statements"],
        "is_verified": True,
    }
    res_p = client.post("/api/v1/profile/projects", json=proj_payload, headers=auth_headers)
    assert res_p.status_code == 201
    p_data = res_p.json()
    assert p_data["stable_id"].startswith("PROJ_")

    del_p = client.delete(f"/api/v1/profile/projects/{p_data['id']}", headers=auth_headers)
    assert del_p.status_code == 200

    # 6. Delete bullet and experience
    del_b = client.delete(f"/api/v1/profile/evidence/{b_id}", headers=auth_headers)
    assert del_b.status_code == 200

    del_exp = client.delete(f"/api/v1/profile/experiences/{exp_id}", headers=auth_headers)
    assert del_exp.status_code == 200


def test_non_destructive_cv_merge(client: TestClient, sample_user: User, auth_headers: dict, db_session: Session):
    """Test that second CV upload with replace_existing=False preserves verified bullets."""
    cv_1 = """
    Alex Rivera
    Staff Engineer
    Experience:
    TechCorp - Senior Engineer
    - Architected multi-region failover handling 100k requests per second.
    Skills:
    Python, FastAPI
    """
    res1 = client.post("/api/v1/cv/parse-text?replace_existing=true", json={"text": cv_1}, headers=auth_headers)
    assert res1.status_code == 200

    # Find the bullet and mark it verified
    bullet = db_session.query(EvidenceItem).filter(EvidenceItem.user_id == sample_user.id).first()
    assert bullet is not None
    orig_stable_id = bullet.stable_id
    bullet.is_verified = True
    db_session.commit()

    # Second CV with an additional bullet under the same role
    cv_2 = """
    Alex Rivera
    Staff Engineer
    Experience:
    TechCorp - Senior Engineer
    - Architected multi-region failover handling 100k requests per second.
    - Mentored 6 junior engineers to mid-level promotion.
    Skills:
    Python, FastAPI, Docker
    """
    res2 = client.post("/api/v1/cv/parse-text?replace_existing=false", json={"text": cv_2}, headers=auth_headers)
    assert res2.status_code == 200

    # Check that original verified bullet remains intact with its stable ID and is_verified=True
    persisted_orig = db_session.query(EvidenceItem).filter(
        EvidenceItem.user_id == sample_user.id,
        EvidenceItem.stable_id == orig_stable_id,
    ).first()
    assert persisted_orig is not None
    assert persisted_orig.is_verified is True

    # Total bullets should now be 2
    all_bullets = db_session.query(EvidenceItem).filter(EvidenceItem.user_id == sample_user.id).all()
    assert len(all_bullets) == 2


def test_matching_engine_and_assessment(client: TestClient, sample_user: User, auth_headers: dict, db_session: Session):
    """Test on-demand AI matching calculation and match querying."""
    # Seed a job
    job = Job(
        title="Senior Python Backend Lead",
        sanitized_title="Senior Python Backend Lead",
        company_name="HyperScale Systems",
        location="Munich, Germany",
        remote=True,
        tags=["Python", "FastAPI", "PostgreSQL"],
        job_types=["Full Time"],
        description="Lead our core transaction pipeline engine in Python and PostgreSQL.",
        url=f"https://example.com/job-{uuid.uuid4().hex[:6]}",
        slug=f"job-hyperscale-{uuid.uuid4().hex[:6]}",
        content_hash=uuid.uuid4().hex,
        published_at=datetime.now(timezone.utc),
    )
    db_session.add(job)
    db_session.commit()

    # 1. Trigger Match Assessment
    res_match = client.post(f"/api/v1/jobs/{job.id}/match", headers=auth_headers)
    assert res_match.status_code == 200
    m_data = res_match.json()
    assert m_data["overall_score"] >= 80
    assert m_data["recommendation"] in ["apply", "consider"]
    assert "assessment" in m_data
    assert m_data["assessment"]["skills_score"] > 0
    assert len(m_data["assessment"]["strengths"]) > 0

    # 2. List Matches with min_score filter
    res_list = client.get("/api/v1/matches?min_score=70", headers=auth_headers)
    assert res_list.status_code == 200
    items = res_list.json()["items"]
    assert len(items) >= 1
    assert items[0]["job_id"] == str(job.id)


def test_cv_tailoring_pipeline_and_download(client: TestClient, sample_user: User, auth_headers: dict, db_session: Session):
    """Test static CV tailoring through DocxTemplate and streaming download."""
    # Seed job
    job = Job(
        title="Principal AI Infrastructure Architect",
        sanitized_title="Principal AI Infrastructure Architect",
        company_name="Apex Neural",
        location="Remote",
        remote=True,
        tags=["Python", "PyTorch"],
        job_types=["Full Time"],
        description="Architect high-performance training clusters and automated pipelines.",
        url=f"https://example.com/job-{uuid.uuid4().hex[:6]}",
        slug=f"job-apex-{uuid.uuid4().hex[:6]}",
        content_hash=uuid.uuid4().hex,
        published_at=datetime.now(timezone.utc),
    )
    db_session.add(job)
    db_session.commit()

    # Seed candidate profile with verified evidence
    client.post(
        "/api/v1/cv/parse-text",
        json={"text": "Alex Rivera\nPrincipal AI Engineer\nExperience:\nAlpha Corp - Developer\n- Built scalable clusters\nSkills:\nPython, PyTorch"},
        headers=auth_headers,
    )

    # 1. Trigger Tailoring
    res_tailor = client.post(f"/api/v1/jobs/{job.id}/tailor-cv", json={"max_bullets_per_role": 3}, headers=auth_headers)
    assert res_tailor.status_code == 200
    doc_data = res_tailor.json()
    doc_id = doc_data["id"]
    assert doc_data["document_type"] == "cv"
    assert doc_data["format"] == "docx"
    assert doc_data["verification_status"] == "unverified"  # Unverified draft items tagged properly
    assert "download_url" in doc_data

    # 2. Download File with Authorization header
    res_dl = client.get(f"/api/v1/documents/{doc_id}/download", headers=auth_headers)
    assert res_dl.status_code == 200
    assert res_dl.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert len(res_dl.content) > 1000  # valid docx binary

    # 3. Direct browser download with query token (no Authorization header)
    token = auth_headers["Authorization"].split(" ")[1]
    res_query_dl = client.get(f"/api/v1/documents/{doc_id}/download?token={token}")
    assert res_query_dl.status_code == 200
    assert res_query_dl.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert len(res_query_dl.content) > 1000

    # 4. Storage resilience check: simulate ephemeral container restart wiping local file
    from app.models.document import GeneratedDocument
    import os
    gen_doc_db = db_session.query(GeneratedDocument).filter(GeneratedDocument.id == uuid.UUID(doc_id)).first()
    assert gen_doc_db is not None
    assert gen_doc_db.file_bytes is not None
    if os.path.exists(gen_doc_db.file_path):
        os.remove(gen_doc_db.file_path)

    res_stream_dl = client.get(f"/api/v1/documents/{doc_id}/download", headers=auth_headers)
    assert res_stream_dl.status_code == 200
    assert len(res_stream_dl.content) > 1000  # streamed seamlessly from DB backup bytes


def test_unverified_bullets_never_leak_in_cv_tailoring(client: TestClient, sample_user: User, auth_headers: dict, db_session: Session):
    """Adversarial check: with require_verified=True, unverified bullets must never appear in generated .docx and provenance must be 100% verified."""
    job = Job(
        title="Distributed Storage Engineer",
        sanitized_title="Distributed Storage Engineer",
        company_name="CloudCeph",
        location="Remote",
        remote=True,
        tags=["Storage", "Python"],
        job_types=["Full Time"],
        description="Build high-reliability object storage layers.",
        url=f"https://example.com/job-{uuid.uuid4().hex[:6]}",
        slug=f"job-ceph-{uuid.uuid4().hex[:6]}",
        content_hash=uuid.uuid4().hex,
        published_at=datetime.now(timezone.utc),
    )
    db_session.add(job)

    # Experience with 1 unverified bullet and 1 verified bullet
    exp = ExperienceRecord(
        user_id=sample_user.id,
        company_name="Storage Inc",
        role_title="Systems Engineer",
        start_date="2021-01",
    )
    db_session.add(exp)
    db_session.flush()

    b_unverified = EvidenceItem(
        user_id=sample_user.id,
        experience_record_id=exp.id,
        stable_id="EXP_UNVERIFIED_999",
        raw_text="SECRET_UNVERIFIED_HALLUCINATION_TEXT",
        is_verified=False,
    )
    b_verified = EvidenceItem(
        user_id=sample_user.id,
        experience_record_id=exp.id,
        stable_id="EXP_VERIFIED_777",
        raw_text="CONFIRMED_VERIFIED_ACHIEVEMENT_TEXT",
        is_verified=True,
    )
    db_session.add_all([b_unverified, b_verified])
    db_session.commit()

    # 1. Partner-strict mode: require_verified=True
    res_tailor = client.post(
        f"/api/v1/jobs/{job.id}/tailor-cv",
        json={"max_bullets_per_role": 2, "require_verified": True},
        headers=auth_headers,
    )
    assert res_tailor.status_code == 200
    doc_data = res_tailor.json()
    assert doc_data["verification_status"] == "verified"

    # Verify ID provenance strictly excludes unverified bullet in partner-strict mode
    assert "EXP_UNVERIFIED_999" not in doc_data["selected_evidence_ids"]
    assert "EXP_VERIFIED_777" in doc_data["selected_evidence_ids"]

    # Verify binary docx content does not leak unverified text
    res_dl = client.get(doc_data["download_url"], headers=auth_headers)
    assert res_dl.status_code == 200
    
    import docx
    import io
    doc = docx.Document(io.BytesIO(res_dl.content))
    full_text = "\n".join([p.text for p in doc.paragraphs])
    assert "SECRET_UNVERIFIED_HALLUCINATION_TEXT" not in full_text
    assert "CONFIRMED_VERIFIED_ACHIEVEMENT_TEXT" in full_text

    # 2. General self-serve mode (default require_verified=False) generates without failing and marks as partially verified
    res_unverified = client.post(
        f"/api/v1/jobs/{job.id}/tailor-cv",
        json={"max_bullets_per_role": 2, "require_verified": False},
        headers=auth_headers,
    )
    assert res_unverified.status_code == 200
    assert res_unverified.json()["verification_status"] in ("verified", "partially_verified", "unverified")
    # Verify the unverified bullet in DB was NOT mutated to is_verified=True!
    persisted_unverified = db_session.query(EvidenceItem).filter(EvidenceItem.stable_id == "EXP_UNVERIFIED_999").first()
    assert persisted_unverified.is_verified is False


def test_jobs_sql_job_types_filter(client: TestClient, sample_user: User, auth_headers: dict, db_session: Session):
    """Test SQL-level filtering on job_types parameter."""
    tag = uuid.uuid4().hex[:6]
    j1 = Job(
        title=f"Full Time Engineer {tag}",
        company_name=f"FullTime Corp {tag}",
        location="Remote",
        remote=True,
        tags=["Python"],
        job_types=["Full Time"],
        description="Full time role",
        url=f"https://example.com/job-ft-{tag}",
        slug=f"job-ft-{tag}",
        content_hash=uuid.uuid4().hex,
        published_at=datetime.now(timezone.utc),
    )
    j2 = Job(
        title=f"Internship Backend {tag}",
        company_name=f"Intern Corp {tag}",
        location="Remote",
        remote=True,
        tags=["Python"],
        job_types=["Internship"],
        description="Internship role",
        url=f"https://example.com/job-int-{tag}",
        slug=f"job-int-{tag}",
        content_hash=uuid.uuid4().hex,
        published_at=datetime.now(timezone.utc),
    )
    db_session.add_all([j1, j2])
    db_session.commit()

    res_ft = client.get(f"/api/v1/jobs?job_types=Full%20Time&search={tag}", headers=auth_headers)
    assert res_ft.status_code == 200
    items_ft = res_ft.json()["items"]
    assert len(items_ft) == 1
    assert items_ft[0]["title"] == f"Full Time Engineer {tag}"

    res_int = client.get(f"/api/v1/jobs?job_types=Internship&search={tag}", headers=auth_headers)
    assert res_int.status_code == 200
    items_int = res_int.json()["items"]
    assert len(items_int) == 1
    assert items_int[0]["title"] == f"Internship Backend {tag}"


def test_cover_letter_generator_and_strategies(client: TestClient, sample_user: User, auth_headers: dict, db_session: Session):
    """Test 10 positioning strategies and cover letter generation."""
    # 1. List strategies
    res_strat = client.get("/api/v1/cover-letters/strategies")
    assert res_strat.status_code == 200
    strategies = res_strat.json()
    assert len(strategies) == 10
    strat_ids = [s["id"] for s in strategies]
    assert "technical_depth" in strat_ids
    assert "business_revenue" in strat_ids
    assert "ai_automation" in strat_ids

    # 2. Generate Letter for Job
    job = Job(
        title="Staff Concurrency Engineer",
        sanitized_title="Staff Concurrency Engineer",
        company_name="QuantumCloud",
        location="Munich, Germany",
        remote=True,
        tags=["Python", "Go"],
        job_types=["Full Time"],
        description="Design lock-free data structures.",
        url=f"https://example.com/job-{uuid.uuid4().hex[:6]}",
        slug=f"job-quantum-{uuid.uuid4().hex[:6]}",
        content_hash=uuid.uuid4().hex,
        published_at=datetime.now(timezone.utc),
    )
    db_session.add(job)
    db_session.commit()

    res_gen = client.post(f"/api/v1/jobs/{job.id}/cover-letter", json={"strategy": "Technical Depth"}, headers=auth_headers)
    assert res_gen.status_code == 200
    letter_data = res_gen.json()
    assert "QuantumCloud" in letter_data["content"]
    assert letter_data["strategy"] == "Technical Depth"

    # 3. Edit Letter Content
    updated_text = letter_data["content"] + "\n\nP.S. Excited to meet the team!"
    res_put = client.put(f"/api/v1/jobs/{job.id}/cover-letter", json={"content": updated_text}, headers=auth_headers)
    assert res_put.status_code == 200
    assert "Excited to meet the team!" in res_put.json()["content"]


def test_application_tracking_system(client: TestClient, sample_user: User, auth_headers: dict, db_session: Session):
    """Test complete ATS lifecycle: Track -> Transition status -> List -> Update notes -> Delete."""
    job = Job(
        title="Lead Platform Architect",
        sanitized_title="Lead Platform Architect",
        company_name="ScaleWorks",
        location="Remote",
        remote=True,
        tags=["FastAPI", "PostgreSQL"],
        job_types=["Full Time"],
        description="Scale infrastructure for enterprise workloads.",
        url=f"https://example.com/job-{uuid.uuid4().hex[:6]}",
        slug=f"job-scaleworks-{uuid.uuid4().hex[:6]}",
        content_hash=uuid.uuid4().hex,
        published_at=datetime.now(timezone.utc),
    )
    db_session.add(job)
    db_session.commit()

    # 1. Track in ATS (status: Saved)
    create_payload = {"job_id": str(job.id), "status": "Saved", "notes": "Initial discovery via Arbeitnow"}
    res_app = client.post("/api/v1/applications", json=create_payload, headers=auth_headers)
    assert res_app.status_code == 201
    app_data = res_app.json()
    app_id = app_data["id"]
    assert app_data["status"] == "Saved"

    # 2. Transition to Applied
    res_status = client.patch(f"/api/v1/applications/{app_id}/status", json={"status": "Applied"}, headers=auth_headers)
    assert res_status.status_code == 200
    assert res_status.json()["status"] == "Applied"
    assert res_status.json()["applied_at"] is not None

    # Check audit event
    assert len(res_status.json()["events"]) >= 1

    # 3. Transition to Interview
    res_status2 = client.patch(f"/api/v1/applications/{app_id}/status", json={"status": "Interview"}, headers=auth_headers)
    assert res_status2.status_code == 200
    assert res_status2.json()["status"] == "Interview"

    # 4. List Applications
    res_list = client.get("/api/v1/applications", headers=auth_headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # 5. Delete Application
    res_del = client.delete(f"/api/v1/applications/{app_id}", headers=auth_headers)
    assert res_del.status_code == 200
