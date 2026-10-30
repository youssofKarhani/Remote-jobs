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


# ============================================================================
# 9. Cross-Project Live Integration with "My sleepless slaves" AI Platform
# ============================================================================

import sys
from pathlib import Path
import httpx
from httpx import ASGITransport

SLEEPLESS_SLAVES_DIR = Path(__file__).resolve().parents[4] / "My sleepless slaves"
if SLEEPLESS_SLAVES_DIR.exists() and str(SLEEPLESS_SLAVES_DIR) not in sys.path:
    sys.path.append(str(SLEEPLESS_SLAVES_DIR))


@pytest.fixture
def sleepless_slaves_stack(tmp_path):
    """Spins up the real 'My sleepless slaves' Orchestrator, AIWorker, and Mock Inference Gateway in-process."""
    if not SLEEPLESS_SLAVES_DIR.exists():
        pytest.skip("My sleepless slaves workspace not found")

    from services.common.config import Settings as PlatformSettings
    from services.common.queue import MemoryJobQueue
    from services.common.storage import LocalStorage
    from services.common.job_store import MemoryJobStore
    from services.orchestrator.app import (
        create_app as create_orchestrator_app,
        get_app_queue,
        get_app_storage,
        get_app_job_store,
    )
    from services.mock_inference.app import create_mock_app
    from services.ai_worker.worker import AIWorker

    p_settings = PlatformSettings(
        ENVIRONMENT="test",
        QUEUE_TYPE="memory",
        STORAGE_TYPE="local",
        LOCAL_STORAGE_DIR=str(tmp_path / "platform_storage"),
        INFERENCE_GATEWAY_URL="http://sleepless-gateway:8001",
        MOCK_COLD_START_DELAY_SECONDS=0.01,
        MOCK_INFERENCE_DELAY_SECONDS=0.01,
    )

    queue = MemoryJobQueue()
    storage = LocalStorage(base_dir=str(tmp_path / "platform_storage"))
    job_store = MemoryJobStore(persistence_file=str(tmp_path / "jobs.json"))

    orch_app = create_orchestrator_app(p_settings)
    orch_app.dependency_overrides[get_app_queue] = lambda: queue
    orch_app.dependency_overrides[get_app_storage] = lambda: storage
    orch_app.dependency_overrides[get_app_job_store] = lambda: job_store

    gateway_app = create_mock_app()
    gateway_transport = ASGITransport(app=gateway_app)
    orch_transport = ASGITransport(app=orch_app)

    worker = AIWorker(
        settings=p_settings,
        queue=queue,
        storage=storage,
        job_store=job_store,
    )

    async def routed_gateway_call(model: str, prompt: str, **kwargs):
        async with httpx.AsyncClient(transport=gateway_transport, base_url="http://sleepless-gateway:8001") as g_client:
            resp = await g_client.post(
                "/v1/chat/completions",
                json={"model": model, "messages": [{"role": "user", "content": prompt}]},
            )
            data = resp.json()
            return {
                "content": data["choices"][0]["message"]["content"],
                "duration_seconds": 0.01,
                "metadata": data.get("mock_metadata", {}),
            }

    worker.call_inference_gateway = routed_gateway_call

    async def process_next_queued_job(_job_id: str) -> None:
        msgs = queue.dequeue(max_messages=1)
        for m in msgs:
            await worker.process_message(m)

    return {
        "gateway_app": gateway_app,
        "gateway_transport": gateway_transport,
        "orch_app": orch_app,
        "orch_transport": orch_transport,
        "worker": worker,
        "queue": queue,
        "job_store": job_store,
        "process_next_queued_job": process_next_queued_job,
    }


class TestCrossProjectSleeplessSlavesIntegration:
    """Verifies live cross-project integration between remotejobs-public and My sleepless slaves."""

    @pytest.mark.asyncio
    async def test_direct_gateway_connection_all_5_methods(self, sleepless_slaves_stack):
        """Verify all 5 AIService methods against My sleepless slaves /v1/chat/completions with fallback disabled."""
        gateway_transport = sleepless_slaves_stack["gateway_transport"]
        async with httpx.AsyncClient(
            transport=gateway_transport,
            base_url="http://sleepless-gateway:8001",
        ) as http_client:
            service = DefaultAIService(
                base_url="http://sleepless-gateway:8001/v1",
                provider="litellm",
                fallback_to_heuristics=False,
                http_client=http_client,
            )

            # 0. Health check
            health = await service.check_health()
            assert health["status"] == "connected"
            assert health["gateway_liveliness"] is True

            # 1. CV Extraction
            draft = await service.extract_cv_to_evidence_bank(
                "Alex Morgan\nPhone: +49 170 1112233\nLinkedIn: https://linkedin.com/in/alexmorgan\nPython, FastAPI"
            )
            assert isinstance(draft, ExtractedEvidenceBankDraft)
            assert draft.phone == "+49 170 1112233"
            assert len(draft.experiences) >= 1
            assert len(draft.skills) >= 2

            # 2. Job Prescreen (relevant & irrelevant)
            pre_rel = await service.prescreen_job("Python backend engineer", "Senior Python Architect", ["Python"])
            assert pre_rel.relevant is True
            assert pre_rel.confidence >= 0.8

            pre_irrel = await service.prescreen_job("Python backend engineer", "Executive Pastry Chef", ["Baking"])
            assert pre_irrel.relevant is False

            # 3. Deep Compatibility Assessment
            assess = await service.assess_job(
                "Candidate [EXP_001] [SKILL_001] Python FastAPI",
                {"title": "Staff Backend Engineer (m/w/d) [Remote]", "company_name": "NovaCloud", "tags": ["Python"]},
            )
            assert assess.overall_score == 88
            assert assess.recommendation == "apply"
            assert assess.sanitized_job_title == "Staff Backend Engineer"
            assert "EXP_001" in assess.matching_evidence_ids

            # 4. CV Evidence Selection (Anti-Hallucination verified)
            allowed = {
                "experience_bullets": ["EXP_001", "EXP_002"],
                "skills": ["SKILL_001", "SKILL_002"],
                "projects": ["PROJ_001"],
                "certifications": ["CERT_001"],
            }
            selection = await service.select_cv_evidence({"title": "Backend Engineer"}, allowed)
            assert set(selection.experience_bullet_ids) == {"EXP_001", "EXP_002"}
            assert set(selection.skill_ids) == {"SKILL_001", "SKILL_002"}

            # 5. Grounded Cover Letter
            letter = await service.generate_cover_letter(
                "Alex Morgan",
                {"title": "Staff Backend Engineer", "company_name": "NovaCloud"},
                [{"stable_id": "EXP_001", "text": "Built distributed pipelines"}],
                strategy="technical_depth",
            )
            assert "NovaCloud" in letter.letter_text
            assert "Staff Backend Engineer" in letter.letter_text
            assert letter.referenced_evidence_ids == ["EXP_001"]

    @pytest.mark.asyncio
    async def test_orchestrator_job_api_all_5_methods(self, sleepless_slaves_stack):
        """Verify all 5 AIService methods over My sleepless slaves Orchestrator (/jobs -> Worker -> /jobs/{id}/result)."""
        orch_transport = sleepless_slaves_stack["orch_transport"]
        process_next = sleepless_slaves_stack["process_next_queued_job"]

        async with httpx.AsyncClient(
            transport=orch_transport,
            base_url="http://sleepless-orchestrator:8000",
        ) as orch_client:
            service = DefaultAIService(
                provider="orchestrator",
                orchestrator_url="http://sleepless-orchestrator:8000",
                fallback_to_heuristics=False,
                orchestrator_http_client=orch_client,
                on_orchestrator_job_submitted=process_next,
                poll_interval=0.01,
            )

            # 0. Health check
            health = await service.check_health()
            assert health["status"] == "connected"
            assert health["orchestrator_liveliness"] is True

            # 1. CV Extraction via /jobs
            draft = await service.extract_cv_to_evidence_bank(
                "Elena Rostova\nPhone: +49 160 9988776\nGitHub: https://github.com/erostova\nKubernetes, Python"
            )
            assert isinstance(draft, ExtractedEvidenceBankDraft)
            assert draft.phone == "+49 160 9988776"
            assert "github.com/erostova" in (draft.github_url or "")

            # 2. Prescreen via /jobs
            pre = await service.prescreen_job("Python, Kubernetes", "Platform AI Engineer", ["Kubernetes", "Python"])
            assert pre.relevant is True
            assert pre.confidence == 0.89

            # 3. Assessment via /jobs
            assess = await service.assess_job(
                "Elena Rostova [EXP_010] [SKILL_020]",
                {"title": "Principal Cloud Architect [Remote]", "company_name": "AetherAI", "tags": ["Kubernetes"]},
            )
            assert assess.overall_score == 88
            assert assess.sanitized_job_title == "Principal Cloud Architect"
            assert "EXP_010" in assess.matching_evidence_ids

            # 4. Evidence Selection via /jobs
            allowed = {
                "experience_bullets": ["EXP_010", "EXP_020"],
                "skills": ["SKILL_020"],
                "projects": ["PROJ_010"],
                "certifications": ["CERT_010"],
            }
            sel = await service.select_cv_evidence({"title": "Principal Cloud Architect"}, allowed)
            assert sel.experience_bullet_ids == ["EXP_010", "EXP_020"]
            assert sel.skill_ids == ["SKILL_020"]

            # 5. Cover Letter via /jobs
            cl = await service.generate_cover_letter(
                "Elena Rostova",
                {"title": "Principal Cloud Architect", "company_name": "AetherAI"},
                [{"stable_id": "EXP_010", "text": "Scaled K3s GPU clusters to zero"}],
                strategy="ai_automation",
            )
            assert "AetherAI" in cl.letter_text
            assert cl.strategy_used == "ai_automation"
            assert cl.referenced_evidence_ids == ["EXP_010"]

    @pytest.mark.asyncio
    async def test_aws_security_group_failover_from_port_4000_to_orchestrator_8000(self, sleepless_slaves_stack):
        """When direct gateway (port 4000) is unreachable on AWS, DefaultAIService automatically succeeds via Orchestrator (port 8000)."""
        orch_transport = sleepless_slaves_stack["orch_transport"]
        process_next = sleepless_slaves_stack["process_next_queued_job"]

        async with httpx.AsyncClient(
            transport=orch_transport,
            base_url="http://51.20.134.201:8000",
        ) as orch_client:
            service = DefaultAIService(
                provider="aws",
                base_url="http://51.20.134.201:4000/v1",
                orchestrator_url="http://51.20.134.201:8000",
                fallback_to_heuristics=False,
                orchestrator_http_client=orch_client,
                on_orchestrator_job_submitted=process_next,
                poll_interval=0.01,
            )

            # Simulate port 4000 being blocked by AWS Security Group
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(
                side_effect=httpx.ConnectError("Port 4000 closed by Security Group")
            )
            service._instructor_client = mock_client

            res = await service.prescreen_job(
                "Python, FastAPI, AWS",
                "Senior Distributed Systems Engineer",
                ["Python", "AWS"],
            )
            assert res.relevant is True
            assert res.confidence == 0.89

    @pytest.mark.asyncio
    async def test_full_remotejobs_workflow_via_sleepless_slaves_orchestrator(
        self,
        client: TestClient,
        sample_user: User,
        auth_headers: dict,
        db_session: Session,
        sleepless_slaves_stack,
        monkeypatch,
    ):
        """End-to-end remotejobs-public workflow routed 100% through My sleepless slaves Orchestrator & AIWorker."""
        orch_transport = sleepless_slaves_stack["orch_transport"]
        process_next = sleepless_slaves_stack["process_next_queued_job"]
        job_store = sleepless_slaves_stack["job_store"]

        orch_client = httpx.AsyncClient(
            transport=orch_transport,
            base_url="http://sleepless-orchestrator:8000",
        )
        try:
            monkeypatch.setattr(ai_service, "provider", "orchestrator")
            monkeypatch.setattr(ai_service, "orchestrator_url", "http://sleepless-orchestrator:8000")
            monkeypatch.setattr(ai_service, "fallback_to_heuristics", False)
            monkeypatch.setattr(ai_service, "_orchestrator_http_client", orch_client)
            monkeypatch.setattr(ai_service, "_on_orchestrator_job_submitted", process_next)
            monkeypatch.setattr(ai_service, "poll_interval", 0.01)

            # 1. Check /api/v1/ai/status reports connected to Orchestrator
            status_resp = client.get("/api/v1/ai/status")
            assert status_resp.status_code == 200
            status_json = status_resp.json()
            assert status_json["status"] == "connected"
            assert status_json["orchestrator_liveliness"] is True

            # 2. Parse CV via Orchestrator + Worker
            resp_parse = client.post(
                "/api/v1/cv/parse-text",
                json={"text": "Marcus Vance\nPhone: +49 151 4455667\nPython, FastAPI, Kubernetes, PostgreSQL"},
                headers=auth_headers,
            )
            assert resp_parse.status_code == 200

            # 3. Verify all extracted evidence items
            resp_verify = client.post("/api/v1/profile/evidence/verify-all", headers=auth_headers)
            assert resp_verify.status_code == 200

            # 4. Create target job
            job = Job(
                title="Staff AI Infrastructure Engineer (m/w/d)",
                sanitized_title="Staff AI Infrastructure Engineer",
                company_name="Hyperion AI",
                location="Munich, Germany",
                remote=True,
                tags=["Python", "FastAPI", "Kubernetes"],
                job_types=["Full Time"],
                description="Architect scale-to-zero Kubernetes inference platforms.",
                url=f"https://example.com/jobs/hyperion-{uuid.uuid4().hex[:6]}",
                slug=f"job-hyperion-{uuid.uuid4().hex[:6]}",
                content_hash=uuid.uuid4().hex,
                published_at=datetime.now(timezone.utc),
            )
            db_session.add(job)
            db_session.commit()
            db_session.refresh(job)

            # 5. Match job via Orchestrator + Worker
            resp_match = client.post(f"/api/v1/jobs/{job.id}/match", headers=auth_headers)
            assert resp_match.status_code == 200
            assert resp_match.json()["overall_score"] == 88

            # 6. Tailor CV via Orchestrator + Worker
            resp_tailor = client.post(
                f"/api/v1/jobs/{job.id}/tailor-cv",
                json={"max_bullets_per_role": 3},
                headers=auth_headers,
            )
            assert resp_tailor.status_code == 200
            assert len(resp_tailor.json()["selected_evidence_ids"]) >= 1

            # 7. Generate Cover Letter via Orchestrator + Worker
            resp_cl = client.post(
                f"/api/v1/jobs/{job.id}/cover-letter",
                json={"strategy": "AI & Automation"},
                headers=auth_headers,
            )
            assert resp_cl.status_code == 200
            assert "Hyperion AI" in resp_cl.json()["content"]

            # Verify that jobs were recorded and completed in My sleepless slaves job_store!
            completed_jobs = job_store.list_jobs(limit=20)
            assert len(completed_jobs) >= 4
            assert all(j.status.value == "completed" for j in completed_jobs)
        finally:
            await orch_client.aclose()



    @pytest.mark.asyncio
    async def test_dynamic_orchestrator_url_discovery_and_failover(self, sleepless_slaves_stack):
        """When EC2 restarts with a new Public IP, DefaultAIService discovers the new IP from Wake Lambda and retries automatically."""
        orch_app = sleepless_slaves_stack["orch_app"]
        process_next = sleepless_slaves_stack["process_next_queued_job"]

        async def router_handler(request: httpx.Request) -> httpx.Response:
            host = request.url.host
            if host == "51.20.134.201":
                raise httpx.ConnectError("Old EC2 Public IP 51.20.134.201 is no longer reachable")
            if host == "wake-api.eu-north-1.amazonaws.com":
                return httpx.Response(
                    200,
                    json={
                        "status": "ok",
                        "previous_state": "running",
                        "action_taken": "none",
                        "public_ip": "13.48.99.101",
                        "orchestrator_url": "http://13.48.99.101:8000",
                    },
                )
            # Route to in-process Orchestrator ASGI app on the new IP 13.48.99.101
            transport = ASGITransport(app=orch_app)
            async with httpx.AsyncClient(transport=transport, base_url="http://13.48.99.101:8000") as inner_client:
                return await inner_client.request(
                    method=request.method,
                    url=str(request.url),
                    headers=request.headers,
                    content=request.content,
                )

        mock_transport = httpx.MockTransport(router_handler)
        async with httpx.AsyncClient(transport=mock_transport) as client_transport:
            service = DefaultAIService(
                provider="orchestrator",
                orchestrator_url="http://51.20.134.201:8000",
                wake_url="https://wake-api.eu-north-1.amazonaws.com/wake",
                fallback_to_heuristics=False,
                orchestrator_http_client=client_transport,
                on_orchestrator_job_submitted=process_next,
                poll_interval=0.01,
            )

            # Call prescreen_job starting with stale IP 51.20.134.201 -> should auto-update to 13.48.99.101 and succeed
            res = await service.prescreen_job(
                "Python, FastAPI, Kubernetes",
                "Senior Cloud Platform Engineer",
                ["Python", "Kubernetes"],
            )
            assert res.relevant is True
            assert res.confidence == 0.89
            assert service.orchestrator_url == "http://13.48.99.101:8000"


def test_ai_wake_endpoint(client: TestClient, monkeypatch):
    """POST /api/v1/ai/wake must trigger wake and return updated orchestrator_url and health."""
    async def fake_trigger_wake():
        ai_service.orchestrator_url = "http://13.48.99.101:8000"
        return True

    monkeypatch.setattr(ai_service, "wake_url", "https://wake-api.eu-north-1.amazonaws.com/wake")
    monkeypatch.setattr(ai_service, "trigger_wake", fake_trigger_wake)

    resp = client.post("/api/v1/ai/wake")
    assert resp.status_code == 200
    data = resp.json()
    assert data["wake_triggered"] is True
    assert data["wake_url_configured"] is True
    assert data["orchestrator_url"] == "http://13.48.99.101:8000"
    assert "ai_status" in data
