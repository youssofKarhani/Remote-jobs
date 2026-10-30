"""Concrete implementation of AIService Protocol utilizing Instructor and structured parsing.

Connects to LiteLLM / AWS Inference gateway / OpenAI-compatible endpoints with logical
model routing (fast, reasoning, coding, writing), automatic fallback to a robust
heuristic engine when endpoints are unavailable or offline, and strict post-generation
verification to prevent hallucinated evidence IDs.
"""

import asyncio
import json
import logging
import re
import time
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set, Tuple, Type, TypeVar
import httpx
from pydantic import BaseModel

from app.config import settings
from app.protocols.ai_service import (
    AIService,
    CoverLetterResult,
    CVSelectionResult,
    ExtractedCertification,
    ExtractedEducation,
    ExtractedEvidenceBankDraft,
    ExtractedEvidenceBullet,
    ExtractedExperience,
    ExtractedProject,
    ExtractedSkill,
    JobAssessmentResult,
    PreScreenResult,
)

logger = logging.getLogger("app.integrations.llm_ai_service")

T = TypeVar("T", bound=BaseModel)

VALID_ORCHESTRATOR_MODELS = {"fast", "reasoning", "coding", "writing", "agent"}


class DefaultAIService:
    """Production AIService implementing the AIService protocol.
    
    Supports:
    1. LiteLLM Unified Gateway / OpenAI-compatible endpoints (/v1/chat/completions).
    2. Personal AI Platform Orchestrator API (/jobs -> /jobs/{id}/result on port 8000) & Serverless Wake.
    3. Automatic dynamic EC2 Public IP / orchestrator_url discovery via Serverless Wake Lambda.
    4. Logical model aliases (fast, reasoning, coding, writing).
    5. Strict anti-hallucination post-validation on evidence IDs.
    6. Seamless, deterministic heuristic fallbacks when the LLM endpoint is unreachable.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        provider: Optional[str] = None,
        model_prescreen: Optional[str] = None,
        model_assessment: Optional[str] = None,
        model_extraction: Optional[str] = None,
        model_tailoring: Optional[str] = None,
        model_cover_letter: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        fallback_to_heuristics: Optional[bool] = None,
        orchestrator_url: Optional[str] = None,
        wake_url: Optional[str] = None,
        poll_interval: Optional[float] = None,
        http_client: Optional[httpx.AsyncClient] = None,
        orchestrator_http_client: Optional[httpx.AsyncClient] = None,
        on_orchestrator_job_submitted: Optional[Callable[[str], Coroutine[Any, Any, None]]] = None,
    ):
        raw_url = base_url or settings.AWS_INFERENCE_ENDPOINT or settings.LLM_BASE_URL
        clean_url = raw_url.rstrip("/")
        if not clean_url.endswith("/v1") and not clean_url.endswith("/api"):
            clean_url += "/v1"
        self.base_url = clean_url
        self.api_key = api_key if api_key is not None else settings.LLM_API_KEY
        self.provider = provider or settings.LLM_PROVIDER
        self.model_prescreen = model_prescreen or settings.LLM_MODEL_PRESCREEN
        self.model_assessment = model_assessment or settings.LLM_MODEL_ASSESSMENT
        self.model_extraction = model_extraction or settings.LLM_MODEL_EXTRACTION
        self.model_tailoring = model_tailoring or settings.LLM_MODEL_TAILORING
        self.model_cover_letter = model_cover_letter or settings.LLM_MODEL_COVER_LETTER
        self.timeout = timeout if timeout is not None else settings.LLM_TIMEOUT_SECONDS
        self.max_retries = max_retries if max_retries is not None else settings.LLM_MAX_RETRIES
        self.fallback_to_heuristics = (
            fallback_to_heuristics
            if fallback_to_heuristics is not None
            else settings.LLM_FALLBACK_TO_HEURISTICS
        )
        self._explicit_orchestrator = orchestrator_url is not None or orchestrator_http_client is not None
        self.orchestrator_url = (orchestrator_url if orchestrator_url is not None else settings.ORCHESTRATOR_URL).rstrip("/")
        self.wake_url = wake_url if wake_url is not None else settings.AWS_WAKE_ENDPOINT
        self.poll_interval = (
            poll_interval
            if poll_interval is not None
            else settings.ORCHESTRATOR_POLL_INTERVAL_SECONDS
        )
        self._http_client = http_client
        self._orchestrator_http_client = orchestrator_http_client
        self._on_orchestrator_job_submitted = on_orchestrator_job_submitted
        self._instructor_client = None

    def get_client(self):
        """Lazily initialize and return instructor-wrapped AsyncOpenAI client."""
        if self.provider in ("mock", "heuristic", "orchestrator"):
            return None

        if self._instructor_client is None:
            try:
                import instructor
                from openai import AsyncOpenAI

                http_client = self._http_client or httpx.AsyncClient(
                    timeout=httpx.Timeout(self.timeout, connect=min(2.0, self.timeout)),
                )
                raw_client = AsyncOpenAI(
                    base_url=self.base_url,
                    api_key=self.api_key or "sk-dev-litellm-key",
                    http_client=http_client,
                )
                self._instructor_client = instructor.from_openai(
                    raw_client,
                    mode=instructor.Mode.JSON,
                )
            except Exception as e:
                logger.warning("Could not initialize instructor/openai client: %s", e)
                return None
        return self._instructor_client

    def _apply_wake_payload(self, payload: Any) -> Optional[str]:
        """Extract dynamic orchestrator_url or public_ip from Wake Lambda response and update in memory."""
        if not isinstance(payload, dict):
            return None
        cp = payload.get("control_plane") if isinstance(payload.get("control_plane"), dict) else {}
        discovered_url = payload.get("orchestrator_url") or cp.get("orchestrator_url")
        if not discovered_url:
            public_ip = payload.get("public_ip") or cp.get("public_ip")
            if public_ip and isinstance(public_ip, str):
                discovered_url = f"http://{public_ip.strip()}:8000"
        if discovered_url and isinstance(discovered_url, str):
            clean_discovered = discovered_url.strip().rstrip("/")
            if clean_discovered and clean_discovered != self.orchestrator_url:
                logger.info(
                    "Updated orchestrator_url dynamically from %s to %s",
                    self.orchestrator_url,
                    clean_discovered,
                )
                self.orchestrator_url = clean_discovered
            return clean_discovered
        return None

    async def discover_orchestrator_url(self) -> Optional[str]:
        """Query the serverless wake /status endpoint to discover the current EC2 public IP without waking."""
        if not self.wake_url:
            return None
        status_url = re.sub(r"/wake/?$", "/status", self.wake_url.rstrip("/"))
        try:
            if self._orchestrator_http_client is not None:
                resp = await self._orchestrator_http_client.get(status_url)
            else:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.get(status_url)
            if resp.status_code == 200:
                return self._apply_wake_payload(resp.json())
        except Exception as exc:
            logger.debug("Could not query wake status endpoint %s: %s", status_url, exc)
        return None

    async def check_gateway_liveliness(self) -> bool:
        """Probe AI Gateway liveliness / health."""
        if self.provider in ("mock", "heuristic"):
            return True
        if self.provider == "orchestrator":
            return await self.check_orchestrator_liveliness()

        paths_to_try = ["/models", "/health", "/health/liveliness"]
        root_url = self.base_url.removesuffix("/v1")

        async def _probe(client: httpx.AsyncClient) -> bool:
            for path in paths_to_try:
                for base in (self.base_url, root_url):
                    target = f"{base}{path}"
                    try:
                        resp = await client.get(
                            target,
                            headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                        )
                        if resp.status_code in (200, 204):
                            return True
                    except Exception:
                        continue
            return False

        if self._http_client is not None:
            if await _probe(self._http_client):
                return True
        else:
            async with httpx.AsyncClient(timeout=3.0) as client:
                if await _probe(client):
                    return True

        if self.provider == "aws" or self._explicit_orchestrator:
            return await self.check_orchestrator_liveliness()
        return False

    async def check_orchestrator_liveliness(self) -> bool:
        """Probe Personal AI Platform Orchestrator (/health and /inference/status), auto-discovering IP changes."""
        if not self.orchestrator_url and self.wake_url:
            await self.discover_orchestrator_url()
        if not self.orchestrator_url:
            return False

        async def _probe(client: httpx.AsyncClient) -> bool:
            for path in ("/health", "/inference/status"):
                try:
                    resp = await client.get(f"{self.orchestrator_url}{path}")
                    if resp.status_code == 200:
                        return True
                except Exception:
                    continue
            return False

        if self._orchestrator_http_client is not None:
            if await _probe(self._orchestrator_http_client):
                return True
            prev_url = self.orchestrator_url
            new_url = await self.discover_orchestrator_url()
            if new_url and new_url != prev_url:
                return await _probe(self._orchestrator_http_client)
            return False

        async with httpx.AsyncClient(timeout=3.0) as client:
            if await _probe(client):
                return True
            prev_url = self.orchestrator_url
            new_url = await self.discover_orchestrator_url()
            if new_url and new_url != prev_url:
                return await _probe(client)
            return False

    async def trigger_wake(self) -> bool:
        """Trigger serverless wake endpoint if configured for scale-to-zero AWS deployment."""
        if not self.wake_url:
            return False
        try:
            if self._orchestrator_http_client is not None:
                resp = await self._orchestrator_http_client.post(self.wake_url, json={"source": "remotejobs-public"})
            else:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.post(self.wake_url, json={"source": "remotejobs-public"})
            if resp.status_code in (200, 202):
                try:
                    self._apply_wake_payload(resp.json())
                except Exception:
                    pass
                return True
            return False
        except Exception as exc:
            logger.warning("Failed to trigger wake endpoint %s: %s", self.wake_url, exc)
            return False

    async def check_health(self) -> Dict[str, Any]:
        """Return connectivity and configuration diagnostics for the AI gateway and orchestrator."""
        is_live = await self.check_gateway_liveliness()
        orchestrator_live = (
            await self.check_orchestrator_liveliness()
            if self.provider in ("orchestrator", "aws") or self._explicit_orchestrator
            else False
        )
        if self.provider in ("mock", "heuristic"):
            status_str = "mock_mode"
        elif is_live or orchestrator_live:
            status_str = "connected"
        else:
            status_str = "unreachable"

        return {
            "status": status_str,
            "provider": self.provider,
            "base_url": self.base_url,
            "orchestrator_url": self.orchestrator_url,
            "models": {
                "prescreen": self.model_prescreen,
                "assessment": self.model_assessment,
                "extraction": self.model_extraction,
                "tailoring": self.model_tailoring,
                "cover_letter": self.model_cover_letter,
            },
            "gateway_liveliness": is_live,
            "orchestrator_liveliness": orchestrator_live,
            "fallback_to_heuristics": self.fallback_to_heuristics,
        }

    @staticmethod
    def _parse_json_to_model(raw_content: Any, response_model: Type[T]) -> T:
        """Parse a raw string or dict from Orchestrator/LLM into a validated Pydantic model."""
        if isinstance(raw_content, response_model):
            return raw_content
        if isinstance(raw_content, dict):
            if "response" in raw_content and not any(k in raw_content for k in response_model.model_fields):
                return DefaultAIService._parse_json_to_model(raw_content["response"], response_model)
            return response_model.model_validate(raw_content)
        if isinstance(raw_content, str):
            cleaned = raw_content.strip()
            # Strip markdown ```json ... ``` fences if present
            fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.S)
            if fence_match:
                cleaned = fence_match.group(1).strip()
            elif not cleaned.startswith("{"):
                brace_match = re.search(r"(\{.*\})", cleaned, re.S)
                if brace_match:
                    cleaned = brace_match.group(1).strip()
            return response_model.model_validate_json(cleaned)
        raise ValueError(f"Unsupported response content type for {response_model.__name__}: {type(raw_content)}")

    async def _run_orchestrator_job(
        self,
        remotejobs_task: str,
        job_type: str,
        model: str,
        prompt: str,
        system_prompt: str,
        response_model: Type[T],
    ) -> T:
        """Submit a structured inference task to the Personal AI Platform Orchestrator (/jobs) and await result."""
        mapped_model = model if model in VALID_ORCHESTRATOR_MODELS else "reasoning"
        job_req = {
            "job_type": job_type,
            "model": mapped_model,
            "payload": {
                "remotejobs_task": remotejobs_task,
                "prompt": prompt,
                "system_prompt": system_prompt,
                "response_schema": response_model.model_json_schema(),
            },
        }

        async def _submit_and_poll(client: httpx.AsyncClient) -> T:
            try:
                submit_resp = await client.post(f"{self.orchestrator_url}/jobs", json=job_req)
            except (httpx.ConnectError, httpx.TimeoutException):
                if self.wake_url:
                    previous_url = self.orchestrator_url
                    await self.trigger_wake()
                    if self.orchestrator_url and self.orchestrator_url != previous_url:
                        submit_resp = await client.post(f"{self.orchestrator_url}/jobs", json=job_req)
                    else:
                        raise
                else:
                    raise

            if submit_resp.status_code not in (200, 202):
                raise RuntimeError(
                    f"Orchestrator job submission failed with HTTP {submit_resp.status_code}: {submit_resp.text}"
                )

            submit_data = submit_resp.json()
            job_id = submit_data["job_id"]

            if self._on_orchestrator_job_submitted is not None:
                await self._on_orchestrator_job_submitted(job_id)

            deadline = time.monotonic() + self.timeout
            while True:
                res_resp = await client.get(f"{self.orchestrator_url}/jobs/{job_id}/result")
                if res_resp.status_code != 200:
                    raise RuntimeError(
                        f"Orchestrator result check failed with HTTP {res_resp.status_code}: {res_resp.text}"
                    )
                res_data = res_resp.json()
                status_val = res_data.get("status")
                if status_val == "completed":
                    result_obj = res_data.get("result") or {}
                    raw_response = result_obj.get("response", result_obj)
                    return self._parse_json_to_model(raw_response, response_model)
                if status_val == "failed":
                    raise RuntimeError(f"Orchestrator job {job_id} failed: {res_data.get('error')}")

                if time.monotonic() >= deadline:
                    raise TimeoutError(f"Timed out waiting for Orchestrator job {job_id} after {self.timeout}s")
                await asyncio.sleep(self.poll_interval)

        if self._orchestrator_http_client is not None:
            return await _submit_and_poll(self._orchestrator_http_client)

        async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout, connect=min(3.0, self.timeout))) as client:
            return await _submit_and_poll(client)

    async def _execute_structured_task(
        self,
        remotejobs_task: str,
        job_type: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
    ) -> Optional[T]:
        """Execute a structured LLM task via Direct Gateway, Orchestrator API, or both with fallback."""
        if self.provider in ("mock", "heuristic"):
            return None

        # 1. Pure Orchestrator mode
        if self.provider == "orchestrator":
            try:
                return await self._run_orchestrator_job(
                    remotejobs_task=remotejobs_task,
                    job_type=job_type,
                    model=model,
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    response_model=response_model,
                )
            except Exception as exc:
                logger.warning("Orchestrator task '%s' failed (%s). Falling back to heuristic.", remotejobs_task, exc)
                if not self.fallback_to_heuristics:
                    raise
                return None

        # 2. Direct Gateway mode (LiteLLM / OpenAI / AWS / Ollama) with optional Orchestrator fallback
        client = self.get_client()
        primary_exc: Optional[Exception] = None
        if client is not None:
            try:
                return await client.chat.completions.create(
                    model=model,
                    response_model=response_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    max_retries=self.max_retries,
                )
            except Exception as exc:
                primary_exc = exc
                logger.warning("Direct LLM call for '%s' failed (%s).", remotejobs_task, exc)

        # If AWS provider or explicit orchestrator configured, try Orchestrator before heuristic fallback
        if self.provider == "aws" or self._explicit_orchestrator:
            try:
                return await self._run_orchestrator_job(
                    remotejobs_task=remotejobs_task,
                    job_type=job_type,
                    model=model,
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    response_model=response_model,
                )
            except Exception as orch_exc:
                logger.warning("Orchestrator fallback for '%s' also failed (%s).", remotejobs_task, orch_exc)
                if primary_exc is None:
                    primary_exc = orch_exc

        if primary_exc is not None and not self.fallback_to_heuristics:
            raise primary_exc

        return None

    # -------------------------------------------------------------------------
    # 1. CV Extraction to Evidence Bank
    # -------------------------------------------------------------------------
    async def extract_cv_to_evidence_bank(self, cv_text: str) -> ExtractedEvidenceBankDraft:
        """Parse raw CV text into structured Evidence Bank entities."""
        from app.services.document_parser import clean_extracted_cv_text
        raw_cv_text = cv_text
        cleaned_cv_text = clean_extracted_cv_text(cv_text)
        prompt = (
            "You are an expert CV parser. Extract all candidate information, work experiences, "
            "discrete achievement bullets, skills, projects, certifications, and education from "
            "the CV text below into the target schema.\n\n"
            f"<cv_text>\n{cleaned_cv_text}\n</cv_text>"
        )
        result = await self._execute_structured_task(
            remotejobs_task="extract_cv",
            job_type="tailor_cv",
            model=self.model_extraction,
            system_prompt="Extract candidate CV to structured evidence bank.",
            user_prompt=prompt,
            response_model=ExtractedEvidenceBankDraft,
        )
        if result and (result.experiences or result.skills or result.headline):
            result.raw_cv_text = raw_cv_text
            result.cleaned_cv_text = cleaned_cv_text
            result.extraction_mode = "llm"
            return result

        return self._heuristic_cv_extraction(raw_cv_text)

    # -------------------------------------------------------------------------
    # 2. Job Pre-Screening
    # -------------------------------------------------------------------------
    async def prescreen_job(
        self,
        candidate_summary: str,
        job_title: str,
        job_tags: List[str],
    ) -> PreScreenResult:
        """Fast high-recall filter for job relevancy."""
        tags_str = ", ".join(job_tags) if job_tags else "None"
        prompt = (
            "Evaluate if this job opportunity has potential relevance for the candidate based "
            "on their technical summary. Optimize strongly for high recall (do not discard viable matches).\n\n"
            f"Job Title: {job_title}\n"
            f"Job Tags: {tags_str}\n\n"
            f"Candidate Summary:\n{candidate_summary}"
        )
        system_prompt = (
            "You are a fast, high-recall job pre-screener. "
            "Return relevant (bool), confidence (0.0-1.0), reason_codes (list), and reasoning (str)."
        )
        result = await self._execute_structured_task(
            remotejobs_task="prescreen_job",
            job_type="job_analysis",
            model=self.model_prescreen,
            system_prompt=system_prompt,
            user_prompt=prompt,
            response_model=PreScreenResult,
        )
        if result is not None:
            conf = max(0.0, min(1.0, float(result.confidence)))
            return PreScreenResult(
                relevant=bool(result.relevant),
                confidence=conf,
                reason_codes=result.reason_codes or ["ROLE_MATCH"],
                reasoning=result.reasoning or f"Evaluated against title '{job_title}'.",
            )

        return self._heuristic_prescreen(candidate_summary, job_title, job_tags)

    # -------------------------------------------------------------------------
    # 3. Deep Compatibility Assessment
    # -------------------------------------------------------------------------
    async def assess_job(
        self,
        candidate_profile_text: str,
        job_details: Dict[str, Any],
    ) -> JobAssessmentResult:
        """Deep multi-dimensional compatibility assessment."""
        raw_title = job_details.get("title", "")
        sanitized_title = self._sanitize_job_title(raw_title)

        job_desc = job_details.get("description", "")[:4000]
        tags = job_details.get("tags", [])
        company = job_details.get("company_name", "")
        loc = job_details.get("location", "")

        prompt = (
            "Perform a multi-dimensional candidate-job compatibility assessment according to the rubric.\n\n"
            f"Job Title: {raw_title}\n"
            f"Company: {company}\n"
            f"Location: {loc}\n"
            f"Tags: {', '.join(tags)}\n"
            f"<job_description>\n{job_desc}\n</job_description>\n\n"
            f"<candidate_profile>\n{candidate_profile_text}\n</candidate_profile>"
        )
        system_prompt = (
            "You are a deep AI job compatibility evaluator. Assess multi-dimensional scores "
            "(overall_score, skills_score, experience_score, seniority_score, location_score, language_score), "
            "matching_evidence_ids, missing_requirements, strengths, recommendation ('apply', 'consider', 'skip'), "
            "and sanitized_job_title."
        )
        result = await self._execute_structured_task(
            remotejobs_task="assess_job",
            job_type="job_analysis",
            model=self.model_assessment,
            system_prompt=system_prompt,
            user_prompt=prompt,
            response_model=JobAssessmentResult,
        )
        if result is not None:
            rec = result.recommendation.lower()
            if rec not in ("apply", "consider", "skip"):
                rec = "apply" if result.overall_score >= 75 else ("consider" if result.overall_score >= 50 else "skip")

            return JobAssessmentResult(
                overall_score=max(0, min(100, int(result.overall_score))),
                skills_score=max(0, min(100, int(result.skills_score))),
                experience_score=max(0, min(100, int(result.experience_score))),
                seniority_score=max(0, min(100, int(result.seniority_score))),
                location_score=max(0, min(100, int(result.location_score))),
                language_score=max(0, min(100, int(result.language_score))),
                matching_evidence_ids=result.matching_evidence_ids or [],
                missing_requirements=result.missing_requirements or [],
                strengths=result.strengths or ["Relevant background"],
                recommendation=rec,
                confidence=max(0.0, min(1.0, float(result.confidence))),
                sanitized_job_title=result.sanitized_job_title or sanitized_title,
                evaluation_mode="ai",
            )

        return self._heuristic_job_assessment(candidate_profile_text, job_details)

    # -------------------------------------------------------------------------
    # 4. CV Evidence Selection (Strict Anti-Hallucination)
    # -------------------------------------------------------------------------
    async def select_cv_evidence(
        self,
        job_details: Dict[str, Any],
        allowed_evidence_ids: Dict[str, List[str]],
        max_bullets_per_role: int = 4,
    ) -> CVSelectionResult:
        """Select relevant verified stable IDs without modifying or hallucinating bullet text."""
        bullets_ordered = list(dict.fromkeys(allowed_evidence_ids.get("experience_bullets", [])))
        skills_ordered = list(dict.fromkeys(allowed_evidence_ids.get("skills", [])))
        projects_ordered = list(dict.fromkeys(allowed_evidence_ids.get("projects", [])))
        certs_ordered = list(dict.fromkeys(allowed_evidence_ids.get("certifications", [])))

        allowed_bullets: Set[str] = set(bullets_ordered)
        allowed_skills: Set[str] = set(skills_ordered)
        allowed_projects: Set[str] = set(projects_ordered)
        allowed_certs: Set[str] = set(certs_ordered)

        title = job_details.get("title", "")
        tags = job_details.get("tags", [])
        desc = job_details.get("description", "")[:2000]

        prompt = (
            "You are a CV tailoring selector. Select the best matching verified evidence IDs for this job.\n"
            "CRITICAL SAFETY RULE: You MUST ONLY select IDs from the provided allowed lists. "
            "Never invent an ID or generate text.\n\n"
            f"Job Title: {title}\n"
            f"Job Tags: {', '.join(tags)}\n"
            f"Job Description: {desc}\n\n"
            f"Allowed Experience Bullet IDs: {bullets_ordered}\n"
            f"Allowed Skill IDs: {skills_ordered}\n"
            f"Allowed Project IDs: {projects_ordered}\n"
            f"Allowed Certification IDs: {certs_ordered}\n"
        )
        system_prompt = (
            "Select verified candidate evidence IDs matching the target job. "
            "Return JSON with experience_bullet_ids, skill_ids, project_ids, certification_ids."
        )
        raw_selection = await self._execute_structured_task(
            remotejobs_task="select_cv_evidence",
            job_type="tailor_cv",
            model=self.model_tailoring,
            system_prompt=system_prompt,
            user_prompt=prompt,
            response_model=CVSelectionResult,
        )
        if raw_selection is not None:
            # HARD POST-VALIDATION GATE: selected_ids ⊆ allowed_ids
            valid_bullets = [sid for sid in raw_selection.experience_bullet_ids if sid in allowed_bullets]
            valid_skills = [sid for sid in raw_selection.skill_ids if sid in allowed_skills]
            valid_projects = [sid for sid in raw_selection.project_ids if sid in allowed_projects]
            valid_certs = [sid for sid in raw_selection.certification_ids if sid in allowed_certs]

            # Fallback to heuristic order if LLM returned completely empty or invalid selections
            if not valid_bullets and bullets_ordered:
                valid_bullets = bullets_ordered[:max_bullets_per_role]
            if not valid_skills and skills_ordered:
                valid_skills = skills_ordered[:10]
            if not valid_projects and projects_ordered:
                valid_projects = projects_ordered[:3]
            if not valid_certs and certs_ordered:
                valid_certs = certs_ordered[:3]

            return CVSelectionResult(
                experience_bullet_ids=valid_bullets[:max_bullets_per_role * 3],
                skill_ids=valid_skills[:12],
                project_ids=valid_projects[:4],
                certification_ids=valid_certs[:4],
            )

        return self._heuristic_evidence_selection(job_details, allowed_evidence_ids, max_bullets_per_role)

    # -------------------------------------------------------------------------
    # 5. Cover Letter Generation
    # -------------------------------------------------------------------------
    async def generate_cover_letter(
        self,
        candidate_profile_text: str,
        job_details: Dict[str, Any],
        selected_evidence_items: List[Dict[str, Any]],
        strategy: str = "technical_depth",
    ) -> CoverLetterResult:
        """Generate evidence-grounded prose for cover letter."""
        valid_evidence_ids = {
            item.get("stable_id")
            for item in selected_evidence_items
            if item.get("stable_id")
        }

        company = job_details.get("company_name", "the hiring team")
        title = job_details.get("title", "this position")
        evidence_text = "\n".join(
            f"- [{item.get('stable_id')}]: {item.get('text')}"
            for item in selected_evidence_items
            if item.get("text")
        )

        prompt = (
            "Write an evidence-grounded cover letter applying to the following job using the "
            f"'{strategy}' positioning approach. Reference only the candidate's verified achievements. "
            "Do not invent skills, degrees, or companies.\n\n"
            f"Job Title: {title}\n"
            f"Company: {company}\n"
            f"Verified Evidence Items:\n{evidence_text}\n\n"
            f"Candidate Info:\n{candidate_profile_text}"
        )
        system_prompt = (
            "You are an executive cover letter writer. Return JSON with letter_text (str), "
            "strategy_used (str), and referenced_evidence_ids (list of stable IDs referenced in text)."
        )
        result = await self._execute_structured_task(
            remotejobs_task="generate_cover_letter",
            job_type="tailor_cover_letter",
            model=self.model_cover_letter,
            system_prompt=system_prompt,
            user_prompt=prompt,
            response_model=CoverLetterResult,
        )
        if result is not None:
            # Post-validate referenced evidence IDs
            ref_ids = [sid for sid in result.referenced_evidence_ids if sid in valid_evidence_ids]
            if not ref_ids and valid_evidence_ids:
                ref_ids = list(valid_evidence_ids)[:3]

            return CoverLetterResult(
                letter_text=result.letter_text,
                strategy_used=result.strategy_used or strategy,
                referenced_evidence_ids=ref_ids,
            )

        return self._heuristic_cover_letter(candidate_profile_text, job_details, selected_evidence_items, strategy)

    # -------------------------------------------------------------------------
    # Heuristic & Fallback Engines
    # -------------------------------------------------------------------------
    def _sanitize_job_title(self, raw_title: str) -> str:
        """Strip brackets, parenthesized tags, and normalized punctuation from job titles."""
        cleaned = re.sub(r"[\(\[\{].*?[\)\]\}]", "", raw_title)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned or raw_title

    def _heuristic_prescreen(
        self,
        candidate_summary: str,
        job_title: str,
        job_tags: List[str],
    ) -> PreScreenResult:
        """Deterministic heuristic prescreening based on keyword and domain overlap."""
        summary_lower = candidate_summary.lower()
        title_lower = job_title.lower()
        tags_lower = [t.lower() for t in job_tags]

        # Standard technical role indicators
        tech_keywords = [
            "engineer", "developer", "architect", "lead", "software",
            "backend", "full stack", "frontend", "data", "ai", "machine learning",
            "cloud", "devops", "platform", "python", "golang", "java", "react",
        ]

        title_matches = [kw for kw in tech_keywords if kw in title_lower]
        tag_matches = [t for t in tags_lower if t in summary_lower]

        relevant = bool(title_matches or tag_matches)
        confidence = 0.88 if (title_matches and tag_matches) else (0.80 if relevant else 0.40)
        reasons = []
        if title_matches:
            reasons.append("ROLE_ALIGNMENT")
        if tag_matches:
            reasons.append("SKILL_MATCH")
        if not reasons:
            reasons = ["DOMAIN_ALIGNMENT"] if relevant else ["ROLE_MISMATCH"]

        return PreScreenResult(
            relevant=relevant,
            confidence=confidence,
            reason_codes=reasons,
            reasoning=f"Job title '{job_title}' assessed against candidate profile keywords.",
        )

    def _heuristic_job_assessment(
        self,
        candidate_profile_text: str,
        job_details: Dict[str, Any],
    ) -> JobAssessmentResult:
        """Deterministic multi-dimensional compatibility scoring."""
        title = job_details.get("title", "")
        sanitized_title = self._sanitize_job_title(title)
        tags = [t.lower() for t in job_details.get("tags", [])]
        desc_lower = (job_details.get("description") or "").lower()
        profile_lower = candidate_profile_text.lower()

        # Skill scoring
        matched_tags = [t for t in tags if t in profile_lower]
        skills_score = int(70 + (len(matched_tags) / max(len(tags), 1)) * 25) if tags else 85
        skills_score = min(98, max(50, skills_score))

        experience_score = 85
        seniority_score = 82
        location_score = 95 if job_details.get("remote", True) else 80
        language_score = 90

        overall = int(
            (skills_score * 0.35)
            + (experience_score * 0.25)
            + (seniority_score * 0.15)
            + (location_score * 0.15)
            + (language_score * 0.10)
        )

        recommendation = "apply" if overall >= 75 else ("consider" if overall >= 55 else "skip")

        missing = [t.title() for t in tags if t not in profile_lower][:3]
        strengths = ["Strong core engineering fundamentals", "Demonstrated alignment with target technology stack"]

        # Detect candidate evidence IDs mentioned in candidate text
        matching_ids = re.findall(r"\b(?:EXP|SKILL|PROJ|CERT|EDU)_\d+\b", candidate_profile_text)

        return JobAssessmentResult(
            overall_score=overall,
            skills_score=skills_score,
            experience_score=experience_score,
            seniority_score=seniority_score,
            location_score=location_score,
            language_score=language_score,
            matching_evidence_ids=list(dict.fromkeys(matching_ids))[:5],
            missing_requirements=missing,
            strengths=strengths,
            recommendation=recommendation,
            confidence=0.91,
            sanitized_job_title=sanitized_title,
            evaluation_mode="heuristic",
        )

    def _heuristic_evidence_selection(
        self,
        job_details: Dict[str, Any],
        allowed_evidence_ids: Dict[str, List[str]],
        max_bullets_per_role: int = 4,
    ) -> CVSelectionResult:
        """Deterministic selection from allowed candidate evidence IDs."""
        exp_bullets = allowed_evidence_ids.get("experience_bullets", [])
        skills = allowed_evidence_ids.get("skills", [])
        projects = allowed_evidence_ids.get("projects", [])
        certs = allowed_evidence_ids.get("certifications", [])

        return CVSelectionResult(
            experience_bullet_ids=exp_bullets[:max_bullets_per_role * 3],
            skill_ids=skills[:10],
            project_ids=projects[:3],
            certification_ids=certs[:3],
        )

    def _heuristic_cover_letter(
        self,
        candidate_profile_text: str,
        job_details: Dict[str, Any],
        selected_evidence_items: List[Dict[str, Any]],
        strategy: str = "technical_depth",
    ) -> CoverLetterResult:
        """Deterministic evidence-grounded prose generation."""
        company = job_details.get("company_name", "the hiring team")
        title = job_details.get("title", "Software Engineer")
        location = job_details.get("location", "Remote")

        strategy_intros = {
            "technical_depth": (
                "Throughout my engineering career, I have focused on mastering low-latency systems, "
                "robust architectural principles, and test-driven reliability."
            ),
            "business_revenue": (
                "I approach engineering through the lens of measurable business ROI, infrastructure efficiency, "
                "and accelerated product delivery."
            ),
            "ai_automation": (
                "My background centers on building autonomous workflows, high-precision agentic pipelines, "
                "and scalable AI-driven infrastructure."
            ),
            "data_engineering": (
                "I specialize in high-throughput data pipelines, fault-tolerant ingestion, and strict data integrity."
            ),
            "team_leadership": (
                "I pair deep technical execution with proactive mentorship, establishing standards, and cross-functional leadership."
            ),
        }
        lead_in = strategy_intros.get(strategy.lower(), strategy_intros["technical_depth"])

        evidence_snippets = [
            f"• {item.get('text')}"
            for item in selected_evidence_items
            if item.get("text")
        ]
        evidence_ids = [
            item.get("stable_id")
            for item in selected_evidence_items
            if item.get("stable_id")
        ]

        # [HIDDEN:EVIDENCE_VERIFICATION]
        lead_evidence = (
            "Here are verified highlights from my engineering track record that directly support your objectives:\n\n"
            if getattr(settings, "FEATURE_EVIDENCE_VERIFICATION", False)
            else "Here are highlights from my engineering track record that directly support your objectives:\n\n"
        )
        evidence_block = (
            lead_evidence
            + "\n".join(evidence_snippets[:4])
            if evidence_snippets
            else "My track record reflects consistent ownership of core software systems and reliable delivery."
        )

        letter = (
            f"Dear Hiring Team at {company},\n\n"
            f"I am writing to express my enthusiastic interest in the {title} position located in {location}. "
            f"{lead_in}\n\n"
            f"{evidence_block}\n\n"
            f"What particularly attracts me to {company} is your commitment to engineering excellence. "
            f"I welcome the opportunity to discuss how my background aligns with your upcoming technical milestones.\n\n"
            f"Thank you for your consideration.\n\n"
            f"Sincerely,\nCandidate"
        )

        return CoverLetterResult(
            letter_text=letter,
            strategy_used=strategy,
            referenced_evidence_ids=evidence_ids[:4],
        )

    # -------------------------------------------------------------------------
    # Heuristic CV Extraction Hardening Helpers
    # -------------------------------------------------------------------------
    _EXPERIENCE_HEADERS = {
        "experience", "work experience", "professional experience",
        "employment", "employment history", "work history",
        "career history", "relevant experience",
    }
    _SKILLS_HEADERS = {
        "skill", "skills", "technical skills", "technologies",
        "tech stack", "core competencies", "skills & technologies",
        "skills and technologies", "skills technologies",
        "technical competencies", "core skills",
    }
    _PROJECTS_HEADERS = {
        "project", "projects", "key projects", "personal projects",
        "academic projects", "selected projects", "portfolio",
        "portfolio projects", "notable projects", "side projects",
    }
    _CERTIFICATIONS_HEADERS = {
        "certification", "certifications", "certificate", "certificates",
        "courses & certifications", "courses and certifications",
        "courses certifications", "licenses", "licenses & certifications",
        "licenses and certifications", "licenses certifications",
        "credentials", "training & certifications", "training certifications",
    }
    _EDUCATION_HEADERS = {
        "education", "academic background", "education & training",
        "education and training", "education training",
        "academic qualifications", "academics", "educational background",
    }
    _LANGUAGES_HEADERS = {
        "language", "languages", "languages spoken",
        "spoken languages", "foreign languages",
    }
    _SUMMARY_HEADERS = {
        "summary", "professional summary", "executive summary",
        "about me", "profile", "personal profile",
        "objective", "career objective",
    }
    _OTHER_KNOWN_HEADERS = {
        "awards", "honors", "honors & awards", "honors and awards",
        "honors awards", "publications", "volunteer", "volunteering",
        "volunteer experience", "interests", "hobbies", "references",
        "activities", "extracurricular activities", "affiliations",
        "memberships", "contact", "contact information", "personal details",
    }

    _SKILL_CONTINUATION_HEADS = {
        "learning", "processing", "engineering", "science", "intelligence",
        "vision", "networks", "network", "models", "modeling", "systems",
        "system", "analysis", "analytics", "visualization", "computing",
        "architecture", "development", "automation", "integration",
        "integrations", "management", "pipelines", "pipeline",
        "orchestration", "optimization", "mining", "forecasting", "testing",
        "security", "administration", "compose", "script", "scripts",
        "studio", "server", "framework", "frameworks", "api", "apis",
        "warehousing", "governance", "ops", "routing", "prompting", "tuning",
    }
    _SKILL_CONTINUATION_PREFIXES = {
        "reinforcement", "machine", "deep", "statistical", "transfer",
        "federated", "supervised", "unsupervised", "semi-supervised",
        "self-supervised", "natural", "natural language", "language", "data",
        "prompt", "software", "cloud", "computer", "neural", "transformer",
        "real-time", "event-driven", "agent", "web", "business",
        "distributed", "backend", "frontend", "full-stack", "docker",
        "google", "google apps", "google sheets", "looker", "apache",
        "amazon", "microsoft", "power", "continuous", "automated",
        "predictive", "exploratory", "exploratory data", "sentiment",
        "time", "time series", "feature", "model", "fine", "large language",
    }

    @classmethod
    def _is_date_range_or_year_span(cls, candidate: str) -> bool:
        """Return True if candidate string represents a date range or year span rather than a phone number."""
        cand = candidate.strip()
        if not cand:
            return True

        # Reject YYYY - YYYY, MM/YYYY - MM/YYYY, YYYY to YYYY, etc.
        if re.search(
            r"\b(?:(?:0?[1-9]|1[0-2])[/\.\-]\s*)?(?:19|20)\d{2}\s*(?:[-–—/]|to)\s*(?:est\.?\s*)?(?:(?:0?[1-9]|1[0-2])[/\.\-]\s*)?(?:19|20)\d{2}\b",
            cand,
            re.I,
        ):
            return True

        # If not explicitly starting with '+', check if digit groups are just years (1950-2039)
        if not cand.startswith("+"):
            groups = re.findall(r"\d+", cand)
            total_digits = sum(len(g) for g in groups)
            if groups and all(len(g) == 4 and 1950 <= int(g) <= 2039 for g in groups):
                return True
            if total_digits <= 8 and any(len(g) == 4 and 1950 <= int(g) <= 2039 for g in groups):
                return True

        return False

    @classmethod
    def _extract_phone_number(cls, text: str) -> Optional[str]:
        """Extract a valid telephone number while rejecting date ranges such as 2019-2022 or 2020 - 2024."""
        # 1. Check explicitly labeled phone lines first
        for line in text.splitlines():
            label_match = re.search(
                r"(?:phone(?:\s+number)?|tel(?:ephone)?|mobile|cell)\s*[:\-]?\s*(\+?\d[\d \t\-\(\)]{6,22}\d)",
                line,
                re.I,
            )
            if label_match:
                cand = re.sub(r"[ \t]{2,}", " ", label_match.group(1).strip())
                digits = re.sub(r"\D", "", cand)
                if not cls._is_date_range_or_year_span(cand) and 7 <= len(digits) <= 15:
                    return cand

        # 2. Scan lines for standalone international or local phone numbers
        for line in text.splitlines():
            for match in re.finditer(r"(?<![\w/])(\+?\d[\d \t\-\(\)]{6,22}\d)(?![\w/])", line):
                cand = re.sub(r"[ \t]{2,}", " ", match.group(1).strip())
                if cls._is_date_range_or_year_span(cand):
                    continue
                digits = re.sub(r"\D", "", cand)
                if not (8 <= len(digits) <= 15):
                    continue
                # If no leading '+', '0', or '(', require at least 9 digits so 8-digit spans are not misread
                if not cand.startswith(("+", "0", "(")) and len(digits) < 9:
                    continue
                return cand

        return None

    @classmethod
    def _is_footer_or_noise_line(cls, line: str) -> bool:
        """Detect obvious CV footer, guidance, or page-number boilerplate."""
        cleaned = re.sub(r"^[-•*–\s]+", "", line).strip()
        if not cleaned:
            return True
        lower = cleaned.lower()

        if re.search(r"^for more information\b.*\bvisit my\b", lower):
            return True
        if re.search(
            r"^for more information on my\s+(?:education|certificates?|certifications?|projects?|experience|skills)",
            lower,
        ):
            return True
        if re.match(r"^visit my (?:linkedin|github|portfolio)(?:\s+profile)?\.?$", lower):
            return True
        if re.match(r"^references?\s+available\s+(?:upon|on)\s+request\.?$", lower):
            return True
        if re.match(r"^page\s+\d+\s*(?:of|/)\s*\d+\.?$", lower):
            return True
        return False

    @classmethod
    def _detect_section_header(cls, line: str) -> Optional[Tuple[str, str]]:
        """Return (canonical_section, raw_heading) if line is a standalone CV section heading."""
        stripped = line.strip()
        if not stripped or len(stripped) > 55:
            return None
        # Bullet items are never top-level section headers
        if stripped.startswith(("-", "•", "*", "–")):
            return None

        raw_heading = re.sub(r"[\s:–—\-]+$", "", stripped).strip()
        norm = re.sub(r"\s+", " ", raw_heading).lower()
        norm_no_amp = re.sub(r"\s+", " ", norm.replace("&", " ").replace("/", " ")).strip()

        for candidate in (norm, norm_no_amp):
            if candidate in cls._LANGUAGES_HEADERS:
                return ("languages", raw_heading)
            if candidate in cls._CERTIFICATIONS_HEADERS:
                return ("certifications", raw_heading)
            if candidate in cls._PROJECTS_HEADERS:
                return ("projects", raw_heading)
            if candidate in cls._SKILLS_HEADERS:
                return ("skills", raw_heading)
            if candidate in cls._EXPERIENCE_HEADERS:
                return ("experience", raw_heading)
            if candidate in cls._EDUCATION_HEADERS:
                return ("education", raw_heading)
            if candidate in cls._SUMMARY_HEADERS:
                return ("summary", raw_heading)
            if candidate in cls._OTHER_KNOWN_HEADERS:
                return ("other", raw_heading)

        return None

    @classmethod
    def _deinterleave_layout_lines(cls, text: str) -> List[str]:
        """De-interleave two-column layout pages and header contact columns into sequential reading order."""
        from app.services.document_parser import reconstruct_broken_urls
        output_lines: List[str] = []
        pages = text.split("\f")

        contact_right_pattern = re.compile(
            r"^(?:email|address|phone(?:\s+number)?|tel(?:ephone)?|mobile|social\s+links|linkedin|github|portfolio)\s*:|"
            r"^https?://|^\+\d",
            re.I,
        )

        for page in pages:
            raw_lines = [ln.rstrip() for ln in page.splitlines() if ln.strip()]
            if not raw_lines:
                continue

            # Determine if this page has a true two-column body layout:
            # Look for lines with a 4+ space gap where either the left or right segment is a section header,
            # or right-indented section headers (leading spaces >= 22).
            right_header_starts: List[int] = []
            for ln in raw_lines:
                lead_spaces = len(ln) - len(ln.lstrip(" \t"))
                if lead_spaces >= 22 and cls._detect_section_header(ln.strip()) is not None:
                    right_header_starts.append(lead_spaces)
                    continue
                for m in re.finditer(r"(\S)([ \t]{4,})(\S)", ln):
                    split_idx = m.start(3)
                    if split_idx < 18:
                        continue
                    left_seg = ln[: m.end(1)].strip()
                    right_seg = ln[split_idx:].strip()
                    if cls._detect_section_header(right_seg) is not None or (
                        cls._detect_section_header(left_seg) is not None and len(right_seg) > 2
                    ):
                        right_header_starts.append(split_idx)
                        break

            if right_header_starts:
                # Two-column page detected: split lines around the column gutter
                col_gutter = min(right_header_starts)
                left_col: List[str] = []
                right_col: List[str] = []

                for ln in raw_lines:
                    lead_spaces = len(ln) - len(ln.lstrip(" \t"))
                    if lead_spaces >= max(20, col_gutter - 6):
                        right_col.append(ln.strip())
                        continue

                    # Find the gap closest to col_gutter
                    best_split: Optional[Tuple[int, int]] = None
                    for m in re.finditer(r"(\S)([ \t]{4,})(\S)", ln):
                        s_idx = m.start(3)
                        if s_idx >= max(18, col_gutter - 12):
                            best_split = (m.end(1), s_idx)
                            break

                    if best_split is not None:
                        l_part = ln[: best_split[0]].strip()
                        r_part = ln[best_split[1] :].strip()
                        if l_part:
                            left_col.append(l_part)
                        if r_part:
                            right_col.append(r_part)
                    else:
                        left_col.append(ln.strip())

                # Reconstruct any URLs broken within a single column (e.g. right-column wrapped LinkedIn URL)
                left_joined = reconstruct_broken_urls("\n".join(left_col))
                right_joined = reconstruct_broken_urls("\n".join(right_col))
                left_lines_clean = [s.strip() for s in left_joined.splitlines() if s.strip()]
                right_lines_clean = [s.strip() for s in right_joined.splitlines() if s.strip()]

                # Split both columns into pre-section header lines and section body lines
                l_sec_idx = next(
                    (i for i, s in enumerate(left_lines_clean) if cls._detect_section_header(s) is not None),
                    len(left_lines_clean),
                )
                r_sec_idx = next(
                    (i for i, s in enumerate(right_lines_clean) if cls._detect_section_header(s) is not None),
                    len(right_lines_clean),
                )
                output_lines.extend(left_lines_clean[:l_sec_idx])
                output_lines.extend(right_lines_clean[:r_sec_idx])
                output_lines.extend(left_lines_clean[l_sec_idx:])
                output_lines.extend(right_lines_clean[r_sec_idx:])
            else:
                # Single-column body page: still separate right-aligned header contact fields on the same line
                page_left: List[str] = []
                page_right_contacts: List[str] = []
                for ln in raw_lines:
                    split_done = False
                    for m in re.finditer(r"(\S)([ \t]{4,})(\S)", ln):
                        s_idx = m.start(3)
                        l_part = ln[: m.end(1)].strip()
                        r_part = ln[s_idx:].strip()
                        if contact_right_pattern.search(r_part):
                            if l_part:
                                page_left.append(l_part)
                            page_right_contacts.append(r_part)
                            split_done = True
                            break
                    if not split_done:
                        page_left.append(ln.strip())

                if page_right_contacts:
                    reconstructed_contacts = reconstruct_broken_urls("\n".join(page_right_contacts))
                    # Insert contact lines right after initial header lines
                    output_lines.extend(
                        s.strip() for s in reconstructed_contacts.splitlines() if s.strip()
                    )
                output_lines.extend(page_left)

        return output_lines

    @classmethod
    def _split_outside_parens(cls, text: str, delimiters: str = ",|•;") -> List[str]:
        """Split string on delimiter characters only when parenthesis depth is zero."""
        parts: List[str] = []
        buf: List[str] = []
        depth = 0
        delim_set = set(delimiters)
        for ch in text:
            if ch == "(":
                depth += 1
                buf.append(ch)
            elif ch == ")":
                depth = max(0, depth - 1)
                buf.append(ch)
            elif ch in delim_set and depth == 0:
                parts.append("".join(buf).strip())
                buf = []
            else:
                buf.append(ch)
        if buf:
            parts.append("".join(buf).strip())
        return [p for p in parts if p]

    @classmethod
    def _join_wrapped_skill_lines(cls, raw_skill_lines: List[str]) -> List[str]:
        """Join skill lines wrapped across line breaks (e.g. 'Reinforcement\\nLearning')."""
        merged: List[str] = []
        for line in raw_skill_lines:
            stripped = line.strip()
            if not stripped:
                continue
            if not merged:
                merged.append(stripped)
                continue

            prev = merged[-1]
            prev_no_bullet = re.sub(r"^[-•*–]\s*", "", prev).strip()
            curr_is_bullet = stripped.startswith(("-", "•", "*", "–"))

            # 1. Unclosed parentheses in previous line
            if prev.count("(") > prev.count(")"):
                merged[-1] = f"{prev} {stripped}"
                continue

            # 2. Previous line ends with explicit continuation punctuation/conjunction
            if re.search(r"(?:[,/&+\-]|\b(?:and|or|of|for|in|to|with))$", prev.rstrip(), re.I):
                if not curr_is_bullet:
                    joiner = "" if prev.rstrip().endswith("-") else " "
                    merged[-1] = f"{prev.rstrip()}{joiner}{stripped}"
                    continue

            # 3. Current line starts with parenthetical or continuation symbol
            if not curr_is_bullet and stripped.startswith(("(", ")", ",", "/", "&")):
                merged[-1] = f"{prev.rstrip()} {stripped}"
                continue

            # 4. Linguistic / spatial continuation for wrapped multi-word skills (e.g. Reinforcement\nLearning)
            if not curr_is_bullet and ":" not in stripped:
                # Extract last skill token from prev and first skill token from stripped
                prev_after_colon = prev_no_bullet.split(":")[-1].strip()
                prev_tokens = cls._split_outside_parens(prev_after_colon)
                curr_tokens = cls._split_outside_parens(stripped)

                if prev_tokens and curr_tokens:
                    last_item = prev_tokens[-1].strip()
                    first_item = curr_tokens[0].strip()
                    first_word = first_item.split()[0].lower() if first_item.split() else ""
                    last_lower = last_item.lower()
                    last_word = last_lower.split()[-1] if last_lower.split() else ""

                    if (
                        first_word in cls._SKILL_CONTINUATION_HEADS
                        and (
                            last_lower in cls._SKILL_CONTINUATION_PREFIXES
                            or last_word in cls._SKILL_CONTINUATION_PREFIXES
                        )
                    ):
                        merged[-1] = f"{prev.rstrip()} {stripped}"
                        continue

            merged.append(stripped)

        return merged

    @classmethod
    def _infer_skill_category(cls, skill_name: str, category_hint: Optional[str] = None) -> str:
        """Map skill name and optional section subheading to a canonical skill category."""
        hint = (category_hint or "").lower()
        s_low = skill_name.lower()

        if any(k in hint for k in ["ai", "ml", "llm", "machine learning", "data science"]):
            return "ai_ml"
        if any(k in hint for k in ["data", "analytics", "etl"]):
            return "data_engineering"
        if any(k in hint for k in ["cloud", "devops", "infra"]):
            return "devops"
        if any(k in hint for k in ["backend", "web", "api"]):
            return "backend"
        if any(k in hint for k in ["automation", "integration", "tool"]):
            return "tools"

        if any(
            k in s_low
            for k in [
                "machine learning", "deep learning", "reinforcement learning",
                "nlp", "natural language", "llm", "gpt", "gemini", "ollama",
                "tensorflow", "keras", "pytorch", "scikit-learn", "nltk",
                "transformer", "prompt engineering", "agent",
            ]
        ):
            return "ai_ml"
        if any(k in s_low for k in ["pandas", "numpy", "parquet", "bigquery", "etl", "pipeline", "looker", "spark"]):
            return "data_engineering"
        if any(k in s_low for k in ["docker", "kubernetes", "terraform", "opentofu", "ci/cd", "git", "aws", "gcp"]):
            return "devops"
        if any(k in s_low for k in ["python", "java", "sql", "api", "backend", "fastapi", "flask", "node", "postgres", "mysql", "mongodb", "mangodb", "redis"]):
            return "backend"
        return "programming"

    def _heuristic_cv_extraction(self, cv_text: str) -> ExtractedEvidenceBankDraft:
        """Robust heuristic parser for CV text extraction into structured draft entities."""
        from app.services.document_parser import clean_extracted_cv_text, reconstruct_broken_urls
        raw_cv_text = cv_text
        cleaned_text = clean_extracted_cv_text(cv_text)

        # De-interleave two-column layouts and reconstruct any newly adjacent broken URLs
        ordered_lines = self._deinterleave_layout_lines(cleaned_text)
        reconstructed_full = reconstruct_broken_urls("\n".join(ordered_lines))

        # Filter out obvious footer / guidance noise lines (including 2-line wrapped footer)
        lines: List[str] = []
        raw_ordered = [ln.strip() for ln in reconstructed_full.splitlines() if ln.strip()]
        skip_next = False
        for idx, ln in enumerate(raw_ordered):
            if skip_next:
                skip_next = False
                continue
            if self._is_footer_or_noise_line(ln):
                if (
                    idx + 1 < len(raw_ordered)
                    and re.search(r"visit my (?:linkedin|github|portfolio)|linkedin profile\.?$", raw_ordered[idx + 1], re.I)
                ):
                    skip_next = True
                continue
            lines.append(ln)

        headline = None
        summary = None
        phone = self._extract_phone_number(reconstructed_full)
        location = None
        linkedin_url = None
        github_url = None
        portfolio_url = None

        li_match = re.search(r"https?://(?:www\.)?linkedin\.com/in/[\w\-]+", reconstructed_full, re.I)
        if li_match:
            linkedin_url = li_match.group(0).strip()

        gh_match = re.search(r"https?://(?:www\.)?github\.com/[\w\-\.]+", reconstructed_full, re.I)
        if gh_match:
            github_url = gh_match.group(0).strip()

        port_match = re.search(
            r"https?://(?!www\.linkedin\.com|linkedin\.com|www\.github\.com|github\.com)(?:www\.)?[\w\.-]+\.[a-z]{2,}(?:/[\w\-\./]*)?",
            reconstructed_full,
            re.I,
        )
        if port_match:
            portfolio_url = port_match.group(0).strip()

        # Prefer explicit Address/Location lines first, then fallback to City, Country regex
        addr_match = re.search(r"(?:Address|Location)\s*:\s*([^\n]+)", reconstructed_full, re.I)
        if addr_match:
            location = addr_match.group(1).strip()
        else:
            header_chunk = "\n".join(lines[:6])
            loc_match = re.search(r"\b([A-Z][a-zA-Z \t]{2,25}?,\s*[A-Z][a-zA-Z]+)\b", header_chunk)
            if loc_match:
                location = loc_match.group(1).splitlines()[0].strip()

        experiences: List[ExtractedExperience] = []
        skills: List[ExtractedSkill] = []
        projects: List[ExtractedProject] = []
        certifications: List[ExtractedCertification] = []
        education: List[ExtractedEducation] = []
        languages: List[str] = []
        unclassified_sections: Dict[str, List[str]] = {}

        current_section = "header"
        current_other_heading = "other"
        current_exp: Optional[ExtractedExperience] = None
        current_project: Optional[ExtractedProject] = None
        pending_skill_lines: List[str] = []

        action_bullet_pattern = re.compile(
            r"^[-•*–]\s*(?:developed|built|engineered|architected|analyzed|implemented|designed|created|automated|integrated|trained)\b",
            re.I,
        )

        for idx, line in enumerate(lines):
            detected = self._detect_section_header(line)
            if detected is not None:
                sec_name, raw_head = detected
                current_section = sec_name
                if sec_name == "other":
                    current_other_heading = raw_head
                    unclassified_sections.setdefault(current_other_heading, [])
                continue

            if current_section == "header":
                is_contact_line = bool(
                    re.search(
                        r"@|https?://|\+\d|^(?:email|address|phone|tel|mobile|social links|linkedin|github)\b",
                        line,
                        re.I,
                    )
                )
                if not is_contact_line and len(line) < 80:
                    if not headline:
                        headline = line
                    elif (
                        headline
                        and len(headline.split()) <= 4
                        and not any(
                            k in headline.lower()
                            for k in ["engineer", "developer", "architect", "analyst", "manager", "lead", "consultant", "scientist"]
                        )
                        and any(
                            k in line.lower()
                            for k in ["engineer", "developer", "architect", "analyst", "manager", "lead", "consultant", "scientist"]
                        )
                    ):
                        headline = f"{headline} — {line}"

            elif current_section == "summary":
                if not summary:
                    summary = line
                else:
                    summary += " " + line

            elif current_section == "experience":
                is_bullet = line.startswith(("-", "•", "*", "–"))
                # Check if a '- Role Title, MM/YYYY to ...' line is actually a role subheader under a company
                role_date_sub = re.match(
                    r"^[-–]\s*([^,•]{3,75}?),\s*(\d{1,2}/\d{4}|(?:19|20)\d{2})\s*(?:to|[-–—])\s*(Present|Current|\d{1,2}/\d{4}|(?:19|20)\d{2})$",
                    line,
                    re.I,
                )
                is_role_line = (not is_bullet) and any(sep in line for sep in [" - ", " – ", " — ", " | ", " @ "])

                if role_date_sub and current_exp is not None:
                    r_title = role_date_sub.group(1).strip()
                    s_date = role_date_sub.group(2).strip()
                    e_raw = role_date_sub.group(3).strip()
                    is_curr = e_raw.lower() in ("present", "current")
                    e_date = None if is_curr else e_raw
                    if not current_exp.bullets and current_exp.role_title in (
                        "Software Engineer",
                        current_exp.location,
                    ):
                        current_exp.role_title = r_title
                        current_exp.start_date = s_date
                        current_exp.end_date = e_date
                        current_exp.is_current = is_curr
                    else:
                        current_exp = ExtractedExperience(
                            company_name=current_exp.company_name,
                            role_title=r_title,
                            location=current_exp.location,
                            start_date=s_date,
                            end_date=e_date,
                            is_current=is_curr,
                            bullets=[],
                        )
                        experiences.append(current_exp)
                elif is_bullet:
                    bullet_text = re.sub(r"^[-•*–]\s*", "", line).strip()
                    if current_exp and bullet_text:
                        current_exp.bullets.append(
                            ExtractedEvidenceBullet(
                                text=bullet_text,
                                category="experience",
                            )
                        )
                elif is_role_line or current_exp is None:
                    role_parts = re.split(r"\s+[-–—|@]\s+", line, maxsplit=1)
                    if len(role_parts) >= 2:
                        comp = role_parts[0].strip()
                        right_part = role_parts[1].strip()
                        # Check if right_part is a location like 'Beirut, Lebanon (Remote)'
                        if re.search(r"\b(?:remote|hybrid|on-site)\b|,\s*[A-Z]", right_part, re.I) and not any(
                            k in right_part.lower()
                            for k in ["engineer", "developer", "architect", "lead", "analyst", "intern", "consultant", "manager", "director"]
                        ):
                            exp_loc = right_part
                            role = "Software Engineer"
                        else:
                            exp_loc = location or "Remote"
                            role = right_part
                    else:
                        comp = line.strip()
                        role = "Software Engineer"
                        exp_loc = location or "Remote"

                    current_exp = ExtractedExperience(
                        company_name=comp or "Company",
                        role_title=role or "Software Engineer",
                        location=exp_loc,
                        start_date="2022-01",
                        end_date=None,
                        is_current=True,
                        bullets=[],
                    )
                    experiences.append(current_exp)
                else:
                    # Continuation line of previous bullet
                    if current_exp and current_exp.bullets:
                        current_exp.bullets[-1].text = f"{current_exp.bullets[-1].text} {line.strip()}"
                    elif current_exp and len(line) > 15:
                        current_exp.bullets.append(
                            ExtractedEvidenceBullet(
                                text=line.strip(),
                                category="experience",
                            )
                        )

            elif current_section == "skills":
                pending_skill_lines.append(line)

            elif current_section == "projects":
                self._consume_project_line(line, projects)
                current_project = projects[-1] if projects else None

            elif current_section == "education":
                clean_edu = re.sub(r"^[-•*–]\s*", "", line).strip()
                if not clean_edu:
                    continue
                # Check if line is institution continuation for previous education entry
                if (
                    education
                    and education[-1].institution == education[-1].degree
                    and any(k in clean_edu.lower() for k in ["university", "institute", "college", "school", "academy"])
                ):
                    education[-1].institution = clean_edu[:80]
                elif len(clean_edu) > 5:
                    year_matches = re.findall(r"(?:19|20)\d{2}", clean_edu)
                    s_yr = year_matches[0] if len(year_matches) >= 1 else "2020"
                    e_yr = year_matches[1] if len(year_matches) >= 2 else "2024"
                    deg_parts = re.split(r"\s+[-–—]\s+", clean_edu, maxsplit=1)
                    if len(deg_parts) == 2 and any(
                        k in deg_parts[0].lower() for k in ["bsc", "bs", "msc", "ms", "bachelor", "master", "phd", "b.sc", "m.sc"]
                    ):
                        deg_title = deg_parts[0].strip()
                        inst_title = deg_title
                    elif len(deg_parts) == 2:
                        inst_title = deg_parts[0].strip()[:80]
                        deg_title = deg_parts[1].strip()[:80]
                    else:
                        inst_title = clean_edu[:80]
                        deg_title = "Bachelor of Science"

                    education.append(
                        ExtractedEducation(
                            institution=inst_title,
                            degree=deg_title,
                            field_of_study="Computer Science",
                            start_date=s_yr,
                            end_date=e_yr,
                        )
                    )

            elif current_section == "certifications":
                # Guard against portfolio projects leaking into certifications due to layout corruption
                next_line = lines[idx + 1] if idx + 1 < len(lines) else ""
                next_line_2 = lines[idx + 2] if idx + 2 < len(lines) else ""
                looks_like_project_header = (
                    (not line.startswith(("-", "•", "*", "–")))
                    and (
                        "(link)" in line.lower()
                        or "senior project" in line.lower()
                        or "technologies used:" in line.lower()
                        or action_bullet_pattern.search(next_line) is not None
                        or action_bullet_pattern.search(next_line_2) is not None
                        or "technologies used:" in next_line.lower()
                        or "technologies used:" in next_line_2.lower()
                    )
                )
                if looks_like_project_header or "technologies used:" in line.lower() or action_bullet_pattern.search(line):
                    current_section = "projects"
                    self._consume_project_line(line, projects)
                    continue

                clean_cert = re.sub(r"^[-•*–]\s*", "", line).strip()
                if len(clean_cert) > 3:
                    cert_parts = re.split(r"\s+[—–]\s+|\s+-\s+(?=[A-Z])", clean_cert, maxsplit=1)
                    c_name = cert_parts[0].strip()[:120]
                    c_issuer = cert_parts[1].strip()[:80] if len(cert_parts) > 1 else "Professional Certification"
                    certifications.append(
                        ExtractedCertification(
                            name=c_name,
                            issuing_organization=c_issuer,
                            issue_date="2024",
                        )
                    )

            elif current_section == "languages":
                clean_lang = re.sub(r"^[-•*–]\s*", "", line).strip()
                if clean_lang and not self._is_footer_or_noise_line(clean_lang):
                    for lang_item in self._split_outside_parens(clean_lang, delimiters=",;|•"):
                        if lang_item and lang_item not in languages:
                            languages.append(lang_item)

            elif current_section == "other":
                unclassified_sections.setdefault(current_other_heading, []).append(line)

        # Process collected skill lines with wrapped-line continuation support
        joined_skill_lines = self._join_wrapped_skill_lines(pending_skill_lines)
        seen_skills: Set[str] = set()
        for s_line in joined_skill_lines:
            clean_s_line = re.sub(r"^[-•*–]\s*", "", s_line).strip()
            if not clean_s_line:
                continue
            category_hint: Optional[str] = None
            if ":" in clean_s_line:
                head_part, tail_part = clean_s_line.split(":", 1)
                if len(head_part.split()) <= 5:
                    category_hint = head_part.strip()
                    clean_s_line = tail_part.strip()

            for item in self._split_outside_parens(clean_s_line, delimiters=",|•;"):
                s_name = item.strip().rstrip(".")
                if (
                    s_name
                    and len(s_name) <= 120
                    and not s_name.lower().startswith("skill")
                    and s_name.lower() not in seen_skills
                ):
                    seen_skills.add(s_name.lower())
                    skills.append(
                        ExtractedSkill(
                            name=s_name,
                            category=self._infer_skill_category(s_name, category_hint),
                        )
                    )

        if not experiences and len(cv_text) > 30:
            experiences.append(
                ExtractedExperience(
                    company_name="Professional Experience",
                    role_title=headline or "Software Engineer",
                    location=location or "Remote",
                    start_date="2022-01",
                    end_date=None,
                    is_current=True,
                    bullets=[
                        ExtractedEvidenceBullet(
                            text=cv_text[:200].strip(),
                            category="experience",
                        )
                    ],
                )
            )

        if not skills and len(cv_text) > 30:
            known_skills = [
                "Python", "FastAPI", "PostgreSQL", "Docker", "TypeScript",
                "React", "Next.js", "SQL", "Git", "Machine Learning", "REST API",
            ]
            for ks in known_skills:
                if re.search(rf"\b{re.escape(ks)}\b", cv_text, re.I):
                    skills.append(ExtractedSkill(name=ks, category="programming"))

        return ExtractedEvidenceBankDraft(
            headline=headline or "Software & AI Engineer",
            summary=summary or "Experienced software professional.",
            phone=phone,
            location=location or "Remote",
            linkedin_url=linkedin_url,
            github_url=github_url,
            portfolio_url=portfolio_url,
            experiences=experiences,
            skills=skills,
            projects=projects,
            certifications=certifications,
            education=education,
            languages=languages,
            unclassified_sections=unclassified_sections,
            raw_cv_text=raw_cv_text,
            cleaned_cv_text=cleaned_text,
            extraction_mode="heuristic_fallback",
            warnings=["Heuristic CV extraction path used."],
        )

    @classmethod
    def _consume_project_line(cls, line: str, projects: List[ExtractedProject]) -> None:
        """Parse a line inside the Projects section into structured ExtractedProject items."""
        stripped = line.strip()
        if not stripped or len(stripped) <= 3:
            return

        is_bullet = stripped.startswith(("-", "•", "*", "–"))
        tech_match = re.search(r"(?:—|--|-)?\s*Technologies\s+used\s*:\s*(.+)$", stripped, re.I)

        if is_bullet and projects:
            curr = projects[-1]
            bullet_body = re.sub(r"^[-•*–]\s*", "", stripped).strip()
            bullet_tech_match = re.search(r"(?:—|--|-)?\s*Technologies\s+used\s*:\s*(.+)$", bullet_body, re.I)
            if bullet_tech_match:
                tech_str = bullet_tech_match.group(1).strip().rstrip(".")
                parsed_techs = [t.strip() for t in cls._split_outside_parens(tech_str, delimiters=",;") if t.strip()]
                for t in parsed_techs:
                    if t not in curr.technologies:
                        curr.technologies.append(t)
                desc_part = re.sub(r"[\s—–\-]+$", "", bullet_body[: bullet_tech_match.start()]).strip()
                if desc_part:
                    curr.description = (
                        f"{curr.description} {desc_part}".strip()
                        if curr.description != curr.title
                        else desc_part
                    )
            else:
                curr.description = (
                    f"{curr.description} {bullet_body}".strip()
                    if curr.description != curr.title
                    else bullet_body
                )
            return

        # Check if this non-bullet line is a wrapped continuation of the current project description/technologies
        if projects:
            curr = projects[-1]
            if tech_match or curr.description.rstrip().endswith(("—", "-", "Technologies", "used:")):
                if tech_match:
                    tech_str = tech_match.group(1).strip().rstrip(".")
                    for t in cls._split_outside_parens(tech_str, delimiters=",;"):
                        t_clean = t.strip().rstrip(".")
                        if t_clean and t_clean not in curr.technologies:
                            curr.technologies.append(t_clean)
                    prefix_desc = stripped[: tech_match.start()].strip().rstrip("—-").strip()
                    if prefix_desc:
                        curr.description = f"{curr.description} {prefix_desc}".strip()
                else:
                    for t in cls._split_outside_parens(stripped, delimiters=",;"):
                        t_clean = t.strip().rstrip(".")
                        if t_clean and t_clean not in curr.technologies:
                            curr.technologies.append(t_clean)
                return

            # If current project was just created (description == title) and this line is a concise domain/category subtitle
            if (
                curr.description == curr.title
                and curr.category is None
                and len(stripped) <= 60
                and not any(sep in stripped for sep in [" - ", " — "])
                and any(
                    k in stripped.lower()
                    for k in [
                        "machine learning", "software", "engineering", "data", "analytics",
                        "natural language", "nlp", "iot", "cloud", "infrastructure",
                        "full-stack", "web", "development", "backend", "frontend", "ai", "automation",
                    ]
                )
            ):
                curr.category = stripped
                return

            # If current project already has a description and this line is a lowercase continuation or ends with a period
            if curr.description != curr.title and (stripped[0].islower() or len(stripped) > 65):
                curr.description = f"{curr.description} {stripped}".strip()
                return

        # Single-line 'Project Title - Description' format (excluding '- Senior Project (link)')
        if " - " in stripped and "senior project" not in stripped.lower():
            t_part, d_part = stripped.split(" - ", 1)
            if len(t_part.strip()) <= 50 and len(d_part.strip()) >= 10:
                projects.append(
                    ExtractedProject(
                        title=t_part.strip(),
                        description=stripped,
                        technologies=[],
                    )
                )
                return

        if len(stripped) > 4:
            projects.append(
                ExtractedProject(
                    title=stripped[:80],
                    description=stripped,
                    technologies=[],
                )
            )


# Global singleton instance
ai_service = DefaultAIService()
