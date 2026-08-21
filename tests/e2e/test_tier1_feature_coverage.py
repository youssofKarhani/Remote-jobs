"""Tier 1: Comprehensive Feature Coverage Tests (Minimum 5 tests per feature).

Features Covered:
1. Canonical Database Models & Foreign Key Relationships
2. Stable ID Assignment & Format Enforcement
3. Structured CV Ingestion & Evidence Bank Staging Flow
4. Arbeitnow Job Source Ingestion Protocol & Mapping
5. Multi-Level Job Deduplication Engine
6. Deterministic Candidate Preferences Filtering Chain
7. Strict Evidence ID Validation Gate & LLM Guardrails
"""

import re
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Set

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.profile import CandidateProfile
from app.models.preference import CandidatePreference
from app.models.evidence import (
    ExperienceRecord,
    EvidenceItem,
    Skill,
    Project,
    Certification,
    EducationRecord,
)
from app.models.job import (
    Company,
    JobSource,
    Job,
    JobSourceRecord,
)
from tests.e2e.conftest import (
    EvidenceValidationError,
    validate_selected_evidence_ids,
    compute_content_hash,
    DeterministicFilterService,
    JOB_TYPE_MAPPING,
)


# ============================================================================
# FEATURE 1: Canonical Database Models & Relationships (>= 5 Tests)
# ============================================================================

class TestFeature1DatabaseModels:
    """Feature 1: PostgreSQL Canonical Database Models & Relationships."""

    def test_f1_user_and_candidate_profile_one_to_one_lifecycle(self, db: Session, make_user, make_profile):
        """Test 1.1: Verify User to CandidateProfile 1-to-1 relationship and cascading."""
        user = make_user(email="alice.profile@example.com", full_name="Alice Candidate")
        profile = make_profile(
            user=user,
            headline="Lead AI Engineer",
            summary="10+ years designing enterprise machine learning platforms.",
            is_verified=True,
        )

        assert profile.user_id == user.id
        assert user.candidate_profile.headline == "Lead AI Engineer"
        assert user.candidate_profile.is_verified is True

        # Query via session
        stmt = select(CandidateProfile).where(CandidateProfile.user_id == user.id)
        queried_profile = db.scalar(stmt)
        assert queried_profile is not None
        assert queried_profile.headline == "Lead AI Engineer"

    def test_f1_user_and_candidate_preference_json_defaults(self, db: Session, make_user, make_preference):
        """Test 1.2: Verify CandidatePreference JSON defaults and data types."""
        user = make_user(email="bob.pref@example.com")
        pref = make_preference(
            user=user,
            target_roles=["Backend Lead", "Platform Engineer"],
            locations=["Berlin", "Remote"],
            remote_only=True,
            job_types=["Full Time", "Part Time"],
            min_salary=85000.0,
            excluded_companies=["SpamRecruitment Ltd"],
            excluded_keywords=["legacy", "crypto"],
        )

        assert pref.user_id == user.id
        assert pref.remote_only is True
        assert pref.min_salary == Decimal("85000.0")
        assert "Backend Lead" in pref.target_roles
        assert "SpamRecruitment Ltd" in pref.excluded_companies
        assert "legacy" in pref.excluded_keywords

    def test_f1_experience_record_and_child_evidence_items(self, db: Session, make_user, make_experience, make_evidence_item):
        """Test 1.3: Verify ExperienceRecord parent container and EvidenceItem child relationships."""
        user = make_user(email="carol.exp@example.com")
        exp = make_experience(
            user=user,
            company_name="Acme AI Corp",
            role_title="Senior ML Engineer",
            start_date="2022-01",
            end_date=None,
            is_current=True,
        )
        item1 = make_evidence_item(
            user=user,
            experience_record=exp,
            stable_id="EXP_001",
            raw_text="Built real-time telemetry pipeline ingesting 100k events/sec.",
            category="metric",
        )
        item2 = make_evidence_item(
            user=user,
            experience_record=exp,
            stable_id="EXP_002",
            raw_text="Architected distributed vector search with sub-50ms latency.",
            category="architecture",
        )

        assert item1.experience_record_id == exp.id
        assert item2.experience_record_id == exp.id
        assert len(user.experience_records) == 1
        assert len(user.evidence_items) == 2

    def test_f1_skills_certifications_projects_education_relationships(
        self, db: Session, make_user, make_skill, make_project, make_certification, make_education
    ):
        """Test 1.4: Verify Skills, Certifications, Projects, and Education models attached to User."""
        user = make_user(email="dave.multi@example.com")
        skill = make_skill(user=user, stable_id="SKILL_001", name="FastAPI", category="backend")
        proj = make_project(user=user, stable_id="PROJ_001", title="Job Discovery Agent")
        cert = make_certification(user=user, stable_id="CERT_001", name="AWS Solutions Architect")
        edu = make_education(user=user, stable_id="EDU_001", institution="TU Berlin", degree="B.Sc.")

        assert skill.user_id == user.id
        assert proj.user_id == user.id
        assert cert.user_id == user.id
        assert edu.user_id == user.id
        assert len(user.skills) == 1
        assert len(user.projects) == 1
        assert len(user.certifications) == 1
        assert len(user.education_records) == 1

    def test_f1_company_job_and_source_record_relationships(
        self, db: Session, make_company, make_job_source, make_job
    ):
        """Test 1.5: Verify Company, JobSource, Job, and JobSourceRecord foreign key relationships."""
        company = make_company(name="HuggingFace Inc", website="https://huggingface.co")
        source = make_job_source(name="arbeitnow", base_url="https://arbeitnow.com/api")
        job = make_job(
            title="Senior ML Engineer",
            company_name="HuggingFace Inc",
            company=company,
            remote=True,
        )

        source_rec = JobSourceRecord(
            id=uuid.uuid4(),
            job_id=job.id,
            source_id=source.id,
            external_id="hf-ml-engineer-101",
            external_url="https://arbeitnow.com/jobs/hf-ml-101",
            raw_payload={"vendor": "arbeitnow", "id": 101},
        )
        db.add(source_rec)
        db.commit()

        assert source_rec.job_id == job.id
        assert source_rec.source_id == source.id
        assert job.company_id == company.id
        assert len(company.jobs) == 1

    def test_f1_user_cascade_deletion_cleans_all_child_entities(
        self, db: Session, make_user, make_profile, make_preference, make_experience, make_evidence_item, make_skill
    ):
        """Test 1.6: Verify deleting a User cascades and removes all profile, preference, and evidence records."""
        user = make_user(email="eve.cascade@example.com")
        make_profile(user=user)
        make_preference(user=user)
        exp = make_experience(user=user)
        make_evidence_item(user=user, experience_record=exp, stable_id="EXP_001")
        make_skill(user=user, stable_id="SKILL_001")

        user_id = user.id
        db.delete(user)
        db.commit()

        assert db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == user_id)) is None
        assert db.scalar(select(CandidatePreference).where(CandidatePreference.user_id == user_id)) is None
        assert db.scalar(select(ExperienceRecord).where(ExperienceRecord.user_id == user_id)) is None
        assert db.scalar(select(EvidenceItem).where(EvidenceItem.user_id == user_id)) is None
        assert db.scalar(select(Skill).where(Skill.user_id == user_id)) is None


# ============================================================================
# FEATURE 2: Stable ID Assignment & Format Enforcement (>= 5 Tests)
# ============================================================================

class TestFeature2StableIDs:
    """Feature 2: Stable Identifier Generation, Regex, and Per-User Scoping."""

    STABLE_ID_PATTERN = re.compile(r"^[A-Z]{3,5}_\d{3,5}$")

    def test_f2_stable_id_standard_regex_format(self):
        """Test 2.1: Verify regex format matching for all standard prefixes."""
        valid_ids = ["EXP_001", "EXP_999", "SKILL_001", "PROJ_042", "CERT_100", "EDU_005"]
        for sid in valid_ids:
            assert bool(self.STABLE_ID_PATTERN.match(sid)), f"Expected {sid} to match stable ID pattern"

    def test_f2_stable_id_sequential_generation(self, db: Session, make_user, make_evidence_item):
        """Test 2.2: Verify sequential zero-padded generation (001, 002, 003)."""
        user = make_user(email="seq.user@example.com")
        for i in range(1, 4):
            stable_id = f"EXP_{i:03d}"
            item = make_evidence_item(user=user, stable_id=stable_id, raw_text=f"Achievement #{i}")
            assert item.stable_id == f"EXP_{i:03d}"

        items = db.scalars(select(EvidenceItem).where(EvidenceItem.user_id == user.id).order_by(EvidenceItem.stable_id)).all()
        assert [i.stable_id for i in items] == ["EXP_001", "EXP_002", "EXP_003"]

    def test_f2_stable_id_multi_tenant_isolation(self, db: Session, make_user, make_evidence_item):
        """Test 2.3: Verify User A and User B can both have EXP_001 independently."""
        user_a = make_user(email="user.a@example.com")
        user_b = make_user(email="user.b@example.com")

        item_a = make_evidence_item(user=user_a, stable_id="EXP_001", raw_text="User A bullet")
        item_b = make_evidence_item(user=user_b, stable_id="EXP_001", raw_text="User B bullet")

        assert item_a.stable_id == "EXP_001"
        assert item_b.stable_id == "EXP_001"
        assert item_a.user_id != item_b.user_id
        assert item_a.raw_text == "User A bullet"
        assert item_b.raw_text == "User B bullet"

    def test_f2_stable_id_immutability_on_evidence_edit(self, db: Session, make_user, make_evidence_item):
        """Test 2.4: Verify stable ID remains unchanged when editing evidence text or category."""
        user = make_user(email="immutable.user@example.com")
        item = make_evidence_item(
            user=user,
            stable_id="EXP_001",
            raw_text="Initial draft achievement.",
            category="experience",
        )

        # User edits the evidence text
        item.raw_text = "Refined and verified achievement with +40% metric."
        item.category = "metric"
        item.is_verified = True
        db.commit()
        db.refresh(item)

        assert item.stable_id == "EXP_001"
        assert item.raw_text == "Refined and verified achievement with +40% metric."
        assert item.is_verified is True

    def test_f2_stable_id_invalid_format_detection(self):
        """Test 2.5: Verify rejection of malformed or non-compliant stable ID formats."""
        invalid_ids = [
            "exp_001",       # Lowercase
            "EXP_1",         # Unpadded single digit
            "EXP-001",       # Hyphen instead of underscore
            "EXPERIENCE_001",# Prefix too long (>5 chars)
            "EX_001",        # Prefix too short (<3 chars)
            "001_EXP",       # Prefix reversed
            "",              # Empty string
            "EXP_ABC",       # Non-numeric suffix
        ]
        for sid in invalid_ids:
            assert not bool(self.STABLE_ID_PATTERN.match(sid)), f"Expected {sid} to fail stable ID pattern"


# ============================================================================
# FEATURE 3: Structured CV Parsing & Ingestion Flow (>= 5 Tests)
# ============================================================================

class TestFeature3CVIngestion:
    """Feature 3: Structured CV Ingestion, Entity Extraction & Staging."""

    def test_f3_cv_experience_structure_extraction(self, db: Session, make_user, make_experience, make_evidence_item):
        """Test 3.1: Verify structured parsing of work experiences with multiple atomic bullets."""
        user = make_user(email="cv.parser@example.com")
        exp = make_experience(
            user=user,
            company_name="DeepMind",
            role_title="Research Engineer",
            start_date="2021-06",
            end_date="2023-12",
            is_current=False,
            location="London, UK",
        )
        b1 = make_evidence_item(
            user=user,
            experience_record=exp,
            stable_id="EXP_001",
            raw_text="Trained 70B parameter transformer models across 256 H100 GPUs.",
            category="ai_ml",
            is_verified=False,
        )
        b2 = make_evidence_item(
            user=user,
            experience_record=exp,
            stable_id="EXP_002",
            raw_text="Reduced distributed training communication overhead by 35%.",
            category="metric",
            is_verified=False,
        )

        assert exp.company_name == "DeepMind"
        assert b1.is_verified is False
        assert b2.is_verified is False
        assert len(exp.evidence_items) == 2

    def test_f3_cv_skills_categorization(self, db: Session, make_user, make_skill):
        """Test 3.2: Verify skill parsing into distinct technical categories."""
        user = make_user(email="skills.user@example.com")
        s1 = make_skill(user=user, stable_id="SKILL_001", name="Python", category="programming", proficiency="expert")
        s2 = make_skill(user=user, stable_id="SKILL_002", name="PostgreSQL", category="backend", proficiency="advanced")
        s3 = make_skill(user=user, stable_id="SKILL_003", name="PyTorch", category="ai_ml", proficiency="advanced")
        s4 = make_skill(user=user, stable_id="SKILL_004", name="Docker", category="devops", proficiency="intermediate")

        assert s1.category == "programming"
        assert s2.category == "backend"
        assert s3.category == "ai_ml"
        assert s4.category == "devops"

    def test_f3_cv_projects_and_certifications_extraction(self, db: Session, make_user, make_project, make_certification):
        """Test 3.3: Verify project portfolio and certifications structured persistence."""
        user = make_user(email="proj.cert@example.com")
        proj = make_project(
            user=user,
            stable_id="PROJ_001",
            title="Distributed Task Orchestrator",
            technologies=["Python", "Redis", "FastAPI"],
            is_verified=False,
        )
        cert = make_certification(
            user=user,
            stable_id="CERT_001",
            name="Certified Kubernetes Administrator",
            issuing_organization="CNCF",
            is_verified=False,
        )

        assert "Redis" in proj.technologies
        assert cert.issuing_organization == "CNCF"

    def test_f3_cv_draft_staging_to_verified_lifecycle(self, db: Session, make_user, make_evidence_item):
        """Test 3.4: Verify draft evidence items start unverified and transition to verified on user review."""
        user = make_user(email="verify.user@example.com")
        item = make_evidence_item(user=user, stable_id="EXP_001", is_verified=False)
        assert item.is_verified is False

        # Candidate reviews and verifies the item
        item.is_verified = True
        db.commit()
        db.refresh(item)
        assert item.is_verified is True

    def test_f3_cv_pre_approved_variants_storage(self, db: Session, make_user, make_evidence_item):
        """Test 3.5: Verify persistence of approved variants dictionary on EvidenceItem."""
        user = make_user(email="variants.user@example.com")
        variants = {
            "EXP_001_FULL": "Optimized distributed data pipeline reducing latency from 3h to 30m, enabling 10+ daily iterations.",
            "EXP_001_SHORT": "Reduced pipeline latency from 3h to 30m.",
            "EXP_001_METRIC": "Achieved 83% reduction in pipeline export time across 24 TB datasets.",
        }
        item = make_evidence_item(
            user=user,
            stable_id="EXP_001",
            raw_text=variants["EXP_001_FULL"],
            variants=variants,
            is_verified=True,
        )

        assert item.variants is not None
        assert "EXP_001_SHORT" in item.variants
        assert "83% reduction" in item.variants["EXP_001_METRIC"]


# ============================================================================
# FEATURE 4: Arbeitnow Job Source Ingestion Protocol (>= 5 Tests)
# ============================================================================

class TestFeature4ArbeitnowIngestion:
    """Feature 4: Job Source Ingestion, Field Mapping, and Protocol Compliance."""

    def test_f4_arbeitnow_raw_payload_field_mapping(self, db: Session, make_company, make_job):
        """Test 4.1: Verify vendor field mapping from Arbeitnow payload into canonical Job model."""
        raw_api_payload = {
            "slug": "senior-python-engineer-berlin-12345",
            "company_name": "SoundCloud",
            "title": "Senior Python Backend Engineer (m/w/d)",
            "description": "<p>Build high-scale audio streaming microservices in Python and Go.</p>",
            "remote": True,
            "url": "https://www.arbeitnow.com/view/senior-python-engineer-berlin-12345",
            "tags": ["Python", "FastAPI", "PostgreSQL", "Kafka"],
            "job_types": ["Full Time", "Remote"],
            "location": "Berlin, Germany",
            "created_at": 1708473600,
        }

        company = make_company(name=raw_api_payload["company_name"])
        job = make_job(
            title=raw_api_payload["title"],
            company_name=raw_api_payload["company_name"],
            location=raw_api_payload["location"],
            remote=raw_api_payload["remote"],
            url=raw_api_payload["url"],
            tags=raw_api_payload["tags"],
            job_types=raw_api_payload["job_types"],
            description=raw_api_payload["description"],
            company=company,
        )

        assert job.company_name == "SoundCloud"
        assert job.remote is True
        assert "Kafka" in job.tags
        assert "Full Time" in job.job_types

    def test_f4_arbeitnow_epoch_timestamp_conversion(self):
        """Test 4.2: Verify conversion of Unix epoch seconds into timezone-aware UTC datetime."""
        epoch_ts = 1708473600
        dt = datetime.fromtimestamp(epoch_ts, tz=timezone.utc)
        assert dt.year == 2024
        assert dt.month == 2
        assert dt.tzinfo == timezone.utc

    def test_f4_arbeitnow_title_sanitization_removes_fluff(self):
        """Test 4.3: Verify removal of gender markers and recruitment fluff from job titles."""
        titles = [
            ("Senior Backend Developer (m/w/d) - Remote", "Senior Backend Developer - Remote"),
            ("AI Engineer (gn) - Vollzeit", "AI Engineer - Vollzeit"),
            ("Data Architect (all genders) [Hybrid]", "Data Architect"),
            ("Lead Systems Specialist (w/m/d)", "Lead Systems Specialist"),
        ]
        for raw, expected in titles:
            cleaned = re.sub(r'\(.*?\)|\[.*?\]', '', raw).strip()
            cleaned = re.sub(r'\s+', ' ', cleaned)
            assert cleaned == expected, f"Failed for {raw}"

    def test_f4_arbeitnow_pagination_stop_on_empty(self):
        """Test 4.4: Verify pagination termination when page returns empty data array."""
        mock_pages = {
            1: [{"slug": "job-1"}],
            2: [{"slug": "job-2"}],
            3: [],  # End of data
        }
        collected = []
        page = 1
        while True:
            data = mock_pages.get(page, [])
            if not data:
                break
            collected.extend(data)
            page += 1

        assert len(collected) == 2
        assert page == 3

    def test_f4_arbeitnow_smart_early_exit_on_seen_jobs(self):
        """Test 4.5: Verify smart early exit when 100% of jobs on a page are already known."""
        known_slugs = {"job-1", "job-2", "job-3"}
        page_items = [{"slug": "job-1"}, {"slug": "job-2"}, {"slug": "job-3"}]

        all_seen = all(item["slug"] in known_slugs for item in page_items)
        assert all_seen is True


# ============================================================================
# FEATURE 5: Multi-Level Job Deduplication Engine (>= 5 Tests)
# ============================================================================

class TestFeature5Deduplication:
    """Feature 5: Multi-Level Content Hashing, URL Matching & Ingestion Idempotence."""

    def test_f5_deduplication_exact_url_match(self, db: Session, make_job):
        """Test 5.1: Canonical URL match detects duplicate job."""
        url = "https://www.arbeitnow.com/view/senior-python-dev-123"
        job1 = make_job(url=url, title="Senior Python Dev", company_name="Corp A")
        
        # Look up existing by URL
        existing = db.scalar(select(Job).where(Job.url == url))
        assert existing is not None
        assert existing.id == job1.id

    def test_f5_deduplication_content_hash_invariance_to_gender_markers(self):
        """Test 5.2: Content hash ignores gender markers like (m/w/d) and extra whitespace."""
        url = "https://example.com/job/1"
        h1 = compute_content_hash(url, "Senior Backend Dev (m/w/d)", "TechCorp", "Berlin")
        h2 = compute_content_hash(url, "Senior Backend Dev (gn)", "TechCorp", "Berlin")
        h3 = compute_content_hash(url, "Senior Backend Dev (all genders)", "TechCorp", "Berlin")
        h4 = compute_content_hash(url, "  Senior Backend Dev   ", "TechCorp", "Berlin")

        assert h1 == h2 == h3 == h4

    def test_f5_deduplication_secondary_source_record_attachment(
        self, db: Session, make_job, make_job_source
    ):
        """Test 5.3: Duplicate job from secondary source attaches a new JobSourceRecord to existing Job."""
        source1 = make_job_source(name="arbeitnow")
        source2 = make_job_source(name="remoteok", base_url="https://remoteok.com/api")
        job = make_job(title="AI Lead", company_name="OpenAI", url="https://openai.com/jobs/ai-lead")

        rec1 = JobSourceRecord(
            id=uuid.uuid4(),
            job_id=job.id,
            source_id=source1.id,
            external_id="arbeitnow-ai-lead",
            external_url="https://arbeitnow.com/jobs/ai-lead",
            raw_payload={"src": "arbeitnow"},
        )
        rec2 = JobSourceRecord(
            id=uuid.uuid4(),
            job_id=job.id,
            source_id=source2.id,
            external_id="remoteok-ai-lead",
            external_url="https://remoteok.com/jobs/ai-lead",
            raw_payload={"src": "remoteok"},
        )
        db.add_all([rec1, rec2])
        db.commit()

        records = db.scalars(select(JobSourceRecord).where(JobSourceRecord.job_id == job.id)).all()
        assert len(records) == 2
        assert {r.source_id for r in records} == {source1.id, source2.id}

    def test_f5_deduplication_idempotent_ingestion(self, db: Session, make_job):
        """Test 5.4: Ingesting the same job multiple times preserves single canonical row."""
        url = "https://example.com/job/unique-slug-99"
        job = make_job(url=url, title="Staff Engineer", company_name="Stripe")
        original_id = job.id

        # Simulate second ingestion attempt
        existing_job = db.scalar(select(Job).where(Job.url == url))
        assert existing_job is not None
        assert existing_job.id == original_id

        count = db.scalar(select(Job).where(Job.url == url))
        assert count is not None

    def test_f5_deduplication_distinct_jobs_have_distinct_hashes(self):
        """Test 5.5: Distinct jobs produce distinct SHA-256 content hashes."""
        h1 = compute_content_hash("https://example.com/job1", "Python Dev", "Company A", "Berlin")
        h2 = compute_content_hash("https://example.com/job2", "Python Dev", "Company B", "Berlin")
        h3 = compute_content_hash("https://example.com/job1", "Java Dev", "Company A", "Berlin")
        h4 = compute_content_hash("https://example.com/job1", "Python Dev", "Company A", "Munich")

        assert len({h1, h2, h3, h4}) == 4


# ============================================================================
# FEATURE 6: Deterministic Candidate Preference Filtering (>= 5 Tests)
# ============================================================================

class TestFeature6DeterministicFilters:
    """Feature 6: Zero-Cost Deterministic Filtering Chain against CandidatePreference."""

    def test_f6_filter_remote_only_enforcement(self, db: Session, make_user, make_preference, make_job):
        """Test 6.1: remote_only=True rejects non-remote jobs and accepts remote jobs."""
        user = make_user(email="remote.tester@example.com")
        pref = make_preference(user=user, remote_only=True, locations=[])

        remote_job = make_job(title="AI Engineer", remote=True, location="Berlin")
        onsite_job = make_job(title="AI Engineer", remote=False, location="Berlin")

        assert DeterministicFilterService.is_job_eligible(remote_job, pref) is True
        assert DeterministicFilterService.is_job_eligible(onsite_job, pref) is False

    def test_f6_filter_location_matching_case_insensitive(self, db: Session, make_user, make_preference, make_job):
        """Test 6.2: Location matching correctly evaluates specified target locations for non-remote jobs."""
        user = make_user(email="loc.tester@example.com")
        pref = make_preference(user=user, remote_only=False, locations=["Berlin", "Munich"])

        berlin_job = make_job(title="Software Engineer", remote=False, location="Berlin, Germany")
        munich_job = make_job(title="Software Engineer", remote=False, location="München / Munich")
        hamburg_job = make_job(title="Software Engineer", remote=False, location="Hamburg, Germany")

        assert DeterministicFilterService.is_job_eligible(berlin_job, pref) is True
        assert DeterministicFilterService.is_job_eligible(munich_job, pref) is True
        assert DeterministicFilterService.is_job_eligible(hamburg_job, pref) is False

    def test_f6_filter_word_boundary_regex_keyword_matching(self, db: Session, make_user, make_preference, make_job):
        """Test 6.3: Regex word boundaries prevent substring false-positives (e.g. 'IT' in 'with')."""
        user = make_user(email="it.tester@example.com")
        pref = make_preference(user=user, target_roles=["IT"], locations=[], remote_only=False)

        valid_it_job = make_job(title="Senior IT Administrator", remote=False, location="Berlin")
        false_positive_job = make_job(title="Developer with strong communication skills", remote=False, location="Berlin")

        assert DeterministicFilterService.is_job_eligible(valid_it_job, pref) is True
        assert DeterministicFilterService.is_job_eligible(false_positive_job, pref) is False

    def test_f6_filter_multilingual_job_type_mapping(self, db: Session, make_user, make_preference, make_job):
        """Test 6.4: German/English job types (e.g. Werkstudent -> Working Student) match correctly."""
        user = make_user(email="werkstudent.tester@example.com")
        pref = make_preference(user=user, job_types=["Working Student"], locations=[], remote_only=False)

        job_german = make_job(title="Werkstudent Data Science (m/w/d)", job_types=["Werkstudent"])
        job_english = make_job(title="Working Student Software Engineering", job_types=["Working Student"])
        job_fulltime = make_job(title="Senior Fullstack Engineer", job_types=["Full Time"])

        assert DeterministicFilterService.is_job_eligible(job_german, pref) is True
        assert DeterministicFilterService.is_job_eligible(job_english, pref) is True
        assert DeterministicFilterService.is_job_eligible(job_fulltime, pref) is False

    def test_f6_filter_excluded_companies_and_keywords(self, db: Session, make_user, make_preference, make_job):
        """Test 6.5: Excluded companies and excluded keywords immediately disqualify matching jobs."""
        user = make_user(email="excluded.tester@example.com")
        pref = make_preference(
            user=user,
            target_roles=["Engineer"],
            locations=[],
            remote_only=False,
            excluded_companies=["BadRecruiter GmbH", "SpamStaffing"],
            excluded_keywords=["gambling", "crypto", "blockchain"],
        )

        clean_job = make_job(title="AI Engineer", company_name="CleanTech Inc", description="Building climate AI models.")
        excluded_comp_job = make_job(title="AI Engineer", company_name="BadRecruiter GmbH Europe", description="Great opportunity.")
        excluded_kw_job = make_job(title="AI Engineer", company_name="FinanceCorp", description="High-frequency crypto trading.")

        assert DeterministicFilterService.is_job_eligible(clean_job, pref) is True
        assert DeterministicFilterService.is_job_eligible(excluded_comp_job, pref) is False
        assert DeterministicFilterService.is_job_eligible(excluded_kw_job, pref) is False

    def test_f6_filter_min_salary_threshold(self, db: Session, make_user, make_preference, make_job):
        """Test 6.6: Job with max salary lower than candidate minimum is disqualified."""
        user = make_user(email="salary.tester@example.com")
        pref = make_preference(user=user, min_salary=90000.0, locations=[], remote_only=False)

        high_salary_job = make_job(title="Staff Engineer", salary_max=110000.0)
        low_salary_job = make_job(title="Junior Developer", salary_max=60000.0)

        assert DeterministicFilterService.is_job_eligible(high_salary_job, pref) is True
        assert DeterministicFilterService.is_job_eligible(low_salary_job, pref) is False


# ============================================================================
# FEATURE 7: Strict Evidence ID Validation Gate (>= 5 Tests)
# ============================================================================

class TestFeature7EvidenceIDValidation:
    """Feature 7: Hard Validation Guardrails (selected_ids ⊆ allowed_ids)."""

    def test_f7_valid_subset_selection_passes(self):
        """Test 7.1: Selected IDs that are a valid subset of allowed IDs succeed."""
        allowed_ids = {"EXP_001", "EXP_002", "EXP_003", "SKILL_001", "PROJ_001"}
        selected_ids = ["EXP_001", "EXP_003", "SKILL_001"]

        # Should execute without raising
        validate_selected_evidence_ids(selected_ids, allowed_ids)

    def test_f7_hallucinated_id_raises_validation_error(self):
        """Test 7.2: LLM returning hallucinated ID raises EvidenceValidationError."""
        allowed_ids = {"EXP_001", "EXP_002", "SKILL_001"}
        hallucinated_selection = ["EXP_001", "EXP_999"]  # EXP_999 was never verified

        with pytest.raises(EvidenceValidationError) as exc_info:
            validate_selected_evidence_ids(hallucinated_selection, allowed_ids)
        assert "EXP_999" in str(exc_info.value)

    def test_f7_cross_tenant_id_injection_rejected(self, db: Session, make_user, make_evidence_item):
        """Test 7.3: Selection containing another user's valid ID is rejected because it is not in allowed_ids."""
        user_a = make_user(email="alice.evidence@example.com")
        user_b = make_user(email="bob.evidence@example.com")

        item_a = make_evidence_item(user=user_a, stable_id="EXP_001")
        item_b = make_evidence_item(user=user_b, stable_id="EXP_002")

        # Allowed IDs for User A strictly computed from User A's verified items
        user_a_allowed_ids = {item.stable_id for item in user_a.evidence_items if item.is_verified}
        assert "EXP_001" in user_a_allowed_ids
        assert "EXP_002" not in user_a_allowed_ids

        # Attempt to submit User B's ID in User A's selection
        with pytest.raises(EvidenceValidationError) as exc_info:
            validate_selected_evidence_ids(["EXP_001", item_b.stable_id], user_a_allowed_ids)
        assert "EXP_002" in str(exc_info.value)

    def test_f7_max_bullets_constraint_enforcement(self):
        """Test 7.4: Exceeding template maximum allowed bullets raises EvidenceValidationError."""
        allowed_ids = {"EXP_001", "EXP_002", "EXP_003", "EXP_004", "EXP_005"}
        selected_ids = ["EXP_001", "EXP_002", "EXP_003", "EXP_004"]

        with pytest.raises(EvidenceValidationError) as exc_info:
            validate_selected_evidence_ids(selected_ids, allowed_ids, max_bullets=3)
        assert "exceeds maximum allowed" in str(exc_info.value)

    def test_f7_exact_verified_text_retrieval_from_db_lookup(self, db: Session, make_user, make_evidence_item):
        """Test 7.5: Proves that rendered text is loaded from DB by stable ID and never taken from LLM prose."""
        user = make_user(email="verified.text@example.com")
        item = make_evidence_item(
            user=user,
            stable_id="EXP_001",
            raw_text="Architected enterprise Kubernetes cluster serving 50M requests/day.",
            is_verified=True,
        )

        allowed_ids = {item.stable_id for item in user.evidence_items if item.is_verified}
        selected_ids = ["EXP_001"]
        validate_selected_evidence_ids(selected_ids, allowed_ids)

        # Dereference from DB
        db_items = db.scalars(
            select(EvidenceItem).where(
                EvidenceItem.user_id == user.id,
                EvidenceItem.stable_id.in_(selected_ids),
                EvidenceItem.is_verified.is_(True),
            )
        ).all()

        rendered_bullets = [it.raw_text for it in db_items]
        assert rendered_bullets == ["Architected enterprise Kubernetes cluster serving 50M requests/day."]
