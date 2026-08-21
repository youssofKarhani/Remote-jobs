"""Integration tests for Job Discovery, Deduplication, and Deterministic Filtering Services."""

from datetime import datetime, timezone
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.job import Job, JobSourceRecord
from app.models.preference import CandidatePreference
from app.models.user import User
from app.protocols.job_source import RawJobDTO
from app.services.job_deduplication import (
    compute_content_hash,
    job_deduplication_service,
    sanitize_job_title,
)
from app.services.job_filtering import (
    deterministic_filter_service,
    DeterministicFilterService,
)


def test_compute_content_hash_invariance():
    """Test that URL query parameters and gender markers do not change content hash."""
    h1 = compute_content_hash(
        url="https://arbeitnow.com/jobs/senior-dev-123?ref=feed&utm_source=email",
        title="Senior Backend Engineer (m/w/d)",
        company="TechCorp GmbH",
        location="Berlin, Germany",
    )
    h2 = compute_content_hash(
        url="https://arbeitnow.com/jobs/senior-dev-123",
        title="Senior Backend Engineer",
        company="techcorp gmbh",
        location="berlin, germany",
    )
    assert h1 == h2


def test_sanitize_job_title():
    """Test title cleaning."""
    clean = sanitize_job_title("Lead AI Architect (m/f/d) [Remote]")
    assert "(m/f/d)" not in clean
    assert "[Remote]" not in clean
    assert "Lead AI Architect" in clean


def test_job_deduplication_service(db_session: Session):
    """Test deduplication during batch job ingestion."""
    raw_jobs = [
        RawJobDTO(
            source_name="arbeitnow",
            external_id="job-slug-1",
            external_url="https://arbeitnow.com/jobs/job-slug-1",
            title="Senior Python Engineer",
            company_name="Alpha Tech",
            location="Berlin, Germany",
            remote=True,
            description="Build scalable microservices in Python.",
            tags=["Python", "FastAPI"],
            job_types=["Full Time"],
            published_at=datetime.now(timezone.utc),
        ),
        RawJobDTO(
            source_name="arbeitnow",
            external_id="job-slug-2",
            external_url="https://arbeitnow.com/jobs/job-slug-2",
            title="Fullstack React Engineer",
            company_name="Beta Innovations",
            location="Munich, Germany",
            remote=False,
            description="Develop front-end components.",
            tags=["React", "TypeScript"],
            job_types=["Full Time"],
            published_at=datetime.now(timezone.utc),
        ),
    ]

    # First ingestion
    stats1 = job_deduplication_service.ingest_raw_jobs(db_session, raw_jobs, source_name="arbeitnow")
    assert stats1["new_jobs_inserted"] == 2
    assert stats1["duplicates_skipped"] == 0

    assert db_session.query(Job).count() == 2
    assert db_session.query(JobSourceRecord).count() == 2

    # Second ingestion with duplicate batch
    stats2 = job_deduplication_service.ingest_raw_jobs(db_session, raw_jobs, source_name="arbeitnow")
    assert stats2["new_jobs_inserted"] == 0
    assert stats2["duplicates_skipped"] == 2

    # DB row count remains 2
    assert db_session.query(Job).count() == 2


def test_deterministic_filter_service():
    """Test zero-cost deterministic filtering with candidate preferences."""
    pref = CandidatePreference(
        target_roles=["Python Developer", "AI Engineer"],
        locations=["Germany", "Berlin"],
        remote_only=True,
        job_types=["Full Time"],
        excluded_companies=["SpammyCorp"],
        excluded_keywords=["Wordpress", "PHP"],
        min_salary=Decimal("80000"),
    )

    # Eligible Job
    matching_job = Job(
        title="Senior Python Developer",
        company_name="Reliable Tech GmbH",
        location="Berlin, Germany",
        remote=True,
        job_types=["Full Time"],
        tags=["Python"],
        description="Great engineering environment.",
        salary_min=Decimal("85000"),
        salary_max=Decimal("95000"),
        url="https://example.com/job1",
        slug="slug-1",
        content_hash="hash1",
        published_at=datetime.now(timezone.utc),
    )
    assert DeterministicFilterService.is_job_eligible(matching_job, pref) is True

    # Ineligible: Non-remote when remote_only is True
    onsite_job = Job(
        title="Python Developer",
        company_name="Reliable Tech GmbH",
        location="Berlin, Germany",
        remote=False,
        job_types=["Full Time"],
        description="Onsite office only.",
        url="https://example.com/job2",
        slug="slug-2",
        content_hash="hash2",
        published_at=datetime.now(timezone.utc),
    )
    assert DeterministicFilterService.is_job_eligible(onsite_job, pref) is False

    # Ineligible: Excluded company
    spam_job = Job(
        title="AI Engineer",
        company_name="SpammyCorp Recruiting",
        location="Berlin, Germany",
        remote=True,
        job_types=["Full Time"],
        description="Join us.",
        url="https://example.com/job3",
        slug="slug-3",
        content_hash="hash3",
        published_at=datetime.now(timezone.utc),
    )
    assert DeterministicFilterService.is_job_eligible(spam_job, pref) is False

    # Ineligible: Excluded keyword (Wordpress)
    wp_job = Job(
        title="Python Developer with Wordpress",
        company_name="Web Studio",
        location="Berlin, Germany",
        remote=True,
        job_types=["Full Time"],
        description="Maintain our legacy Wordpress backend.",
        url="https://example.com/job4",
        slug="slug-4",
        content_hash="hash4",
        published_at=datetime.now(timezone.utc),
    )
    assert DeterministicFilterService.is_job_eligible(wp_job, pref) is False


def test_deterministic_filter_word_boundary_precision():
    """Test regex word boundary precision preventing false positives (e.g. 'IT' in 'with')."""
    pref = CandidatePreference(
        excluded_keywords=["IT"],
        remote_only=False,
    )
    job_with = Job(
        title="Python Engineer",
        company_name="Tech Co",
        location="Munich",
        remote=True,
        description="Engineer with strong experience in Python.",  # Contains 'with'
        url="https://example.com/job-with",
        slug="job-with",
        content_hash="hash-with",
        published_at=datetime.now(timezone.utc),
    )
    # 'with' does NOT trigger word boundary match for 'IT'
    assert DeterministicFilterService.is_job_eligible(job_with, pref) is True

    job_it = Job(
        title="IT Support Specialist",
        company_name="Tech Co",
        location="Munich",
        remote=True,
        description="Handle IT tickets.",
        url="https://example.com/job-it",
        slug="job-it",
        content_hash="hash-it",
        published_at=datetime.now(timezone.utc),
    )
    # Isolated 'IT' triggers exclusion
    assert DeterministicFilterService.is_job_eligible(job_it, pref) is False


def test_german_job_type_mapping():
    """Test mapping German 'Werkstudent' to 'Working Student'."""
    pref = CandidatePreference(
        job_types=["Working Student"],
        remote_only=False,
    )
    german_student_job = Job(
        title="Werkstudent Backend Development",
        company_name="Munich AI GmbH",
        location="Munich",
        remote=False,
        job_types=["Teilzeit"],
        description="Unterstütze unser Entwicklungsteam.",
        url="https://example.com/werkstudent",
        slug="job-ws",
        content_hash="hash-ws",
        published_at=datetime.now(timezone.utc),
    )
    assert DeterministicFilterService.is_job_eligible(german_student_job, pref) is True


def test_jobs_api_endpoints(client: TestClient, sample_user: User, auth_headers: dict, db_session: Session):
    """Test /api/v1/jobs list, query params, preferences, and detail endpoints."""
    # Seed a test job
    job = Job(
        title="Senior AI Engineer",
        sanitized_title="Senior AI Engineer",
        company_name="Cortex AI",
        location="Munich, Germany",
        remote=True,
        job_types=["Full Time"],
        tags=["Python", "PyTorch"],
        description="Build state of the art models.",
        url="https://arbeitnow.com/jobs/cortex-ai-1",
        slug="cortex-ai-senior-ai-engineer-1",
        content_hash="content-hash-cortex-1",
        published_at=datetime.now(timezone.utc),
    )
    db_session.add(job)
    db_session.commit()

    # 1. GET /api/v1/jobs
    res = client.get("/api/v1/jobs?page=1&limit=10", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["pagination"]["total_items"] >= 1
    assert data["items"][0]["title"] == "Senior AI Engineer"

    # 2. GET /api/v1/jobs/{id}
    res_detail = client.get(f"/api/v1/jobs/{job.id}", headers=auth_headers)
    assert res_detail.status_code == 200
    assert res_detail.json()["company_name"] == "Cortex AI"

    # 3. GET /api/v1/preferences
    res_pref = client.get("/api/v1/preferences", headers=auth_headers)
    assert res_pref.status_code == 200

    # 4. PUT /api/v1/preferences
    update_pref = {
        "target_roles": ["AI Engineer"],
        "locations": ["Munich", "Berlin"],
        "remote_only": True,
        "min_salary": 90000,
    }
    res_pref_update = client.put("/api/v1/preferences", json=update_pref, headers=auth_headers)
    assert res_pref_update.status_code == 200
    assert res_pref_update.json()["remote_only"] is True
    assert res_pref_update.json()["target_roles"] == ["AI Engineer"]
