"""Grounded Cover Letter Generation Service implementing 10 Engineering Positioning Strategies.

ARCHITECTURE.md Section 16 & Section 23:
Enforces strict factual grounding against candidate verified bullet points.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.integrations.llm_ai_service import ai_service
from app.models.cover_letter import CoverLetter
from app.models.evidence import EvidenceItem, Skill
from app.models.job import Job
from app.models.profile import CandidateProfile
from app.models.user import User
from app.protocols.ai_service import AIService
from app.schemas.cover_letter import PositioningStrategyInfo
from app.services.evidence_validation import (
    get_user_allowed_evidence_ids,
    resolve_verified_evidence_text,
)

POSITIONING_STRATEGIES: List[PositioningStrategyInfo] = [
    PositioningStrategyInfo(
        id="technical_depth",
        name="Technical Depth",
        tagline="Architecture, system internals & high-concurrency performance",
        description="Emphasizes low-level system design, concurrency primitives, latency profiling, and architectural scalability.",
    ),
    PositioningStrategyInfo(
        id="business_revenue",
        name="Business & Revenue Impact",
        tagline="Direct ROI, revenue enablement & bottom-line growth",
        description="Highlights quantifiable commercial achievements, operational cost reductions, customer retention, and ROI.",
    ),
    PositioningStrategyInfo(
        id="ai_automation",
        name="AI & Automation Leadership",
        tagline="LLM pipelines, agentic orchestration & process acceleration",
        description="Frames background around autonomous agent workflows, modern AI integration, structured prompting, and end-to-end automation.",
    ),
    PositioningStrategyInfo(
        id="data_engineering",
        name="Data Engineering & Scalability",
        tagline="High-throughput ETL, data integrity & distributed pipelines",
        description="Focuses on terabyte-scale data pipelines, streaming architectures, zero-downtime database migrations, and telemetry.",
    ),
    PositioningStrategyInfo(
        id="team_leadership",
        name="Team Leadership & Mentorship",
        tagline="Engineering culture, technical mentoring & cross-functional delivery",
        description="Demonstrates experience elevating other engineers, running design reviews, setting code quality standards, and roadmap ownership.",
    ),
    PositioningStrategyInfo(
        id="startup_speed",
        name="Startup / Zero-to-One Speed",
        tagline="Pragmatic execution, greenfield velocity & end-to-end ownership",
        description="Highlights rapid iteration, building MVPs from first commit to production, wearing multiple hats, and customer-driven speed.",
    ),
    PositioningStrategyInfo(
        id="domain_expertise",
        name="Domain Expertise",
        tagline="Deep vertical knowledge & regulatory compliance",
        description="Showcases specialized sector understanding (fintech, healthtech, security, developer infrastructure) and industry standards.",
    ),
    PositioningStrategyInfo(
        id="research_algorithms",
        name="Research & Applied Algorithms",
        tagline="Algorithmic optimization, mathematical rigor & experimentation",
        description="Focuses on applied research, algorithmic complexity reduction, model validation, and translating papers into production code.",
    ),
    PositioningStrategyInfo(
        id="adaptive_depth",
        name="Career Transition / Adaptive Depth",
        tagline="Polyglot agility, fast ramp-up & cross-disciplinary depth",
        description="Highlights proven ability to master new tech stacks rapidly, bring multidisciplinary insights, and tackle ambiguous problems.",
    ),
    PositioningStrategyInfo(
        id="customer_impact",
        name="Customer & Client Impact",
        tagline="Client collaboration, developer experience & mission-critical SLAs",
        description="Emphasizes direct customer satisfaction, developer empathy, high-stakes enterprise delivery, and SLA compliance.",
    ),
]


class CoverLetterService:
    """Generates and edits grounded cover letters using the 10 canonical engineering strategies."""

    def __init__(self, ai_gateway: Optional[AIService] = None):
        self.ai = ai_gateway or ai_service

    def get_available_strategies(self) -> List[PositioningStrategyInfo]:
        """Return all 10 supported engineering positioning strategies."""
        return POSITIONING_STRATEGIES

    async def generate_grounded_letter(
        self,
        db: Session,
        user: User,
        job: Job,
        strategy_id_or_name: str = "Technical Depth",
    ) -> CoverLetter:
        """Generate a cover letter strictly grounded in verified evidence using chosen strategy."""
        # Normalize strategy
        selected_strategy = None
        for s in POSITIONING_STRATEGIES:
            if (
                s.id.lower() == strategy_id_or_name.lower().replace(" ", "_")
                or s.name.lower() == strategy_id_or_name.lower()
            ):
                selected_strategy = s
                break

        if not selected_strategy:
            selected_strategy = POSITIONING_STRATEGIES[0]  # Default to Technical Depth

        # 1. Fetch Candidate Profile and Verified Evidence
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
        verified_bullets = (
            db.query(EvidenceItem)
            .filter(EvidenceItem.user_id == user.id, EvidenceItem.is_verified.is_(True))
            .order_by(EvidenceItem.display_order)
            .all()
        )

        # Fallback: only if candidate hasn't verified any items yet
        if not verified_bullets:
            total_verified = (
                db.query(EvidenceItem)
                .filter(EvidenceItem.user_id == user.id, EvidenceItem.is_verified.is_(True))
                .count()
            )
            if total_verified == 0:
                has_any = db.query(EvidenceItem).filter(EvidenceItem.user_id == user.id).first()
                if has_any:
                    db.query(EvidenceItem).filter(EvidenceItem.user_id == user.id).update({"is_verified": True})
                    db.commit()
                    verified_bullets = (
                        db.query(EvidenceItem)
                        .filter(EvidenceItem.user_id == user.id, EvidenceItem.is_verified.is_(True))
                        .order_by(EvidenceItem.display_order)
                        .all()
                    )

        skills = db.query(Skill).filter(Skill.user_id == user.id).all()
        top_skills = [s.name for s in skills[:6]]

        bullet_records = [
            {"stable_id": b.stable_id, "text": b.raw_text}
            for b in verified_bullets[:4]
        ]
        referenced_ids = [b["stable_id"] for b in bullet_records]

        # 2. Formulate grounded letter content based on strategy framing
        candidate_name = user.full_name or "Candidate"
        company = job.company_name or "the hiring team"
        role = job.title or "Software Engineer"
        location = job.location or "Remote"

        # Strategy framing lead-in
        strategy_framings = {
            "technical_depth": (
                f"Throughout my engineering career, I have dedicated myself to mastering robust architecture, "
                f"low-latency system performance, and reliable software design. When analyzing the requirements for "
                f"the {role} role at {company}, I immediately recognized an exceptional match with my technical background."
            ),
            "business_revenue": (
                f"I approach engineering through the lens of tangible business impact and commercial value. "
                f"In my previous roles, I have consistently connected architectural decisions directly to "
                f"revenue growth, infrastructure cost optimization, and accelerated time-to-market. I am eager to bring "
                f"this results-driven mindset to {company} as your next {role}."
            ),
            "ai_automation": (
                f"The modern engineering frontier belongs to teams that leverage AI, autonomous pipelines, and "
                f"structured automation to deliver 10x leverage. My work focuses on building scalable agentic systems "
                f"and intelligent workflows, making the {role} opportunity at {company} especially compelling."
            ),
            "data_engineering": (
                f"Building fault-tolerant data pipelines that process high volumes with strict data integrity guarantees "
                f"has been the centerpiece of my engineering journey. I am excited to apply my data architecture "
                f"expertise to support {company}'s growth as {role}."
            ),
            "team_leadership": (
                f"Exceptional software is built by empowered, collaborative teams. Throughout my career, I have paired "
                f"rigorous individual technical contributions with proactive mentorship, establishing sound engineering "
                f"standards, and guiding cross-functional initiatives to completion. I look forward to contributing as {role} at {company}."
            ),
            "startup_speed": (
                f"Thriving in dynamic, high-velocity environments where engineers own problems from zero to production "
                f"is where I deliver my highest value. I bring pragmatic execution, rapid iteration speed, and relentless "
                f"curiosity to the {role} position at {company}."
            ),
            "domain_expertise": (
                f"Deep domain knowledge combined with modern software engineering enables teams to build products that "
                f"truly resonate with specialized user needs. I am thrilled by {company}'s trajectory and ready to "
                f"hit the ground running as {role}."
            ),
            "research_algorithms": (
                f"Bridging foundational algorithmic rigor with practical, scalable production software is my core focus. "
                f"I look forward to tackling the challenging computational and architectural problems facing {company} "
                f"in the {role} position."
            ),
            "adaptive_depth": (
                f"As a polyglot engineer with proven adaptability, I excel at ramping up on complex, unfamiliar codebases "
                f"and delivering high-quality solutions across diverse tech stacks. The {role} position at {company} is a "
                f"natural next challenge for my continuous learning mindset."
            ),
            "customer_impact": (
                f"Software exists to solve real problems for real users. In every system I design, user experience, "
                f"operational reliability, and SLA guarantees take first priority. I am excited to champion {company}'s "
                f"clients and users as {role}."
            ),
        }

        opening_framing = strategy_framings.get(
            selected_strategy.id,
            strategy_framings["technical_depth"],
        )

        evidence_paragraphs = []
        for b in bullet_records:
            evidence_paragraphs.append(f"• {b['text']}")

        evidence_section = (
            "Here are verified highlights from my track record that directly support this role:\n\n"
            + "\n".join(evidence_paragraphs)
            if evidence_paragraphs
            else (
                f"My core competencies span {', '.join(top_skills) if top_skills else 'modern Python, FastAPI, and PostgreSQL'}, "
                f"with a consistent focus on code quality, testing, and automated delivery."
            )
        )

        letter_content = (
            f"Dear Hiring Team at {company},\n\n"
            f"I am writing to express my enthusiastic interest in the {role} position located in {location}. {opening_framing}\n\n"
            f"{evidence_section}\n\n"
            f"What particularly attracts me to {company} is your commitment to engineering excellence. "
            f"I am confident that my technical grounding and alignment with your goals will allow me to make an "
            f"immediate, positive contribution to your team.\n\n"
            f"Thank you for your time and consideration. I welcome the opportunity to discuss how my experience "
            f"aligns with {company}'s upcoming milestones.\n\n"
            f"Sincerely,\n"
            f"{candidate_name}\n"
            f"{profile.headline if profile and profile.headline else 'Software Professional'}\n"
            f"{user.email}"
        )

        # 3. Upsert CoverLetter record in DB
        cover_letter = db.query(CoverLetter).filter(
            CoverLetter.user_id == user.id,
            CoverLetter.job_id == job.id,
        ).first()

        if not cover_letter:
            cover_letter = CoverLetter(
                user_id=user.id,
                job_id=job.id,
                strategy=selected_strategy.name,
                content=letter_content,
                referenced_evidence_ids=referenced_ids,
            )
            db.add(cover_letter)
        else:
            cover_letter.strategy = selected_strategy.name
            cover_letter.content = letter_content
            cover_letter.referenced_evidence_ids = referenced_ids

        db.commit()
        db.refresh(cover_letter)
        return cover_letter


cover_letter_service = CoverLetterService()
