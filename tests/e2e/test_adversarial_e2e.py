"""Adversarial E2E Challenge Suite for Milestone 1 (M1).
Stress tests regex safety, word boundary tokenizer edge cases, multi-tenant isolation,
deduplication hash invariants, and evidence validation robustness.
"""

import re
import uuid
from decimal import Decimal
from typing import List, Set
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
from app.models.job import Company, JobSource, Job, JobSourceRecord
from tests.e2e.conftest import (
    EvidenceValidationError,
    validate_selected_evidence_ids,
    compute_content_hash,
    DeterministicFilterService,
    JOB_TYPE_MAPPING,
)


class TestAdversarialRegexAndTokenizer:
    """Stress-test regex patterns against dangerous regex syntax and programming language terms."""

    @pytest.mark.parametrize(
        "tech_symbol",
        [
            "C++",
            "C#",
            ".NET",
            ".NET Core",
            "Node.js",
            "Vue.js",
            "React.js",
            "PL/SQL",
            "Objective-C",
            "CI/CD",
            "TCP/IP",
            "R&D",
        ],
    )
    def test_special_programming_symbols_filter_matching(self, tech_symbol: str):
        """Ensure symbols with +, #, ., / are safely matched as exact terms without regex crashes."""
        pattern = DeterministicFilterService._make_word_pattern(tech_symbol)
        
        # Should match when present as distinct token
        positive_text = f"We require strong experience in {tech_symbol} for this role."
        assert re.search(pattern, positive_text.lower()) is not None

        # Should match when surrounded by punctuation or spaces
        positive_paren = f"Skills: ({tech_symbol}), Python, Docker"
        assert re.search(pattern, positive_paren.lower()) is not None

    def test_short_acronym_word_boundary_isolation(self):
        """Ensure short terms like 'IT', 'AI', 'Go', 'R' don't match substrings of larger words."""
        it_pattern = DeterministicFilterService._make_word_pattern("IT")
        
        # Should match 'IT' as standalone word
        assert re.search(it_pattern, "senior it manager") is not None
        assert re.search(it_pattern, "working in it department") is not None
        
        # Must NOT match substrings in 'with', 'submit', 'position', 'written'
        assert re.search(it_pattern, "candidate with 5 years experience") is None
        assert re.search(it_pattern, "please submit your resume") is None
        assert re.search(it_pattern, "position available immediately") is None
        assert re.search(it_pattern, "written communication skills") is None

        go_pattern = DeterministicFilterService._make_word_pattern("Go")
        assert re.search(go_pattern, "golang or go developer") is not None
        assert re.search(go_pattern, "going to lead the team") is None
        assert go_pattern is not None

    def test_catastrophic_backtracking_and_malicious_regex_keywords(self):
        """Ensure malicious user-supplied regex meta-characters don't cause ReDoS or syntax crashes."""
        adversarial_inputs = [
            "((((((((((a+)+)+)+)+)+)+)+)+)+)",
            ".*",
            "[a-z]+",
            "(?<=abc)def",
            "^$*",
            "\\b\\w+\\b",
            "[\\]\\^\\$\\*\\+\\?\\{\\}\\|\\(\\)]",
            "???++**",
        ]
        for term in adversarial_inputs:
            # Must safely construct pattern without re.error exception
            pattern = DeterministicFilterService._make_word_pattern(term)
            assert pattern is not None
            # Searching with constructed pattern must never crash or raise
            re.search(pattern, "standard job description with some words")


class TestAdversarialEvidenceValidation:
    """Stress-test strict evidence validation rules."""

    def test_empty_selection_passes(self):
        """Empty selected IDs is a valid no-op selection."""
        validate_selected_evidence_ids([], {"EXP_001", "EXP_002"})

    def test_whitespace_and_casing_strictness(self):
        """Evidence IDs must match strictly; whitespace or casing mismatch must be rejected."""
        allowed = {"EXP_001", "SKILL_001"}

        # Leading / trailing whitespace must be treated as invalid
        with pytest.raises(EvidenceValidationError):
            validate_selected_evidence_ids([" EXP_001 "], allowed)

        # Lowercase must be rejected
        with pytest.raises(EvidenceValidationError):
            validate_selected_evidence_ids(["exp_001"], allowed)

    def test_max_bullets_exact_boundary(self):
        """max_bullets enforcement at boundary conditions."""
        allowed = {"EXP_001", "EXP_002", "EXP_003", "EXP_004"}
        
        # Exactly at limit -> passes
        validate_selected_evidence_ids(["EXP_001", "EXP_002", "EXP_003"], allowed, max_bullets=3)

        # Exceeds limit by 1 -> raises
        with pytest.raises(EvidenceValidationError):
            validate_selected_evidence_ids(["EXP_001", "EXP_002", "EXP_003", "EXP_004"], allowed, max_bullets=3)


class TestAdversarialMultiTenantMassiveLoad:
    """Simulate high volume multi-tenant data insertion and query isolation."""

    def test_high_volume_multi_tenant_evidence_isolation(self, db: Session, make_user, make_evidence_item):
        """Create 10 users each with 10 evidence items sharing identical stable_ids (EXP_001 to EXP_010)."""
        users = [make_user(email=f"load_user_{i}@example.com") for i in range(10)]

        for user in users:
            for item_idx in range(1, 11):
                make_evidence_item(
                    user=user,
                    stable_id=f"EXP_{item_idx:03d}",
                    raw_text=f"User {user.email} metric #{item_idx}",
                    is_verified=True,
                )

        db.commit()

        # Verify that for each user, querying by (user_id, stable_id) returns ONLY that user's item
        for user in users:
            items = db.scalars(
                select(EvidenceItem).where(EvidenceItem.user_id == user.id)
            ).all()
            assert len(items) == 10
            for item in items:
                assert item.user_id == user.id
                assert user.email in item.raw_text
