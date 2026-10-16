"""Job Matching and Compatibility Assessment Service."""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.integrations.llm_ai_service import ai_service
from app.models.evidence import EvidenceItem, ExperienceRecord, Skill
from app.models.job import Job
from app.models.matching import JobAssessment, JobMatch, PreScreenResultRecord
from app.models.profile import CandidateProfile
from app.models.user import User
from app.protocols.ai_service import AIService, JobAssessmentResult, PreScreenResult


class MatchingService:
    """Orchestrates candidate-job compatibility assessment and match persistence."""

    def __init__(self, ai_gateway: Optional[AIService] = None):
        self.ai = ai_gateway or ai_service

    async def assess_candidate_job(
        self,
        db: Session,
        user: User,
        job: Job,
    ) -> JobMatch:
        """Perform AI compatibility assessment for a candidate against a job."""
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
        skills = db.query(Skill).filter(Skill.user_id == user.id).all()
        verified_bullets = (
            db.query(EvidenceItem)
            .filter(EvidenceItem.user_id == user.id, EvidenceItem.is_verified.is_(True))
            .all()
        )

        skill_names = [s.name for s in skills]
        bullet_texts = [b.raw_text for b in verified_bullets]

        candidate_summary = (
            f"Headline: {profile.headline if profile else 'Engineer'}\n"
            f"Summary: {profile.summary if profile else ''}\n"
            f"Skills: {', '.join(skill_names)}\n"
            f"Key Achievements: {' '.join(bullet_texts[:5])}"
        )

        job_details = {
            "id": str(job.id),
            "title": job.title,
            "company_name": job.company_name,
            "location": job.location,
            "remote": job.remote,
            "description": job.description,
            "tags": job.tags or [],
        }

        # 1. Prescreen job
        prescreen_res: PreScreenResult = await self.ai.prescreen_job(
            candidate_summary=candidate_summary,
            job_title=job.title,
            job_tags=job.tags or [],
        )

        # Upsert PreScreenResultRecord
        ps_record = db.query(PreScreenResultRecord).filter(
            PreScreenResultRecord.user_id == user.id,
            PreScreenResultRecord.job_id == job.id,
        ).first()
        if not ps_record:
            ps_record = PreScreenResultRecord(
                user_id=user.id,
                job_id=job.id,
                relevant=prescreen_res.relevant,
                confidence=prescreen_res.confidence,
                reason_codes=prescreen_res.reason_codes,
                reasoning=prescreen_res.reasoning,
            )
            db.add(ps_record)
        else:
            ps_record.relevant = prescreen_res.relevant
            ps_record.confidence = prescreen_res.confidence
            ps_record.reason_codes = prescreen_res.reason_codes
            ps_record.reasoning = prescreen_res.reasoning

        # 2. Deep Compatibility Assessment
        assessment_res: JobAssessmentResult = await self.ai.assess_job(
            candidate_profile_text=candidate_summary,
            job_details=job_details,
        )

        # 3. Upsert JobMatch
        match = db.query(JobMatch).filter(
            JobMatch.user_id == user.id,
            JobMatch.job_id == job.id,
        ).first()

        if not match:
            match = JobMatch(
                user_id=user.id,
                job_id=job.id,
                overall_score=assessment_res.overall_score,
                recommendation=assessment_res.recommendation,
                status="new",
            )
            db.add(match)
            db.flush()
        else:
            match.overall_score = assessment_res.overall_score
            match.recommendation = assessment_res.recommendation
            match.matched_at = func.now()

        # 4. Upsert JobAssessment
        assessment = db.query(JobAssessment).filter(
            JobAssessment.job_match_id == match.id,
        ).first()

        if not assessment:
            assessment = JobAssessment(
                job_match_id=match.id,
                skills_score=assessment_res.skills_score,
                experience_score=assessment_res.experience_score,
                seniority_score=assessment_res.seniority_score,
                location_score=assessment_res.location_score,
                language_score=assessment_res.language_score,
                confidence=assessment_res.confidence,
                strengths=assessment_res.strengths,
                missing_requirements=assessment_res.missing_requirements,
                matching_evidence_ids=assessment_res.matching_evidence_ids,
            )
            db.add(assessment)
        else:
            assessment.skills_score = assessment_res.skills_score
            assessment.experience_score = assessment_res.experience_score
            assessment.seniority_score = assessment_res.seniority_score
            assessment.location_score = assessment_res.location_score
            assessment.language_score = assessment_res.language_score
            assessment.confidence = assessment_res.confidence
            assessment.strengths = assessment_res.strengths
            assessment.missing_requirements = assessment_res.missing_requirements
            assessment.matching_evidence_ids = assessment_res.matching_evidence_ids

        db.commit()
        db.refresh(match)
        return match


matching_service = MatchingService()
