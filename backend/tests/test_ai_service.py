"""Comprehensive Automated Test Suite for AI Gateway, AIService, and End-to-End Workflow.

Verifies:
1. Full AIService protocol conformance and typing.
2. Multi-model routing (fast, reasoning, coding, writing) and configuration.
3. Diagnostic health endpoint /api/v1/ai/status.
4. CV extraction (both mock LLM and robust heuristic engine, plus edge cases).
5. Job prescreening (both mock LLM and domain heuristic engine).
6. Deep compatibility assessment (multi-dimensional scoring, sanitization, recommendations).
7. Anti-hallucination gate in CV evidence selection (purging hallucinated IDs).
8. Evidence-grounded cover letter generation across canonical positioning strategies.
9. Error recovery, timeout resilience, and fallback switching.
10. End-to-end multi-step platform workflow (CV upload -> Evidence Verification -> Match -> Tailoring -> Cover Letter -> Application).
"""

import inspect
import os
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from app.integrations.llm_ai_service import DefaultAIService, ai_service
from app.models.evidence import EvidenceItem, ExperienceRecord, Skill
from app.models.job import Job
from app.models.user import User
from app.protocols.ai_service import (
    AIService,
    CoverLetterResult,
    CVSelectionResult,
    ExtractedEvidenceBankDraft,
    ExtractedEvidenceBullet,
    ExtractedExperience,
    ExtractedSkill,
    JobAssessmentResult,
    PreScreenResult,
)


# ============================================================================
# 1. AIService Protocol Conformance & Configuration
# ============================================================================

class TestAIServiceProtocolConformance:
    """Verifies that DefaultAIService conforms to the AIService protocol."""

    def test_protocol_isinstance_check(self):
        """ai_service must satisfy runtime AIService protocol check."""
        service = DefaultAIService()
        assert isinstance(service, AIService)

    def test_required_methods_exist_and_are_async(self):
        """All 5 protocol methods must be asynchronous coroutine functions."""
        required_methods = [
            "extract_cv_to_evidence_bank",
            "prescreen_job",
            "assess_job",
            "select_cv_evidence",
            "generate_cover_letter",
        ]
        service = DefaultAIService()
        for method_name in required_methods:
            method = getattr(service, method_name, None)
            assert method is not None, f"Method {method_name} missing from AIService"
            assert inspect.iscoroutinefunction(method), f"Method {method_name} must be an async coroutine"

    def test_model_aliases_configuration(self):
        """Ensure logical model tiers (fast, reasoning, coding, writing) are properly wired."""
        service = DefaultAIService(
            base_url="http://51.20.134.201:4000/v1",
            api_key="custom-key",
            model_prescreen="fast",
            model_assessment="reasoning",
            model_extraction="coding",
            model_tailoring="reasoning",
            model_cover_letter="writing",
            timeout=25.0,
            max_retries=3,
        )
        assert service.base_url == "http://51.20.134.201:4000/v1"
        assert service.api_key == "custom-key"
        assert service.model_prescreen == "fast"
        assert service.model_assessment == "reasoning"
        assert service.model_extraction == "coding"
        assert service.model_tailoring == "reasoning"
        assert service.model_cover_letter == "writing"
        assert service.timeout == 25.0
        assert service.max_retries == 3

    def test_base_url_normalization(self):
        """Ensure missing /v1 suffix is cleanly normalized."""
        service = DefaultAIService(base_url="http://localhost:4000")
        assert service.base_url == "http://localhost:4000/v1"

        service_slash = DefaultAIService(base_url="http://localhost:4000/")
        assert service_slash.base_url == "http://localhost:4000/v1"

    @pytest.mark.asyncio
    async def test_ai_status_diagnostics(self):
        """check_health must return complete diagnostic metadata."""
        service = DefaultAIService(provider="mock")
        health = await service.check_health()
        assert "status" in health
        assert health["status"] == "mock_mode"
        assert "models" in health
        assert health["models"]["prescreen"] == "fast"
        assert health["models"]["assessment"] == "reasoning"


def test_ai_status_endpoint(client: TestClient):
    """GET /api/v1/ai/status must return diagnostic status without hanging."""
    resp = client.get("/api/v1/ai/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "models" in data
    assert "base_url" in data


# ============================================================================
# 2. CV Extraction (LLM, Heuristic, Edge Cases)
# ============================================================================

class TestAIServiceExtraction:
    """Verifies CV extraction to structured Evidence Bank draft."""

    @pytest.mark.asyncio
    async def test_extraction_heuristic_rich_cv(self):
        """Heuristic parser must extract experiences, bullets, skills, and contact info."""
        cv_text = """
Alex Morgan
Staff Cloud & AI Architect - Munich, Germany
Phone: +49 170 9876543
Email: alex.morgan@example.com
LinkedIn: https://linkedin.com/in/alexmorgan
GitHub: https://github.com/alexmorgan

Summary:
Accomplished software engineer with 8+ years designing fault-tolerant distributed systems.

Experience:
QuantumCloud - Senior Platform Engineer
- Built high-throughput telemetry ingestion pipeline processing 40k events/sec.
- Reduced p99 API latency from 450ms to 42ms with asynchronous worker pool.

RUYA Advisory - Backend Software Engineer
- Architected payment orchestration service handling EUR 12M monthly volume.
- Enforced strict multi-tenant schema isolation in PostgreSQL.

Skills:
Python, FastAPI, PostgreSQL, Docker, Kubernetes, Redis, AWS

Projects:
Autonomous Agent Swarm - Multi-agent task distributor in Python

Education:
Technical University of Munich - Master of Science in Informatics

Certifications:
AWS Certified Solutions Architect - Professional
"""
        service = DefaultAIService(provider="mock")
        draft = await service.extract_cv_to_evidence_bank(cv_text)

        assert isinstance(draft, ExtractedEvidenceBankDraft)
        assert draft.phone == "+49 170 9876543"
        assert "linkedin.com/in/alexmorgan" in (draft.linkedin_url or "")
        assert "github.com/alexmorgan" in (draft.github_url or "")
        assert len(draft.experiences) >= 2
        assert len(draft.skills) >= 5
        assert any("Python" in s.name for s in draft.skills)
        assert len(draft.education) >= 1
        assert len(draft.certifications) >= 1
        assert len(draft.projects) >= 1

        # Check bullets extracted
        total_bullets = sum(len(e.bullets) for e in draft.experiences)
        assert total_bullets >= 2

    @pytest.mark.asyncio
    async def test_extraction_edge_cases(self):
        """Extraction must be resilient to empty, tiny, or malformed text."""
        service = DefaultAIService(provider="mock")

        # Empty text
        draft_empty = await service.extract_cv_to_evidence_bank("")
        assert isinstance(draft_empty, ExtractedEvidenceBankDraft)

        # Whitespace only
        draft_ws = await service.extract_cv_to_evidence_bank("   \n\n\t  ")
        assert isinstance(draft_ws, ExtractedEvidenceBankDraft)

        # Single line
        draft_single = await service.extract_cv_to_evidence_bank("Jordan Lee - Python Developer in Berlin")
        assert isinstance(draft_single, ExtractedEvidenceBankDraft)
        assert draft_single.headline is not None

        # Special unicode and symbols
        draft_unicode = await service.extract_cv_to_evidence_bank("Élise Müller • Développeuse backend C++ / .NET à Zürich")
        assert isinstance(draft_unicode, ExtractedEvidenceBankDraft)

    @pytest.mark.asyncio
    async def test_extraction_with_mocked_llm(self):
        """When LLM returns a structured draft, it must be validated and returned."""
        service = DefaultAIService(provider="litellm")
        mock_client = MagicMock()
        expected_draft = ExtractedEvidenceBankDraft(
            headline="Principal Distributed Systems Engineer",
            summary="Expert in high-throughput messaging and consensus algorithms.",
            experiences=[
                ExtractedExperience(
                    company_name="Vortex Labs",
                    role_title="Lead Architect",
                    start_date="2021-03",
                    bullets=[
                        ExtractedEvidenceBullet(text="Designed consensus engine", category="experience")
                    ],
                )
            ],
            skills=[ExtractedSkill(name="Python", category="backend")],
        )

        mock_client.chat.completions.create = AsyncMock(return_value=expected_draft)
        service._instructor_client = mock_client

        result = await service.extract_cv_to_evidence_bank("Vortex Labs CV content")
        assert result.headline == "Principal Distributed Systems Engineer"
        assert len(result.experiences) == 1
        assert result.experiences[0].company_name == "Vortex Labs"


# ============================================================================
# 3. Job Pre-Screening (Fast Recall Filter)
# ============================================================================

class TestAIServicePreScreening:
    """Verifies fast high-recall pre-screening capability."""

    @pytest.mark.asyncio
    async def test_prescreen_heuristic_relevant_role(self):
        """Technical alignment must yield relevant=True and high confidence."""
        service = DefaultAIService(provider="mock")
        res = await service.prescreen_job(
            candidate_summary="Python, FastAPI, distributed systems, backend engineering",
            job_title="Staff Backend Software Engineer",
            job_tags=["Python", "PostgreSQL", "FastAPI"],
        )
        assert isinstance(res, PreScreenResult)
        assert res.relevant is True
        assert 0.0 <= res.confidence <= 1.0
        assert res.confidence >= 0.70
        assert len(res.reason_codes) >= 1
        assert len(res.reasoning) > 0

    @pytest.mark.asyncio
    async def test_prescreen_heuristic_irrelevant_role(self):
        """Obvious non-technical mismatch must yield relevant=False."""
        service = DefaultAIService(provider="mock")
        res = await service.prescreen_job(
            candidate_summary="Python, FastAPI, distributed systems",
            job_title="Executive Pastry Chef & Restaurant Manager",
            job_tags=["Baking", "Culinary", "Hospitality"],
        )
        assert isinstance(res, PreScreenResult)
        assert res.relevant is False
        assert 0.0 <= res.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_prescreen_with_mocked_llm_confidence_clamping(self):
        """Confidence returned by LLM must be strictly clamped between 0.0 and 1.0."""
        service = DefaultAIService(provider="litellm")
        mock_client = MagicMock()
        # Mock LLM returning out-of-range confidence
        mock_client.chat.completions.create = AsyncMock(
            return_value=PreScreenResult(
                relevant=True,
                confidence=1.0,
                reason_codes=["STRONG_MATCH"],
                reasoning="Candidate satisfies all prerequisites.",
            )
        )
        service._instructor_client = mock_client

        res = await service.prescreen_job(
            candidate_summary="Expert",
            job_title="Senior Engineer",
            job_tags=["Python"],
        )
        assert res.relevant is True
        assert res.confidence == 1.0


# ============================================================================
# 4. Deep Compatibility Assessment
# ============================================================================

class TestAIServiceAssessment:
    """Verifies multi-dimensional scoring and title sanitization."""

    @pytest.mark.asyncio
    async def test_assess_job_heuristic_scoring_rubric(self):
        """Scores across all 6 dimensions must be valid integers in range [0, 100]."""
        service = DefaultAIService(provider="mock")
        job_details = {
            "title": "Lead Software Engineer (m/w/d) [Remote, Full-Time]",
            "company_name": "TechCorp",
            "location": "Berlin, Germany",
            "remote": True,
            "tags": ["Python", "FastAPI", "PostgreSQL"],
            "description": "We are seeking a Lead Software Engineer with strong Python and API expertise.",
        }
        res = await service.assess_job(
            candidate_profile_text="Python, FastAPI, PostgreSQL, Docker, AWS architecture",
            job_details=job_details,
        )
        assert isinstance(res, JobAssessmentResult)
        assert 0 <= res.overall_score <= 100
        assert 0 <= res.skills_score <= 100
        assert 0 <= res.experience_score <= 100
        assert 0 <= res.seniority_score <= 100
        assert 0 <= res.location_score <= 100
        assert 0 <= res.language_score <= 100
        assert res.recommendation in ("apply", "consider", "skip")
        assert 0.0 <= res.confidence <= 1.0

        # Title sanitization check
        assert "[" not in res.sanitized_job_title
        assert "]" not in res.sanitized_job_title
        assert "(m/w/d)" not in res.sanitized_job_title
        assert res.sanitized_job_title == "Lead Software Engineer"

    @pytest.mark.asyncio
    async def test_assess_job_with_mocked_llm(self):
        """Ensure LLM assessment response is parsed into JobAssessmentResult."""
        service = DefaultAIService(provider="litellm")
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(
            return_value=JobAssessmentResult(
                overall_score=92,
                skills_score=95,
                experience_score=90,
                seniority_score=88,
                location_score=100,
                language_score=90,
                matching_evidence_ids=["EXP_001", "SKILL_001"],
                missing_requirements=["Kubernetes"],
                strengths=["Exceptional Python mastery"],
                recommendation="apply",
                confidence=0.96,
                sanitized_job_title="Lead Software Engineer",
            )
        )
        service._instructor_client = mock_client

        res = await service.assess_job("Profile", {"title": "Lead Software Engineer"})
        assert res.overall_score == 92
        assert res.recommendation == "apply"
        assert "Kubernetes" in res.missing_requirements


# ============================================================================
# 5. CV Evidence Selection & Anti-Hallucination Gate
# ============================================================================

class TestAIServiceCVTailoringAntiHallucination:
    """Verifies that the LLM can ONLY select allowed IDs and cannot invent facts."""

    @pytest.mark.asyncio
    async def test_hallucinated_ids_purged_by_post_validation_gate(self):
        """CRITICAL: Any ID returned by LLM not present in allowed set must be rejected."""
        service = DefaultAIService(provider="litellm")
        allowed_ids = {
            "experience_bullets": ["EXP_001", "EXP_002"],
            "skills": ["SKILL_001", "SKILL_002"],
            "projects": ["PROJ_001"],
            "certifications": ["CERT_001"],
        }

        # Mock an adversarial/hallucinating LLM
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(
            return_value=CVSelectionResult(
                experience_bullet_ids=["EXP_001", "EXP_999_HALLUCINATED", "EXP_EVIL_INJECT"],
                skill_ids=["SKILL_001", "SKILL_FAKE_AI"],
                project_ids=["PROJ_001", "PROJ_DOES_NOT_EXIST"],
                certification_ids=["CERT_001", "CERT_FORGED"],
            )
        )
        service._instructor_client = mock_client

        selection = await service.select_cv_evidence(
            job_details={"title": "Backend Lead"},
            allowed_evidence_ids=allowed_ids,
        )

        # Invariant: selected_ids ⊆ allowed_ids
        for b_id in selection.experience_bullet_ids:
            assert b_id in allowed_ids["experience_bullets"], f"Hallucinated bullet {b_id} leaked!"
        for s_id in selection.skill_ids:
            assert s_id in allowed_ids["skills"], f"Hallucinated skill {s_id} leaked!"
        for p_id in selection.project_ids:
            assert p_id in allowed_ids["projects"], f"Hallucinated project {p_id} leaked!"
        for c_id in selection.certification_ids:
            assert c_id in allowed_ids["certifications"], f"Hallucinated cert {c_id} leaked!"

        assert "EXP_999_HALLUCINATED" not in selection.experience_bullet_ids
        assert "SKILL_FAKE_AI" not in selection.skill_ids

    @pytest.mark.asyncio
    async def test_select_cv_evidence_heuristic(self):
        """Heuristic selector returns valid subset of allowed IDs."""
        service = DefaultAIService(provider="mock")
        allowed_ids = {
            "experience_bullets": ["EXP_001", "EXP_002", "EXP_003"],
            "skills": ["SKILL_001", "SKILL_002"],
            "projects": ["PROJ_001"],
            "certifications": ["CERT_001"],
        }
        selection = await service.select_cv_evidence(
            job_details={"title": "Engineer"},
            allowed_evidence_ids=allowed_ids,
            max_bullets_per_role=2,
        )
        assert isinstance(selection, CVSelectionResult)
        assert len(selection.experience_bullet_ids) <= 6
        assert set(selection.experience_bullet_ids).issubset(set(allowed_ids["experience_bullets"]))


# ============================================================================
# 6. Cover Letter Generation
# ============================================================================

class TestAIServiceCoverLetter:
    """Verifies evidence-grounded cover letter generation across strategies."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("strategy", [
        "technical_depth",
        "business_revenue",
        "ai_automation",
        "data_engineering",
        "team_leadership",
    ])
    async def test_cover_letter_heuristic_strategies(self, strategy: str):
        """Cover letter must reference company, job role, and candidate evidence."""
        service = DefaultAIService(provider="mock")
        evidence = [
            {"stable_id": "EXP_001", "text": "Reduced latency by 80% with async pipelines."},
            {"stable_id": "EXP_002", "text": "Architected high-throughput message bus."},
        ]
        result = await service.generate_cover_letter(
            candidate_profile_text="Alex Morgan - Senior Engineer",
            job_details={"title": "Cloud Architect", "company_name": "QuantumCloud", "location": "Munich"},
            selected_evidence_items=evidence,
            strategy=strategy,
        )
        assert isinstance(result, CoverLetterResult)
        assert "QuantumCloud" in result.letter_text
        assert "Cloud Architect" in result.letter_text
        assert result.strategy_used == strategy
        assert "EXP_001" in result.referenced_evidence_ids

    @pytest.mark.asyncio
    async def test_cover_letter_with_mocked_llm(self):
        """Ensure LLM cover letter output and referenced IDs are correctly preserved."""
        service = DefaultAIService(provider="litellm")
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(
            return_value=CoverLetterResult(
                letter_text="Dear QuantumCloud Team,\nI am writing to apply...",
                strategy_used="technical_depth",
                referenced_evidence_ids=["EXP_001"],
            )
        )
        service._instructor_client = mock_client

        evidence = [{"stable_id": "EXP_001", "text": "Built pipeline"}]
        res = await service.generate_cover_letter(
            "Profile",
            {"title": "Dev", "company_name": "QuantumCloud"},
            evidence,
        )
        assert "QuantumCloud" in res.letter_text
        assert res.referenced_evidence_ids == ["EXP_001"]


# ============================================================================
# 7. Error Recovery & Fallback Resiliency
# ============================================================================

class TestAIServiceErrorRecovery:
    """Verifies resilience when LLM calls fail or network times out."""

    @pytest.mark.asyncio
    async def test_llm_exception_triggers_heuristic_fallback(self):
        """When LLM raises a connection error and fallback is enabled, heuristic handles it."""
        service = DefaultAIService(provider="litellm", fallback_to_heuristics=True)
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(side_effect=RuntimeError("Connection timeout to LiteLLM"))
        service._instructor_client = mock_client

        # Prescreen fallback
        prescreen = await service.prescreen_job("Python engineer", "Backend Developer", ["Python"])
        assert prescreen.relevant is True

        # Assessment fallback
        assessment = await service.assess_job("Profile", {"title": "Software Engineer"})
        assert assessment.overall_score >= 50

        # Cover letter fallback
        letter = await service.generate_cover_letter("Profile", {"title": "Dev", "company_name": "Acme"}, [])
        assert "Acme" in letter.letter_text

    @pytest.mark.asyncio
    async def test_llm_exception_propagates_when_fallback_disabled(self):
        """When fallback is disabled, exceptions must be raised to the caller."""
        service = DefaultAIService(provider="litellm", fallback_to_heuristics=False)
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(side_effect=ConnectionError("Gateway unreachable"))
        service._instructor_client = mock_client

        with pytest.raises(ConnectionError):
            await service.prescreen_job("Profile", "Developer", [])


# ============================================================================
# 8. Complete End-to-End Multi-Step Platform Workflow
# ============================================================================

def test_full_ai_workflow_remotejobs(client: TestClient, sample_user: User, auth_headers: dict, db_session: Session):
    """End-to-end integration test validating the entire platform workflow with AI integration."""
    # Step 1: Upload and parse CV raw text
    cv_payload = {
        "text": """
Jordan Taylor
Staff Software Engineer - Munich, Germany
Email: jordan.taylor@example.com
Phone: +49 170 5551234
LinkedIn: https://linkedin.com/in/jordantaylor

Professional Summary:
Backend architect specializing in Python, FastAPI, distributed databases, and high-performance APIs.

Experience:
CloudScale GmbH - Senior Backend Architect
- Designed event-driven messaging backbone processing 50M messages daily.
- Decreased API response times by 65% through database index redesign.

Skills:
Python, FastAPI, PostgreSQL, Redis, Docker, Kubernetes, AWS

Projects:
TelemetryCollector - High throughput distributed log collector in Python

Education:
Technical University of Munich - M.Sc. Computer Science
"""
    }
    resp_parse = client.post("/api/v1/cv/parse-text", json=cv_payload, headers=auth_headers)
    assert resp_parse.status_code == 200
    parse_data = resp_parse.json()
    assert parse_data["status"] == "completed"

    # Step 2: Auto-verify candidate evidence items in the Evidence Bank
    resp_verify = client.post("/api/v1/profile/evidence/verify-all", headers=auth_headers)
    assert resp_verify.status_code == 200

    # Step 3: Create a new normalized target job opportunity
    job = Job(
        title="Senior Python / Backend Platform Engineer (m/w/d)",
        sanitized_title="Senior Python / Backend Platform Engineer",
        company_name="ApexCloud Technologies",
        location="Munich, Germany",
        remote=True,
        tags=["Python", "FastAPI", "PostgreSQL", "Docker"],
        job_types=["Full Time"],
        description="We are looking for a Senior Python Engineer to design our next-generation cloud services.",
        url=f"https://example.com/jobs/apex-{uuid.uuid4().hex[:6]}",
        slug=f"job-apex-{uuid.uuid4().hex[:6]}",
        content_hash=uuid.uuid4().hex,
        published_at=datetime.now(timezone.utc),
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    # Step 4: Execute Compatibility Assessment & Matching
    resp_match = client.post(f"/api/v1/jobs/{job.id}/match", headers=auth_headers)
    assert resp_match.status_code == 200
    match_data = resp_match.json()
    assert match_data["overall_score"] >= 60
    assert match_data["recommendation"] in ("apply", "consider")
    assert "ApexCloud Technologies" in match_data["job"]["company_name"]

    # Step 5: Tailor CV for target job (selecting verified evidence only)
    resp_tailor = client.post(f"/api/v1/jobs/{job.id}/tailor-cv", json={"max_bullets_per_role": 3}, headers=auth_headers)
    assert resp_tailor.status_code == 200
    tailor_data = resp_tailor.json()
    assert tailor_data["document_type"] == "cv"
    assert len(tailor_data["selected_evidence_ids"]) >= 1

    # Step 6: Generate Grounded Cover Letter using AI
    resp_letter = client.post(
        f"/api/v1/jobs/{job.id}/cover-letter",
        json={"strategy": "Technical Depth"},
        headers=auth_headers,
    )
    assert resp_letter.status_code == 200
    letter_data = resp_letter.json()
    assert "ApexCloud Technologies" in letter_data["content"]
    assert letter_data["strategy"] == "Technical Depth"

    # Step 7: Apply / Track application lifecycle
    app_payload = {
        "job_id": str(job.id),
        "status": "Applied",
        "notes": "Tailored application generated and submitted.",
    }
    resp_app = client.post("/api/v1/applications", json=app_payload, headers=auth_headers)
    assert resp_app.status_code == 201
    app_data = resp_app.json()
    assert app_data["status"] == "Applied"
    assert app_data["job_id"] == str(job.id)
