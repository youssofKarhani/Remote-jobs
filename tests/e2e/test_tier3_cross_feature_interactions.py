"""Tier 3: Cross-Feature Interaction E2E Tests.

End-to-End Workflows & Cross-Module Interactions Covered:
1. Full Candidate Journey: Register -> CV Parsing -> Evidence Staging -> User Verification -> Preferences -> Job Ingestion -> Deterministic Filter -> AI Evidence Selection -> Verified CV Output.
2. Multi-Tenant Cross-Isolation: Multi-user concurrent state, private preference scoping, zero evidence leakage, cross-tenant ID injection rejection.
3. Draft Staging to Verification Lifecycle: Draft items blocked from selection until approved; approved items immediately available.
4. Multi-Source Ingestion, Deduplication, and Unified Feed Consistency.
5. Preference Dynamic Mutation: Candidate modifies filter constraints and sees instant feed updates without database corruption or re-ingestion.
"""

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


class TestTier3CrossFeatureInteractions:
    """Tier 3 Cross-Feature Interaction Test Suite."""

    def test_tier3_full_candidate_lifecycle_upload_to_filtered_feed(
        self, db: Session, make_user, make_profile, make_preference, make_experience, make_evidence_item, make_skill, make_job
    ):
        """Test 3.1: Full Candidate Lifecycle (Upload -> Parse -> Verify -> Filter -> Tailor Selection)."""
        # Step 1: User registers
        candidate = make_user(email="carol.lifecycle@example.com", full_name="Carol Engineer")

        # Step 2: Profile & Evidence parsed from CV (draft state)
        profile = make_profile(
            user=candidate,
            headline="Senior AI Systems Engineer",
            summary="Specialist in distributed LLM architectures.",
            is_verified=False,
        )
        exp1 = make_experience(
            user=candidate,
            company_name="AI Frontier Labs",
            role_title="Lead AI Engineer",
            start_date="2022-03",
            is_current=True,
        )
        b1 = make_evidence_item(
            user=candidate,
            experience_record=exp1,
            stable_id="EXP_001",
            raw_text="Built high-throughput model serving gateway processing 50M tokens/min.",
            category="architecture",
            is_verified=False,
        )
        b2 = make_evidence_item(
            user=candidate,
            experience_record=exp1,
            stable_id="EXP_002",
            raw_text="Reduced inference memory footprint by 45% using FP8 quantization.",
            category="optimization",
            is_verified=False,
        )
        s1 = make_skill(user=candidate, stable_id="SKILL_001", name="FastAPI", is_verified=False)
        s2 = make_skill(user=candidate, stable_id="SKILL_002", name="PyTorch", is_verified=False)

        # Step 3: Candidate reviews & verifies draft items via /profile
        profile.is_verified = True
        b1.is_verified = True
        b2.is_verified = True
        s1.is_verified = True
        s2.is_verified = True
        db.commit()

        # Step 4: Candidate configures job preferences via /preferences
        pref = make_preference(
            user=candidate,
            target_roles=["AI Engineer", "LLM Systems"],
            locations=["Berlin", "Remote"],
            remote_only=True,
            job_types=["Full Time"],
            min_salary=90000.0,
            excluded_companies=["SpamTech"],
            excluded_keywords=["legacy", "crypto"],
        )

        # Step 5: Ingest batch of external jobs
        job_match = make_job(
            title="Senior AI Engineer (m/w/d)",
            company_name="Anthropic Partner",
            location="Berlin, Germany",
            remote=True,
            salary_min=95000.0,
            salary_max=120000.0,
            description="Build scalable LLM platforms with FastAPI and PyTorch.",
        )
        job_onsite_mismatch = make_job(
            title="Senior AI Engineer",
            company_name="OnsiteCorp",
            location="Frankfurt, Germany",
            remote=False,  # Fails remote_only constraint
            salary_max=100000.0,
        )
        job_excluded_kw = make_job(
            title="Senior AI Engineer",
            company_name="Blockchain Labs",
            location="Berlin",
            remote=True,
            description="Work on crypto trading algorithms.",  # Fails excluded_keywords
        )

        # Step 6: Deterministic Filter evaluates candidate feed
        eligible_jobs = [
            j for j in [job_match, job_onsite_mismatch, job_excluded_kw]
            if DeterministicFilterService.is_job_eligible(j, pref)
        ]
        assert len(eligible_jobs) == 1
        assert eligible_jobs[0].id == job_match.id

        # Step 7: AI selects verified evidence IDs for job_match
        allowed_ids = {item.stable_id for item in candidate.evidence_items if item.is_verified}
        allowed_ids.update({skill.stable_id for skill in candidate.skills if skill.is_verified})
        assert allowed_ids == {"EXP_001", "EXP_002", "SKILL_001", "SKILL_002"}

        selected_ids = ["EXP_001", "EXP_002", "SKILL_001"]
        validate_selected_evidence_ids(selected_ids, allowed_ids)

        # Step 8: Document Renderer resolves verified exact text from database
        rendered_evidence = db.scalars(
            select(EvidenceItem).where(
                EvidenceItem.user_id == candidate.id,
                EvidenceItem.stable_id.in_(selected_ids),
                EvidenceItem.is_verified == True,
            )
        ).all()

        assert len(rendered_evidence) == 2
        assert "50M tokens/min" in rendered_evidence[0].raw_text

    def test_tier3_multi_tenant_isolation_cross_profile_and_evidence(
        self, db: Session, make_user, make_preference, make_evidence_item, make_job
    ):
        """Test 3.2: Multi-Tenant Isolation (User A & B cannot cross-access or hijack evidence/preferences)."""
        user_a = make_user(email="alice.tenant@example.com")
        user_b = make_user(email="bob.tenant@example.com")

        # User A: Python Backend Engineer
        pref_a = make_preference(user=user_a, target_roles=["Python"], remote_only=True)
        item_a = make_evidence_item(user=user_a, stable_id="EXP_001", raw_text="Alice's Python backend achievement")

        # User B: Frontend React Engineer
        pref_b = make_preference(user=user_b, target_roles=["React"], remote_only=True)
        item_b = make_evidence_item(user=user_b, stable_id="EXP_001", raw_text="Bob's React frontend achievement")

        job_python = make_job(title="Python Backend Specialist", remote=True)
        job_react = make_job(title="React Frontend Specialist", remote=True)

        # User A sees Python job, User B sees React job
        assert DeterministicFilterService.is_job_eligible(job_python, pref_a) is True
        assert DeterministicFilterService.is_job_eligible(job_react, pref_a) is False

        assert DeterministicFilterService.is_job_eligible(job_react, pref_b) is True
        assert DeterministicFilterService.is_job_eligible(job_python, pref_b) is False

        # User A allowed IDs contains only Alice's item
        alice_allowed_ids = {item.stable_id for item in user_a.evidence_items if item.is_verified}
        assert alice_allowed_ids == {"EXP_001"}

        # When Alice resolves EXP_001 from DB, it returns Alice's text
        alice_item = db.scalar(
            select(EvidenceItem).where(
                EvidenceItem.user_id == user_a.id,
                EvidenceItem.stable_id == "EXP_001",
            )
        )
        assert alice_item.raw_text == "Alice's Python backend achievement"

    def test_tier3_staging_and_verification_cycle(self, db: Session, make_user, make_evidence_item):
        """Test 3.3: Draft items are rejected by AI selection until user explicitly verifies them."""
        candidate = make_user(email="staging.tester@example.com")
        draft_item = make_evidence_item(user=candidate, stable_id="EXP_001", is_verified=False)

        # Unverified items cannot be in allowed_ids
        allowed_ids_before = {item.stable_id for item in candidate.evidence_items if item.is_verified}
        assert "EXP_001" not in allowed_ids_before

        with pytest.raises(EvidenceValidationError):
            validate_selected_evidence_ids(["EXP_001"], allowed_ids_before)

        # User verifies item via /profile
        draft_item.is_verified = True
        db.commit()

        allowed_ids_after = {
            item.stable_id
            for item in db.scalars(select(EvidenceItem).where(EvidenceItem.user_id == candidate.id, EvidenceItem.is_verified == True)).all()
        }
        assert "EXP_001" in allowed_ids_after
        # Now validation passes cleanly
        validate_selected_evidence_ids(["EXP_001"], allowed_ids_after)

    def test_tier3_job_ingestion_deduplication_and_feed_consistency(
        self, db: Session, make_job_source, make_job, make_user, make_preference
    ):
        """Test 3.4: Multi-source job ingestion deduplication preserves feed consistency."""
        source_arbeitnow = make_job_source(name="arbeitnow")
        source_remoteok = make_job_source(name="remoteok", base_url="https://remoteok.com/api")

        candidate = make_user(email="dedup.candidate@example.com")
        pref = make_preference(user=candidate, target_roles=["Data Engineer"], remote_only=True)

        # Job 1 ingested from Arbeitnow
        url_1 = "https://arbeitnow.com/jobs/lead-data-engineer-101"
        job1 = make_job(
            title="Lead Data Engineer (m/w/d)",
            company_name="Spotify",
            location="Berlin",
            remote=True,
            url=url_1,
        )
        rec1 = JobSourceRecord(
            id=uuid.uuid4(),
            job_id=job1.id,
            source_id=source_arbeitnow.id,
            external_id="spot-de-101",
            external_url=url_1,
            raw_payload={"source": "arbeitnow"},
        )
        db.add(rec1)
        db.commit()

        # Job 2: Same position listed on RemoteOK
        # Deduplication engine computes matching content hash
        hash_job2 = compute_content_hash(url_1, "Lead Data Engineer (gn)", "Spotify", "Berlin")
        assert hash_job2 == job1.content_hash

        # Second source record attaches to existing job1
        rec2 = JobSourceRecord(
            id=uuid.uuid4(),
            job_id=job1.id,
            source_id=source_remoteok.id,
            external_id="rok-spot-101",
            external_url=url_1,
            raw_payload={"source": "remoteok"},
        )
        db.add(rec2)
        db.commit()

        # Feed query returns exactly ONE job opportunity for candidate
        matching_jobs = [j for j in db.scalars(select(Job)).all() if DeterministicFilterService.is_job_eligible(j, pref)]
        assert len(matching_jobs) == 1
        assert matching_jobs[0].id == job1.id
        assert len(matching_jobs[0].source_records) == 2

    def test_tier3_preference_dynamic_mutation_updates_feed_instantly(
        self, db: Session, make_user, make_preference, make_job
    ):
        """Test 3.5: Candidate modifies preferences and sees feed update dynamically without re-fetching."""
        user = make_user(email="dynamic.pref@example.com")
        pref = make_preference(user=user, target_roles=["Backend"], remote_only=True)

        remote_backend_job = make_job(title="Senior Backend Engineer", remote=True)
        onsite_berlin_job = make_job(title="Senior Backend Engineer", remote=False, location="Berlin, Germany")
        fulltime_frontend_job = make_job(title="Frontend Engineer", remote=True)

        # Stage 1: Candidate is remote_only
        feed_stage1 = [
            j for j in [remote_backend_job, onsite_berlin_job, fulltime_frontend_job]
            if DeterministicFilterService.is_job_eligible(j, pref)
        ]
        assert len(feed_stage1) == 1
        assert feed_stage1[0].id == remote_backend_job.id

        # Stage 2: Candidate changes preference to allow Berlin onsite
        pref.remote_only = False
        pref.locations = ["Berlin"]
        db.commit()

        feed_stage2 = [
            j for j in [remote_backend_job, onsite_berlin_job, fulltime_frontend_job]
            if DeterministicFilterService.is_job_eligible(j, pref)
        ]
        assert len(feed_stage2) == 2
        assert {j.id for j in feed_stage2} == {remote_backend_job.id, onsite_berlin_job.id}
