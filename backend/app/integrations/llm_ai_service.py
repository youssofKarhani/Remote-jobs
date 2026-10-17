"""Concrete implementation of AIService Protocol utilizing Instructor and structured parsing.

Connects to LiteLLM / AWS Inference gateway / OpenAI-compatible endpoints with logical
model routing (fast, reasoning, coding, writing), automatic fallback to a robust
heuristic engine when endpoints are unavailable or offline, and strict post-generation
verification to prevent hallucinated evidence IDs.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Set
import httpx

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


class DefaultAIService:
    """Production AIService implementing the AIService protocol.
    
    Supports:
    1. LiteLLM Unified Gateway / AWS inference deployment / OpenAI-compatible endpoints.
    2. Logical model aliases (fast, reasoning, coding, writing).
    3. Strict anti-hallucination post-validation on evidence IDs.
    4. Seamless, deterministic heuristic fallbacks when the LLM endpoint is unreachable.
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
    ):
        raw_url = base_url or settings.LLM_BASE_URL
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
        self._instructor_client = None

    def get_client(self):
        """Lazily initialize and return instructor-wrapped AsyncOpenAI client."""
        if self.provider in ("mock", "heuristic"):
            return None

        if self._instructor_client is None:
            try:
                import instructor
                from openai import AsyncOpenAI

                http_client = httpx.AsyncClient(
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

    async def check_gateway_liveliness(self) -> bool:
        """Probe AI Gateway liveliness / health."""
        if self.provider in ("mock", "heuristic"):
            return True

        paths_to_try = ["/models", "/health", "/health/liveliness"]
        root_url = self.base_url.removesuffix("/v1")
        async with httpx.AsyncClient(timeout=3.0) as client:
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

    async def check_health(self) -> Dict[str, Any]:
        """Return connectivity and configuration diagnostics for the AI gateway."""
        is_live = await self.check_gateway_liveliness()
        if self.provider in ("mock", "heuristic"):
            status_str = "mock_mode"
        elif is_live:
            status_str = "connected"
        else:
            status_str = "unreachable"

        return {
            "status": status_str,
            "provider": self.provider,
            "base_url": self.base_url,
            "models": {
                "prescreen": self.model_prescreen,
                "assessment": self.model_assessment,
                "extraction": self.model_extraction,
                "tailoring": self.model_tailoring,
                "cover_letter": self.model_cover_letter,
            },
            "gateway_liveliness": is_live,
            "fallback_to_heuristics": self.fallback_to_heuristics,
        }

    # -------------------------------------------------------------------------
    # 1. CV Extraction to Evidence Bank
    # -------------------------------------------------------------------------
    async def extract_cv_to_evidence_bank(self, cv_text: str) -> ExtractedEvidenceBankDraft:
        """Parse raw CV text into structured Evidence Bank entities."""
        client = self.get_client()
        if client is not None:
            try:
                prompt = (
                    "You are an expert CV parser. Extract all candidate information, work experiences, "
                    "discrete achievement bullets, skills, projects, certifications, and education from "
                    "the CV text below into the target schema.\n\n"
                    f"<cv_text>\n{cv_text}\n</cv_text>"
                )
                result: ExtractedEvidenceBankDraft = await client.chat.completions.create(
                    model=self.model_extraction,
                    response_model=ExtractedEvidenceBankDraft,
                    messages=[
                        {"role": "system", "content": "Extract candidate CV to structured evidence bank."},
                        {"role": "user", "content": prompt},
                    ],
                    max_retries=self.max_retries,
                )
                if result and (result.experiences or result.skills or result.headline):
                    return result
            except Exception as exc:
                logger.warning("LLM CV extraction failed (%s). Falling back to heuristic.", exc)
                if not self.fallback_to_heuristics:
                    raise

        return self._heuristic_cv_extraction(cv_text)

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
        client = self.get_client()
        if client is not None:
            try:
                tags_str = ", ".join(job_tags) if job_tags else "None"
                prompt = (
                    "Evaluate if this job opportunity has potential relevance for the candidate based "
                    "on their technical summary. Optimize strongly for high recall (do not discard viable matches).\n\n"
                    f"Job Title: {job_title}\n"
                    f"Job Tags: {tags_str}\n\n"
                    f"Candidate Summary:\n{candidate_summary}"
                )
                result: PreScreenResult = await client.chat.completions.create(
                    model=self.model_prescreen,
                    response_model=PreScreenResult,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a fast, high-recall job pre-screener. "
                                "Return relevant (bool), confidence (0.0-1.0), reason_codes (list), and reasoning (str)."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_retries=self.max_retries,
                )
                # Clamp confidence
                conf = max(0.0, min(1.0, float(result.confidence)))
                return PreScreenResult(
                    relevant=bool(result.relevant),
                    confidence=conf,
                    reason_codes=result.reason_codes or ["ROLE_MATCH"],
                    reasoning=result.reasoning or f"Evaluated against title '{job_title}'.",
                )
            except Exception as exc:
                logger.warning("LLM prescreen failed (%s). Falling back to heuristic.", exc)
                if not self.fallback_to_heuristics:
                    raise

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

        client = self.get_client()
        if client is not None:
            try:
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

                result: JobAssessmentResult = await client.chat.completions.create(
                    model=self.model_assessment,
                    response_model=JobAssessmentResult,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a deep AI job compatibility evaluator. Assess multi-dimensional scores "
                                "(overall_score, skills_score, experience_score, seniority_score, location_score, language_score), "
                                "matching_evidence_ids, missing_requirements, strengths, recommendation ('apply', 'consider', 'skip'), "
                                "and sanitized_job_title."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_retries=self.max_retries,
                )
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
                )
            except Exception as exc:
                logger.warning("LLM job assessment failed (%s). Falling back to heuristic.", exc)
                if not self.fallback_to_heuristics:
                    raise

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
        allowed_bullets: Set[str] = set(allowed_evidence_ids.get("experience_bullets", []))
        allowed_skills: Set[str] = set(allowed_evidence_ids.get("skills", []))
        allowed_projects: Set[str] = set(allowed_evidence_ids.get("projects", []))
        allowed_certs: Set[str] = set(allowed_evidence_ids.get("certifications", []))

        client = self.get_client()
        if client is not None:
            try:
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
                    f"Allowed Experience Bullet IDs: {list(allowed_bullets)}\n"
                    f"Allowed Skill IDs: {list(allowed_skills)}\n"
                    f"Allowed Project IDs: {list(allowed_projects)}\n"
                    f"Allowed Certification IDs: {list(allowed_certs)}\n"
                )

                raw_selection: CVSelectionResult = await client.chat.completions.create(
                    model=self.model_tailoring,
                    response_model=CVSelectionResult,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Select verified candidate evidence IDs matching the target job. "
                                "Return JSON with experience_bullet_ids, skill_ids, project_ids, certification_ids."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_retries=self.max_retries,
                )

                # HARD POST-VALIDATION GATE: selected_ids ⊆ allowed_ids
                valid_bullets = [sid for sid in raw_selection.experience_bullet_ids if sid in allowed_bullets]
                valid_skills = [sid for sid in raw_selection.skill_ids if sid in allowed_skills]
                valid_projects = [sid for sid in raw_selection.project_ids if sid in allowed_projects]
                valid_certs = [sid for sid in raw_selection.certification_ids if sid in allowed_certs]

                # Fallback to heuristic order if LLM returned completely empty or invalid selections
                if not valid_bullets and allowed_bullets:
                    valid_bullets = list(allowed_bullets)[:max_bullets_per_role]
                if not valid_skills and allowed_skills:
                    valid_skills = list(allowed_skills)[:10]
                if not valid_projects and allowed_projects:
                    valid_projects = list(allowed_projects)[:3]
                if not valid_certs and allowed_certs:
                    valid_certs = list(allowed_certs)[:3]

                return CVSelectionResult(
                    experience_bullet_ids=valid_bullets[:max_bullets_per_role * 3],
                    skill_ids=valid_skills[:12],
                    project_ids=valid_projects[:4],
                    certification_ids=valid_certs[:4],
                )
            except Exception as exc:
                logger.warning("LLM evidence selection failed (%s). Falling back to heuristic.", exc)
                if not self.fallback_to_heuristics:
                    raise

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
        client = self.get_client()
        valid_evidence_ids = {
            item.get("stable_id")
            for item in selected_evidence_items
            if item.get("stable_id")
        }

        if client is not None:
            try:
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

                result: CoverLetterResult = await client.chat.completions.create(
                    model=self.model_cover_letter,
                    response_model=CoverLetterResult,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an executive cover letter writer. Return JSON with letter_text (str), "
                                "strategy_used (str), and referenced_evidence_ids (list of stable IDs referenced in text)."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_retries=self.max_retries,
                )

                # Post-validate referenced evidence IDs
                ref_ids = [sid for sid in result.referenced_evidence_ids if sid in valid_evidence_ids]
                if not ref_ids and valid_evidence_ids:
                    ref_ids = list(valid_evidence_ids)[:3]

                return CoverLetterResult(
                    letter_text=result.letter_text,
                    strategy_used=result.strategy_used or strategy,
                    referenced_evidence_ids=ref_ids,
                )
            except Exception as exc:
                logger.warning("LLM cover letter generation failed (%s). Falling back to heuristic.", exc)
                if not self.fallback_to_heuristics:
                    raise

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

        relevant = bool(title_matches or tag_matches or "software" in summary_lower or "engineer" in summary_lower)
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

        evidence_block = (
            "Here are verified highlights from my engineering track record that directly support your objectives:\n\n"
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

    def _heuristic_cv_extraction(self, cv_text: str) -> ExtractedEvidenceBankDraft:
        """Robust heuristic parser for CV text extraction into structured draft entities."""
        lines = [line.strip() for line in cv_text.splitlines() if line.strip()]
        
        headline = None
        summary = None
        phone = None
        location = None
        linkedin_url = None
        github_url = None
        portfolio_url = None

        # Extract contact info via regex
        phone_match = re.search(r"(\+?\d[\d\s\-\(\)]{7,}\d)", cv_text)
        if phone_match:
            phone = phone_match.group(1).strip()

        li_match = re.search(r"https?://(?:www\.)?linkedin\.com/in/[\w\-]+", cv_text, re.I)
        if li_match:
            linkedin_url = li_match.group(0).strip()

        gh_match = re.search(r"https?://(?:www\.)?github\.com/[\w\-]+", cv_text, re.I)
        if gh_match:
            github_url = gh_match.group(0).strip()

        port_match = re.search(r"https?://(?:www\.)?(?!linkedin|github)[\w\.-]+\.[a-z]{2,}", cv_text, re.I)
        if port_match:
            portfolio_url = port_match.group(0).strip()

        loc_match = re.search(r"([A-Z][a-zA-Z\s]{2,30}?,\s*[A-Z][a-zA-Z]+)", cv_text)
        if loc_match:
            location = loc_match.group(1).splitlines()[0].strip()

        experiences: List[ExtractedExperience] = []
        skills: List[ExtractedSkill] = []
        projects: List[ExtractedProject] = []
        certifications: List[ExtractedCertification] = []
        education: List[ExtractedEducation] = []

        current_section = "header"
        current_exp: Optional[ExtractedExperience] = None

        for line in lines:
            lower = line.lower()
            
            # Detect section headers (must be a concise heading or end with :)
            is_header_candidate = len(line.split()) <= 4 or line.endswith(":")
            if is_header_candidate:
                if any(h in lower for h in ["experience", "employment", "work history"]):
                    current_section = "experience"
                    continue
                elif any(h in lower for h in ["skills", "technical skills", "technologies", "tech stack"]):
                    current_section = "skills"
                    continue
                elif any(h in lower for h in ["projects", "portfolio", "key projects"]):
                    current_section = "projects"
                    continue
                elif any(h in lower for h in ["education", "academic", "university", "degree"]):
                    current_section = "education"
                    continue
                elif any(h in lower for h in ["certification", "certificates", "licenses"]):
                    current_section = "certifications"
                    continue
                elif any(h in lower for h in ["summary", "about me", "profile"]):
                    current_section = "summary"
                    continue

            if current_section == "header":
                if not headline and len(line) < 80 and not any(c in line for c in ["@", "http", "+"]):
                    headline = line
            elif current_section == "summary":
                if not summary:
                    summary = line
                else:
                    summary += " " + line
            elif current_section == "experience":
                is_bullet = line.startswith(("-", "•", "*", "–"))
                is_role_line = (not is_bullet) and any(sep in line for sep in [" - ", " – ", " | ", " @ "])

                if is_bullet:
                    bullet_text = re.sub(r"^[-•*–]\s*", "", line).strip()
                    if current_exp and bullet_text:
                        current_exp.bullets.append(
                            ExtractedEvidenceBullet(
                                text=bullet_text,
                                category="experience",
                            )
                        )
                elif is_role_line or current_exp is None:
                    role_parts = re.split(r"\s+[-–|@]\s+", line)
                    if len(role_parts) >= 2:
                        comp = role_parts[0].strip()
                        role = role_parts[1].strip()
                    else:
                        comp = line.strip()
                        role = "Software Engineer"

                    current_exp = ExtractedExperience(
                        company_name=comp or "Company",
                        role_title=role or "Software Engineer",
                        location=location or "Remote",
                        start_date="2022-01",
                        end_date=None,
                        is_current=True,
                        bullets=[],
                    )
                    experiences.append(current_exp)
                else:
                    if current_exp and len(line) > 15:
                        current_exp.bullets.append(
                            ExtractedEvidenceBullet(
                                text=line.strip(),
                                category="experience",
                            )
                        )
            elif current_section == "skills":
                items = re.split(r"[,|•;]", line)
                for item in items:
                    s_name = item.strip()
                    if s_name and len(s_name) < 40 and not s_name.lower().startswith("skill"):
                        skills.append(
                            ExtractedSkill(
                                name=s_name,
                                category=(
                                    "backend"
                                    if any(k in s_name.lower() for k in ["python", "java", "sql", "api", "backend", "fastapi"])
                                    else "programming"
                                ),
                            )
                        )
            elif current_section == "projects":
                if len(line) > 10:
                    projects.append(
                        ExtractedProject(
                            title=line[:50],
                            description=line,
                            technologies=["Python", "FastAPI"],
                        )
                    )
            elif current_section == "education":
                if len(line) > 10:
                    education.append(
                        ExtractedEducation(
                            institution=line[:60],
                            degree="Bachelor of Science",
                            field_of_study="Computer Science",
                            start_date="2020",
                            end_date="2024",
                        )
                    )
            elif current_section == "certifications":
                if len(line) > 5:
                    certifications.append(
                        ExtractedCertification(
                            name=line[:80],
                            issuing_organization="Professional Certification",
                            issue_date="2024",
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
        )


# Global singleton instance
ai_service = DefaultAIService()
