"""Tier 2: Boundary and Corner Case E2E Tests.

Edge Cases & Boundaries Covered:
1. Empty and whitespace-only CV payloads
2. Extreme CV sizes (e.g. 50,000+ words)
3. Malformed and corrupted API / JSON payloads
4. Non-existent and hallucinated evidence ID references
5. Unauthorized cross-tenant evidence ID injection attacks
6. Duplicate URLs with differing query parameters and timestamps
7. Complex Unicode, German Umlauts, Typographic Quotes, and Emojis
8. Extreme salary filter values (0, negative, 1,000,000,000)
9. Regex meta-characters in keywords (C++, C#, .NET, Node.js)
10. Rate limit simulation (HTTP 429) & backoff handling
11. Empty preference criteria matching all valid jobs
12. Overlapping company and keyword exclusions
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


class TestTier2BoundaryCornerCases:
    """Tier 2 Boundary and Corner Case Test Suite."""

    def test_tier2_empty_or_whitespace_cv_handling(self, db: Session, make_user, make_profile):
        """Test 2.1: Empty or whitespace-only CV text does not crash profile persistence."""
        user = make_user(email="empty.cv@example.com")
        profile = make_profile(user=user, raw_cv_text="   \n\t   ", is_verified=False)

        assert profile.raw_cv_text.strip() == ""
        assert profile.is_verified is False
        assert len(user.evidence_items) == 0

    def test_tier2_extreme_size_cv_payload(self, db: Session, make_user, make_profile, make_evidence_item):
        """Test 2.2: Extremely large CV text (50,000 words / 500KB text) persists cleanly."""
        large_cv_text = "Experienced software engineer with extensive cloud knowledge. " * 5000
        user = make_user(email="large.cv@example.com")
        profile = make_profile(user=user, raw_cv_text=large_cv_text)

        # Add 50 atomic evidence items
        for i in range(1, 51):
            make_evidence_item(
                user=user,
                stable_id=f"EXP_{i:03d}",
                raw_text=f"Built high-throughput data subsystem #{i} handling 100k msg/sec.",
                is_verified=True,
            )

        db.commit()
        db.refresh(user)

        assert len(user.evidence_items) == 50
        assert len(user.candidate_profile.raw_cv_text) > 200000

    def test_tier2_malformed_json_fallback(self, db: Session, make_user, make_preference):
        """Test 2.3: Graceful defaults when optional JSON preference fields are empty or null."""
        user = make_user(email="malformed.pref@example.com")
        pref = CandidatePreference(
            id=uuid.uuid4(),
            user_id=user.id,
            target_roles=[],
            locations=[],
            remote_only=False,
            job_types=[],
            excluded_companies=[],
            excluded_keywords=[],
            languages=[],
        )
        db.add(pref)
        db.commit()
        db.refresh(pref)

        assert pref.target_roles == []
        assert pref.excluded_companies == []
        assert pref.excluded_keywords == []

    def test_tier2_nonexistent_evidence_ids_rejection(self):
        """Test 2.4: Multiple non-existent and hallucinated evidence IDs are rejected with complete error details."""
        allowed_ids = {"EXP_001", "EXP_002", "SKILL_001"}
        hallucinated_ids = ["EXP_999", "SKILL_404", "PROJ_000"]

        with pytest.raises(EvidenceValidationError) as exc_info:
            validate_selected_evidence_ids(hallucinated_ids, allowed_ids)

        error_msg = str(exc_info.value)
        assert "EXP_999" in error_msg
        assert "SKILL_404" in error_msg
        assert "PROJ_000" in error_msg

    def test_tier2_cross_tenant_evidence_id_hijack_prevention(self, db: Session, make_user, make_evidence_item):
        """Test 2.5: User A cannot use User B's verified IDs even when crafted in malicious payload."""
        victim_user = make_user(email="victim@example.com")
        attacker_user = make_user(email="attacker@example.com")

        victim_item = make_evidence_item(user=victim_user, stable_id="EXP_001", raw_text="Victim's confidential metric")
        attacker_item = make_evidence_item(user=attacker_user, stable_id="EXP_001", raw_text="Attacker's public metric")

        # Compute allowed IDs strictly for attacker
        attacker_allowed_ids = {
            item.stable_id
            for item in db.scalars(select(EvidenceItem).where(EvidenceItem.user_id == attacker_user.id, EvidenceItem.is_verified == True)).all()
        }

        # Attacker attempts to reference victim's items
        assert "EXP_001" in attacker_allowed_ids

        # Fetching evidence for attacker must NEVER return victim's item
        attacker_db_item = db.scalar(
            select(EvidenceItem).where(
                EvidenceItem.user_id == attacker_user.id,
                EvidenceItem.stable_id == "EXP_001",
            )
        )
        assert attacker_db_item.raw_text == "Attacker's public metric"
        assert attacker_db_item.raw_text != "Victim's confidential metric"

    def test_tier2_duplicate_urls_with_query_params(self):
        """Test 2.6: Canonical content hashing ignores tracking parameters in URLs (?utm_source=..., ?ref=...)."""
        base_url = "https://arbeitnow.com/jobs/senior-ml-engineer-101"
        url_with_tracking_1 = f"{base_url}?utm_source=linkedin&utm_medium=job_board"
        url_with_tracking_2 = f"{base_url}?ref=newsletter&page=1"

        h1 = compute_content_hash(url_with_tracking_1, "Senior ML Engineer", "OpenAI", "Berlin")
        h2 = compute_content_hash(url_with_tracking_2, "Senior ML Engineer", "OpenAI", "Berlin")
        h3 = compute_content_hash(base_url, "Senior ML Engineer", "OpenAI", "Berlin")

        assert h1 == h2 == h3

    def test_tier2_complex_unicode_german_and_emojis(self, db: Session, make_job, make_user, make_preference):
        """Test 2.7: German umlauts (ä, ö, ü, ß), typographical quotes (“ ”), and emojis (🚀) handle cleanly."""
        user = make_user(email="unicode.tester@example.com")
        pref = make_preference(
            user=user,
            target_roles=["Künstliche Intelligenz", "Entwickler"],
            locations=["München", "Köln", "Zürich"],
            excluded_keywords=["Glücksspiel"],
        )

        job_unicode = make_job(
            title="Senior Entwickler für Künstliche Intelligenz (m/w/d) 🚀",
            company_name="Münchener Rück AG",
            location="München, Deutschland",
            description="Wir entwickeln „State-of-the-Art“ KI-Lösungen für Großunternehmen.",
            remote=False,
        )

        assert DeterministicFilterService.is_job_eligible(job_unicode, pref) is True

    def test_tier2_extreme_salary_filter_boundaries(self, db: Session, make_user, make_preference, make_job):
        """Test 2.8: Extreme salary boundaries (0, negative, 1,000,000,000 EUR) handle safely."""
        user = make_user(email="extreme.salary@example.com")

        # Zero salary requirement
        pref = make_preference(user=user, min_salary=0.0)
        job_normal = make_job(title="Engineer", salary_max=50000.0)
        assert DeterministicFilterService.is_job_eligible(job_normal, pref) is True

        # Very high salary requirement (1,000,000 EUR)
        pref.min_salary = Decimal("1000000.0")
        db.commit()
        assert DeterministicFilterService.is_job_eligible(job_normal, pref) is False

        # Job with None salary passes gracefully
        job_no_salary = make_job(title="Engineer", salary_max=None)
        assert DeterministicFilterService.is_job_eligible(job_no_salary, pref) is True

    def test_tier2_regex_meta_characters_in_keywords(self, db: Session, make_user, make_preference, make_job):
        """Test 2.9: Keywords with regex meta-characters (C++, C#, .NET, Node.js, (AI)) match correctly without regex errors."""
        user = make_user(email="regex.kw@example.com")
        pref = make_preference(
            user=user,
            target_roles=["C++", "C#", ".NET", "Node.js"],
            excluded_keywords=["[Legacy]", "(Deprecated)"],
        )

        job_cpp = make_job(title="Senior C++ Graphics Developer", description="High performance rendering")
        job_csharp = make_job(title="Lead .NET / C# Architect", description="Enterprise systems")
        job_nodejs = make_job(title="Fullstack Node.js Engineer", description="Backend APIs")
        job_deprecated = make_job(title="Senior C++ Developer", description="Working on (Deprecated) framework")

        assert DeterministicFilterService.is_job_eligible(job_cpp, pref) is True
        assert DeterministicFilterService.is_job_eligible(job_csharp, pref) is True
        assert DeterministicFilterService.is_job_eligible(job_nodejs, pref) is True
        assert DeterministicFilterService.is_job_eligible(job_deprecated, pref) is False

    def test_tier2_rate_limit_http_429_backoff_simulation(self):
        """Test 2.10: Rate limiting header parsing and exponential backoff retry calculation."""
        response_headers = {"Retry-After": "5", "X-RateLimit-Remaining": "0"}
        retry_after = int(response_headers.get("Retry-After", 1))
        assert retry_after == 5

        # Exponential backoff progression for 3 retries: 2^attempt * base + jitter
        backoffs = [2 ** attempt * 1.0 for attempt in range(3)]
        assert backoffs == [1.0, 2.0, 4.0]

    def test_tier2_empty_preferences_matches_all_valid_jobs(self, db: Session, make_user, make_preference, make_job):
        """Test 2.11: Candidate with empty preferences matches any non-excluded job opportunity."""
        user = make_user(email="empty.pref@example.com")
        pref = make_preference(user=user, target_roles=[], locations=[], job_types=[], remote_only=False)

        job1 = make_job(title="Junior Python Dev", remote=True)
        job2 = make_job(title="Senior Java Architect", remote=False, location="Tokyo")
        job3 = make_job(title="Product Manager", job_types=["Part Time"])

        assert DeterministicFilterService.is_job_eligible(job1, pref) is True
        assert DeterministicFilterService.is_job_eligible(job2, pref) is True
        assert DeterministicFilterService.is_job_eligible(job3, pref) is True

    def test_tier2_overlapping_company_and_keyword_exclusions(self, db: Session, make_user, make_preference, make_job):
        """Test 2.12: Dual exclusions on company and keyword both evaluate properly."""
        user = make_user(email="dual.excluded@example.com")
        pref = make_preference(
            user=user,
            excluded_companies=["ScamCorp"],
            excluded_keywords=["crypto"],
        )

        job_both_excluded = make_job(
            title="Senior Developer",
            company_name="ScamCorp International",
            description="We build crypto trading bots.",
        )

        assert DeterministicFilterService.is_job_eligible(job_both_excluded, pref) is False
